from __future__ import annotations

import re

from cloudshell.layer_one.core.driver_commands_interface import DriverCommandsInterface
from cloudshell.layer_one.core.helper.logger import get_l1_logger
from cloudshell.layer_one.core.helper.runtime_configuration import RuntimeConfiguration
from cloudshell.layer_one.core.response.response_info import (
    AttributeValueResponseInfo,
    GetStateIdResponseInfo,
    ResourceDescriptionResponseInfo,
)

from arista_eos.arista_eos_exceptions import (
    AristaEOSMappingException,
    AristaEOSWrongParams,
)
from arista_eos.cli.arista_cli_handler import AristaCliHandler
from arista_eos.command_actions.autoload_actions import AutoloadActions
from arista_eos.command_actions.mapping_actions import MappingActions
from arista_eos.model.arista_chassis import AristaChassis
from arista_eos.model.arista_port import AristaPort

logger = get_l1_logger(name=__name__)


class DriverCommands(DriverCommandsInterface):
    """Driver commands implementation."""

    CHASSIS_ID = 1

    def __init__(self, runtime_config: RuntimeConfiguration):
        self._runtime_config = runtime_config
        self._cli_handler = AristaCliHandler(runtime_config)
        self.__device_info = None

    def _device_info(self, session):
        if not self.__device_info:
            autoload_actions = AutoloadActions(session)
            self.__device_info = autoload_actions.device_info()
        return self.__device_info

    def login(self, address: str, username: str, password: str):
        """Perform login operation on the device.

        Example:
            # Define session attributes
            self._cli_handler.define_session_attributes(address, username, password)

            # Obtain cli session
            with self._cli_handler.default_mode_service() as session:
                # Executing simple command
                device_info = session.send_command("show version")
                logger.info(device_info)
        """
        address_data = re.search(
            r"(?P<host>[^:]*)" r":?(?P<port>[0-9]*?)",
            address,
            re.IGNORECASE,
        )

        if not address_data:
            raise AristaEOSWrongParams(
                "Make sure that address is in correct format: host[:port]"
            )
        host = address_data.group("host")
        port = address_data.group("port")
        try:
            port = int(port)
        except Exception:  # noqa: E722
            port = None

        self._cli_handler.define_session_attributes(host, username, password, port)
        with self._cli_handler.get_cli_service(
            self._cli_handler.enable_mode
        ) as enable_session:
            device_info = self._device_info(enable_session)
            if not device_info:
                logger.error(f"DeviceInfo: {device_info}")
                raise
            logger.debug(
                f"Model Name: {device_info.get('modelName')}, "
                f"SerialNumber: {device_info.get('serialNumber')}, "
                f"Version: {device_info.get('version')}"
            )

    def get_resource_description(self, address: str) -> ResourceDescriptionResponseInfo:
        """Autoload function to retrieve all information from the device."""
        with self._cli_handler.get_cli_service(
            self._cli_handler.enable_mode
        ) as enable_session:
            device_info = self._device_info(enable_session)

            chassis = AristaChassis(1, address)
            chassis.set_model_name(device_info.get("modelName"))
            chassis.set_os_version(device_info.get("version"))
            chassis.set_serial_number(device_info.get("serialNumber"))

            autoload_actions = AutoloadActions(enable_session)
            ports_info = autoload_actions.get_ports()
            ports = {}
            for port_id, port_data in ports_info.items():
                port = AristaPort(resource_id=port_id)
                port.set_port_speed(str(port_data.get("speed")))
                port.set_auto_negotiation(port_data.get("autoneg"))
                port.set_duplex(port_data.get("duplex"))
                port.set_parent_resource(chassis)
                ports[port_data.get("name")] = port

            connections_info = autoload_actions.get_connections()
            for _, ifaces in connections_info.items():
                if ifaces and len(ifaces) > 1:
                    src_port = ports.get(ifaces[0])
                    dst_port = ports.get(ifaces[1])
                    if src_port and dst_port:
                        src_port.add_mapping(dst_port)
                        dst_port.add_mapping(src_port)

        return ResourceDescriptionResponseInfo([chassis])

    def map_uni(self, src_port: str, dst_ports: list[str]):
        """Unidirectional mapping of two ports."""
        msg = "Unidirectional connections are not supported."
        logger.debug(
            f"{msg}."
            f"Provided data: source port - {src_port}, destination ports - {dst_ports}"
        )
        raise AristaEOSMappingException(msg)

    def map_bidi(self, src_port: str, dst_port: str):
        """Create a bidirectional connection between source and destination ports."""
        logger.debug(
            f"Try to create bi-directional connection:"
            f"SRC - {src_port}, DST - {dst_port}"
        )
        src_port = src_port.replace("-", "/")
        dst_port = dst_port.replace("-", "/")

        with self._cli_handler.get_cli_service(
            self._cli_handler.config_patch_mode
        ) as patch_session:

            mapping_actions = MappingActions(patch_session)
            mapping_actions.create_mapping(
                src_port=self._convert_port_address(src_port),
                dst_port=self._convert_port_address(dst_port),
            )

    def map_tap(self, src_port: str, dst_ports: list[str]):
        """Add TAP connection.

        Example:
            return self.map_uni(
                        "192.168.42.240/1/21",
                        ["192.168.42.240/1/22", "192.168.42.240/1/23"]
                        )
        """
        with self._cli_handler.get_cli_service(
            self._cli_handler.config_patch_mode
        ) as patch_session:

            mapping_actions = MappingActions(patch_session)
            src_port = src_port.replace("-", "/")
            for dst_port in dst_ports:
                dst_port = dst_port.replace("-", "/")
                logger.debug(
                    f"Try to create TAP-connection:"
                    f"SRC - {src_port}, DST - {dst_port}"
                )
                mapping_actions.create_mapping(
                    src_port=self._convert_port_address(src_port),
                    dst_port=self._convert_port_address(dst_port),
                    is_tap=True,
                )

    def map_clear_to(self, src_port: str, dst_ports: list[str]):
        """Remove simplex/multicast/duplex connection ending on the dst port."""
        logger.debug(
            f"Try to remove connections:" f"SRC - {src_port}, DST ports - {dst_ports}"
        )
        dst_ports.append(src_port)
        self.map_clear(dst_ports)

    def map_clear(self, ports: list[str]):
        """Remove simplex/multicast/duplex connection ending on the destination port.

        ports - ["192.168.42.240/1/21", "192.168.42.240/1/22"]
        """
        logger.debug(f"Try to remove connections for ports: {ports}")

        with self._cli_handler.get_cli_service(
            self._cli_handler.enable_mode
        ) as enable_session:
            autoload_actions = AutoloadActions(enable_session)
            connections_info = autoload_actions.get_connections()

        if connections_info:  # Check if any connection exists
            full_patch_names = set()
            for port in ports:
                port = self._convert_port_address(port).replace("-", "/")
                patch_names = self._get_patch_name(
                    port=port, connections_info=connections_info
                )
                full_patch_names.update(patch_names)

            if full_patch_names:  # Check if connections for provided ports exists
                with self._cli_handler.get_cli_service(
                    self._cli_handler.config_patch_mode
                ) as patch_session:
                    mapping_actions = MappingActions(patch_session)
                    mapping_actions.remove_mapping(full_patch_names)

    def get_state_id(self) -> GetStateIdResponseInfo:
        """Check if CS synchronized with the device."""
        return GetStateIdResponseInfo(-1)

    def set_state_id(self, state_id: str):
        """Set synchronization state id to the device."""
        pass

    def get_attribute_value(
        self, cs_address: str, attribute_name: str
    ) -> AttributeValueResponseInfo:
        """Retrieve attribute value from the device.

        Example:
            with self._cli_handler.config_mode_service() as session:
                command = AttributeCommandFactory.get_attribute_command(
                                                                    cs_address,
                                                                    attribute_name
                                                                    )
                value = session.send_command(command)
                return AttributeValueResponseInfo(value)
        """
        pass

    def set_attribute_value(
        self, cs_address: str, attribute_name: str, attribute_value: str
    ) -> AttributeValueResponseInfo:
        """Set attribute value to the device.

        Example:
            with self._cli_handler.config_mode_service() as session:
                command = AttributeCommandFactory.set_attribute_command(
                                                                    cs_address,
                                                                    attribute_name,
                                                                    attribute_value
                                                                    )
                session.send_command(command)
                return AttributeValueResponseInfo(attribute_value)
        """
        pass

    def set_speed_manual(self, src_port: str, dst_port: str, speed, duplex):
        """Set connection speed."""
        raise NotImplementedError

    def _convert_port_address(self, port: str) -> str:
        """Convert full port address to port id.

        192.168.105.29/4 -> 4
        192.168.105.29/2-4 -> 2-4
        192.168.105.29/2/4 -> 2/4
        """
        return port.split("/", 1)[-1]

    def _get_patch_name(
        self, port: str, connections_info: dict[str, list[str]] = None
    ) -> set[str]:
        """Get all patch names for provided port."""
        patch_names = set()
        port = f"{MappingActions.INTERFACE_TYPE}{port.replace('-', '/')}"
        if not connections_info:
            with self._cli_handler.get_cli_service(
                self._cli_handler.enable_mode
            ) as enable_session:
                autoload_actions = AutoloadActions(enable_session)
                connections_info = autoload_actions.get_connections()

        for patch_name, conn in connections_info.items():
            if port in conn:
                patch_names.add(patch_name)

        return patch_names
