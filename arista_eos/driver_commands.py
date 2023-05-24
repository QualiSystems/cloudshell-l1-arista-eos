#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
from cloudshell.cli.cli import CLI
from cloudshell.layer_one.core.driver_commands_interface import DriverCommandsInterface
from cloudshell.layer_one.core.layer_one_driver_exception import LayerOneDriverException
from cloudshell.layer_one.core.response.resource_info.entities.chassis import Chassis
from cloudshell.layer_one.core.response.resource_info.entities.port import Port
from cloudshell.layer_one.core.response.response_info import GetStateIdResponseInfo, \
    ResourceDescriptionResponseInfo, AttributeValueResponseInfo

from cloudshell.networking.arista.cli.arista_cli_configurator import AristaCLIConfigurator


class AristaL1ResourceConfig:
    def __init__(self, address, user, password, runtime_config):
        self.address = address
        self.user = user
        self.password = password
        self.enable_password = "arista"
        self.sessions_concurrency_limit = 1
        self._runtime_config = runtime_config
        cli_connection_type = runtime_config.read_key("CLI.TYPE", True)
        cli_tcp_port = runtime_config.read_key("CLI.PORTS", True)
        if len(cli_connection_type) > 1:
            self.cli_connection_type = "Auto"
            self.cli_tcp_port = None
        else:
            self.cli_connection_type = cli_connection_type[0]
            self.cli_tcp_port = cli_tcp_port.get(self.cli_connection_type)


class DriverCommands(DriverCommandsInterface):
    """
    Driver commands implementation
    """

    MAP_CMD = "l1 source {dst}"
    REMOVE_MAP_CMD = MAP_CMD.format(dst="none")

    def __init__(self, logger, runtime_config):
        """
        :type logger: logging.Logger
        :type runtime_config: cloudshell.layer_one.core.helper.runtime_configuration.RuntimeConfiguration
        """
        self._logger = logger
        self._runtime_config = runtime_config
        self._resource_config = None
        self.cli = None
        self._switch_id = None
        self._cli = CLI()

    def login(self, address, username, password):
        """
        Perform login operation on the device
        :param address: resource address, "192.168.42.240"
        :param username: username to login on the device
        :param password: password
        :return: None
        :raises Exception: if command failed
        Example:
            # Define session attributes
            self._cli_handler.define_session_attributes(address, username, password)

            # Obtain cli session
            with self._cli_handler.default_mode_service() as session:
                # Executing simple command
                device_info = session.send_command('show version')
                self._logger.info(device_info)
        """
        self._resource_config = AristaL1ResourceConfig(address, username, password,
                                                      self._runtime_config)
        self.cli = AristaCLIConfigurator(resource_config=self._resource_config, logger=self._logger, api=None, cli=self._cli)
        with self.cli.enable_mode_service() as session:
            self._switch_id = self._get_serial_number(session)

    def get_state_id(self):
        """
        Check if CS synchronized with the device.
        :return: Synchronization ID, GetStateIdResponseInfo(-1) if not used
        :rtype: cloudshell.layer_one.core.response.response_info.GetStateIdResponseInfo
        :raises Exception: if command failed

        Example:
            # Obtain cli session
            with self._cli_handler.default_mode_service() as session:
                # Execute command
                chassis_name = session.send_command('show chassis name')
                return chassis_name
        """
        return GetStateIdResponseInfo(-1)

    def set_state_id(self, state_id):
        """
        Set synchronization state id to the device, called after Autoload or SyncFomDevice commands
        :param state_id: synchronization ID
        :type state_id: str
        :return: None
        :raises Exception: if command failed

        Example:
            # Obtain cli session
            with self._cli_handler.config_mode_service() as session:
                # Execute command
                session.send_command('set chassis name {}'.format(state_id))
        """
        pass

    def map_bidi(self, src_port, dst_port):
        """
        Create a bidirectional connection between source and destination ports
        :param src_port: src port address, '192.168.42.240/1/21'
        :type src_port: str
        :param dst_port: dst port address, '192.168.42.240/1/22'
        :type dst_port: str
        :return: None
        :raises Exception: if command failed

        Example:
            with self._cli_handler.config_mode_service() as session:
                session.send_command('map bidir {0} {1}'.format(convert_port(src_port), convert_port(src_port)))

        """
        with self.cli.config_mode_service() as session:
            src = self._convert_port_address(src_port)
            dst = self._convert_port_address(dst_port)
            self._map_uni(src, dst)
            self._map_uni(dst, src)

    def map_uni(self, src_port, dst_ports):
        """
        Unidirectional mapping of two ports
        :param src_port: src port address, '192.168.42.240/1/21'
        :type src_port: str
        :param dst_ports: list of dst ports addresses, ['192.168.42.240/1/22', '192.168.42.240/1/23']
        :type dst_ports: list
        :return: None
        :raises Exception: if command failed

        Example:
            with self._cli_handler.config_mode_service() as session:
                for dst_port in dst_ports:
                    session.send_command('map {0} also-to {1}'.format(convert_port(src_port), convert_port(dst_port)))
        """
        with self.cli.config_mode_service() as session:
            for dst_port in dst_ports:
                src = self._convert_port_address(src_port)
                dst = self._convert_port_address(dst_port)
                self._map_uni(src, dst)
                # src = self._convert_port_address(src_port)
                # dst = self._convert_port_address(dst_port)
                # self._enable_port(session, src)
                # self._enable_port(session, dst)
                # result = session.send_command("tap {src} {dst}".format(
                #     src=src,
                #     dst=dst))
                # if not re.search("Added input tap", result, re.IGNORECASE):
                #     raise LayerOneDriverException(
                #         "Failed to create mapping between {src} {dst}".format(
                #             src=src,
                #             dst=dst))

    def _map_uni(self, src_port, dst_port):
        """
        Unidirectional mapping of two ports
        :param src_port: src port address, 
        :type src_port: str
        :param dst_port: dst port address,
        :type dst_port: str
        :return: None
        :raises Exception: if command failed
        """
        with self.cli.config_mode_service() as session:
            self._enable_port(session, dst_port)
            self._enable_port(session, src_port)
            result = session.send_command("l1 source {dst}".format(dst=dst_port))
            if not re.search("patch created", result, re.IGNORECASE):
                raise LayerOneDriverException(
                    "Failed to create mapping between {src} {dst}".format(
                        src=src_port,
                        dst=dst_port))

    def get_resource_description(self, address):
        """
        Auto-load function to retrieve all information from the device
        :param address: resource address, '192.168.42.240'
        :type address: str
        :return: resource description
        :rtype: cloudshell.layer_one.core.response.response_info.ResourceDescriptionResponseInfo
        :raises cloudshell.layer_one.core.layer_one_driver_exception.LayerOneDriverException: Layer one exception.
        """
        port_dict = {}
        Port.NAME_TEMPLATE = "{}"
        with self.cli.config_mode_service() as session:
            model = "Arista L1 EOS Chassis"
            serial = self._get_serial_number(session)
            model_name = self._get_model_name(session)
            os_version = self._get_os_version(session)
            chassis = Chassis(0, address, model, serial)
            chassis.set_serial_number(serial)
            chassis.set_model_name(model_name)
            chassis.set_os_version(os_version)
            ports_out = session.send_command("show interface status")
            port_match = re.findall(r"(?P<iface>et.+?)\s+"
                                    r"(?P<status>\w+)\s+"
                                    r"(?P<vlan>.+?)\s+"
                                    r"(?P<duplex>.+?)\s+"
                                    r"(?P<speed>\d+)",
                                    ports_out,
                                    re.IGNORECASE
                                    )
            for port_name, _, _, duplex, speed in port_match:
                port_name = re.sub(r"et(hernet)*", "ethernet", port_name, flags=(
                    re.IGNORECASE))
                port = Port(port_name.replace("/", "-"), 'Generic L1 Port')
                port.set_port_speed(speed)
                port.set_duplex(duplex)
                port.set_parent_resource(chassis)
                port_dict[port_name] = port
            bidi_mappings = self._get_mappings(session)
            for src, dst in bidi_mappings.items():
                src_port = port_dict.get(src)
                dst_port = port_dict.get(dst)
                if src_port and dst_port:
                    src_port.add_mapping(dst_port)
                    dst_port.add_mapping(src_port)
            # tap_mappings = self._get_tap_mappings(session)
            # for src, dst in tap_mappings.items():
            #     src_port = port_dict.get(src)
            #     dst_port = port_dict.get(dst)
            #     if src_port and dst_port:
            #         src_port.add_mapping(dst_port)

        return ResourceDescriptionResponseInfo([chassis])

    def _enable_port(self, session, port):
        session.send_command("interface {}".format(port),
                             remove_prompt=True)
        session.send_command("no shutdown",
                             remove_prompt=True)

    def _disable_port(self, session, port):
        session.send_command("interface {}".format(port),
                             remove_prompt=True)
        session.send_command("shutdown",
                             remove_prompt=True)

    def _get_serial_number(self, session):
        serial_number = session.send_command("show version | grep Serial",
                                             remove_prompt=True)
        result = re.sub("serial\s+number\s+|\n$", "", serial_number, flags=(
            re.IGNORECASE))
        return str(result)

    def _get_model_name(self, session):
        result = session.send_command("show version | head -1",
                                      remove_prompt=True)
        return str(result).strip(" \r\t\n")

    def _get_os_version(self, session):
        os_version = session.send_command("show version | grep 'System version'",
                                          remove_prompt=True)
        result = re.sub("system\s+version\s+|\n$", "", os_version, flags=(
            re.IGNORECASE))
        return str(result)

    def _get_mappings(self, session):
        mappings = session.send_command("show l1 path")
        return dict(re.findall(r"(?P<src>et.+)\s+(?P<dst>et.+)\s+",
                               mappings,
                               re.IGNORECASE))

    # def _get_tap_mappings(self, session):
    #     mappings = session.send_command("show config running-config tap")
    #     return {dst: src for src, dst in re.findall(r"(?P<src>et.+)\s+(?P<dst>et.+)",
    #                                                 mappings,
    #                                                 re.IGNORECASE)}

    def map_clear(self, ports):
        """
        Remove simplex/multi-cast/duplex connection ending on the destination port
        :param ports: ports, ['192.168.42.240/1/21', '192.168.42.240/1/22']
        :type ports: list
        :return: None
        :raises Exception: if command failed

        Example:
            exceptions = []
            with self._cli_handler.config_mode_service() as session:
                for port in ports:
                    try:
                        session.send_command('map clear {}'.format(convert_port(port)))
                    except Exception as e:
                        exceptions.append(str(e))
                if exceptions:
                    raise Exception('self.__class__.__name__', ','.join(exceptions))
        """
        for port in ports:
            with self.cli.config_mode_service() as session:
                src_port = self._convert_port_address(port)
                dst_port = self._get_bidi_mappings(session).get("src_port")
                self._remove_bidi_mapping(session, src_port, dst_port)
                self._remove_bidi_mapping(session, dst_port, src_port)
                self._disable_port(session, src_port)
                self._disable_port(session, dst_port)
                dst_port = self._get_tap_mappings(session).get("src_port")
                self._disable_port(session, dst_port)

    def map_clear_to(self, src_port, dst_ports):
        """
        Remove simplex/multi-cast/duplex connection ending on the destination port
        :param src_port: src port address, '192.168.42.240/1/21'
        :type src_port: str
        :param dst_ports: list of dst ports addresses, ['192.168.42.240/1/21',
                                                        '192.168.42.240/1/22']
        :type dst_ports: list
        :return: None
        :raises Exception: if command failed
        """
        with self.cli.config_mode_service() as session:
            for dst_port in dst_ports:
                src = self._convert_port_address(src_port)
                dst = self._convert_port_address(dst_port)
                self._remove_bidi_mapping(session, src, dst)
                self._remove_bidi_mapping(session, dst, src)
                self._disable_port(session, src)
                self._disable_port(session, dst)

    def _remove_bidi_mapping(self, session, src_port, dst_port):
        self._remove_map_uni(session, src_port)
        self._remove_map_uni(session, dst_port)

    def _remove_map_uni(self, session, src_port):
        self._disable_port(session, src_port)
        session.send_command(self.REMOVE_MAP_CMD)

    def get_attribute_value(self, cs_address, attribute_name):
        """
        Retrieve attribute value from the device
        :param cs_address: address, '192.168.42.240/1/21'
        :type cs_address: str
        :param attribute_name: attribute name, "Port Speed"
        :type attribute_name: str
        :return: attribute value
        :rtype: cloudshell.layer_one.core.response.response_info.AttributeValueResponseInfo
        :raises Exception: if command failed
        """
        if attribute_name == "Serial Number":
            if len(cs_address.split("/")) == 1:
                return AttributeValueResponseInfo(self._switch_id)
            else:
                return AttributeValueResponseInfo("NA")
        else:
            raise LayerOneDriverException("GetAttributeValue command is not supported")

    def set_attribute_value(self, cs_address, attribute_name, attribute_value):
        """
        Set attribute value to the device
        :param cs_address: address, '192.168.42.240/1/21'
        :type cs_address: str
        :param attribute_name: attribute name, "Port Speed"
        :type attribute_name: str
        :param attribute_value: value, "10000"
        :type attribute_value: str
        :return: attribute value
        :rtype: cloudshell.layer_one.core.response.response_info.AttributeValueResponseInfo
        :raises Exception: if command failed
        """
        raise NotImplementedError

    def map_tap(self, src_port, dst_ports):
        """
        Add TAP connection
        :param src_port: port to monitor '192.168.42.240/1/21'
        :type src_port: str
        :param dst_ports: ['192.168.42.240/1/22', '192.168.42.240/1/23']
        :type dst_ports: list
        :return: None
        :raises Exception: if command failed

        Example:
            return self.map_uni(src_port, dst_ports)
        """
        self.map_uni(src_port, dst_ports)

    def set_speed_manual(self, src_port, dst_port, speed, duplex):
        """
        Set connection speed. It is not used with new standard
        :param src_port:
        :param dst_port:
        :param speed:
        :param duplex:
        :return:
        """
        raise NotImplementedError

    @staticmethod
    def _convert_port_address(port):
        """
        :param port:
        :type port: str
        :return:
        """
        return port.split("/")[-1].replace("-", "/")


if __name__ == "__main__":
    import logging
    from cloudshell.logging.qs_logger import get_qs_logger
    from unittest.mock import Mock
    ip = "192.168.105.28"
    _logger = get_qs_logger()
    _runtime_config_instance = Mock()
    _runtime_config_instance.read_key.side_effect = [["SSH", "TELNET"], {"SSH": 22,
                                                                         "TELNET": 23}]
    driver = DriverCommands(_logger, _runtime_config_instance)
    driver.login(ip, "admin", "admin")
    response = driver.get_resource_description(ip)
    # result = driver.map_clear_to('192.168.23.10/ethernet30-3',
    #                              ['192.168.23.10/ethernet31-3'])
    response = driver.map_bidi(f'{ip}/ethernet3',
                               f'{ip}/ethernet4')
    result1 = driver.map_clear_to(f'{ip}/ethernet3',
                                  [f'{ip}/ethernet4'])
    # result2 = driver.map_clear_to('192.168.23.10/ethernet30-1',
    #                               ['192.168.23.10/ethernet31-1',
    #                                '192.168.23.10/ethernet31-2'])
    # response1 = driver.map_uni('192.168.23.10/ethernet30-1',
    #                            ['192.168.23.10/ethernet31-1',
    #                             '192.168.23.10/ethernet31-2'])
    # result3 = driver.map_clear_to('192.168.23.10/ethernet30-1',
    #                               ['192.168.23.10/ethernet31-1',
    #                                '192.168.23.10/ethernet31-2']
    #                               )
    print("!")
