from __future__ import annotations

import json
import re

from cloudshell.cli.command_template.command_template_executor import (
    CommandTemplateExecutor,
)
from cloudshell.cli.service.cli_service import CliService
from cloudshell.layer_one.core.helper.logger import get_l1_logger

import arista_eos.command_templates.autoload as command_template
from arista_eos.arista_eos_exceptions import AristaEOSAutoloadException

logger = get_l1_logger(name=__name__)


def convert_output(raw_output: str) -> dict:
    """Clear raw output.

    There is not zero chance to get dirty output that can not be converted to JSON
    """
    match = re.search(r".*?(?P<output>{.*}).*", raw_output, re.DOTALL)
    if not match:
        logger.debug(f"Can not parse command output. Raw output: {raw_output}")
        raise AristaEOSAutoloadException("Can not parse command output.")
    try:
        res = json.loads(match.group("output"))
    except Exception as err:
        raise AristaEOSAutoloadException(
            f"Can not parse command output due to incorrect JSON format: {str(err)}"
        )

    return res


class AutoloadActions:
    """Autoload actions."""

    def __init__(self, cli_service: CliService):
        self._cli_service = cli_service

    def device_info(self) -> dict:
        """Get device info."""
        raw_output = CommandTemplateExecutor(
            self._cli_service, command_template.SHOW_DEVICE_INFO
        ).execute_command()

        return convert_output(raw_output=raw_output)

    def get_ports(self) -> dict[str, dict[str, str]]:
        """Get ports with details."""
        raw_output = CommandTemplateExecutor(
            self._cli_service, command_template.SHOW_PORTS
        ).execute_command()

        output = convert_output(raw_output=raw_output)
        logger.debug(f"Ports JSON output: {output}")

        res = {}
        interfaces = output.get("interfaces", {})
        for iface, if_data in interfaces.items():
            if "Management" in iface:
                continue

            match = re.search(r"\D+(?P<if_id>\d+.*)", iface)
            if not match:
                logger.debug(f"Can not parse Interface name. Iface: {iface}")

            if_id = match.group("if_id").replace("/", "-")

            res[if_id] = {
                "name": if_data.get("name"),
                "mac": if_data.get("physicalAddress"),
                "autoneg": if_data.get("autoNegotiate"),
                "duplex": if_data.get("duplex"),
                "speed": if_data.get("bandwidth"),
            }

        logger.debug(f"Existed ports: {res}")
        return res

    def get_connections(self) -> dict[str, list[str]]:
        """Get existed connections."""
        raw_output = CommandTemplateExecutor(
            self._cli_service, command_template.SHOW_CONNECTIONS
        ).execute_command()

        output = convert_output(raw_output=raw_output)
        logger.debug(f"Connections JSON output: {output}")

        res = {}
        patches = output.get("patches", {})
        for patch_name, data in patches.items():
            connectors = data.get("connectors", {})
            ifaces = []
            for _, conn_data in connectors.items():
                ifaces.append(conn_data.get("portConnectorInfo", {}).get("interface"))

            res[patch_name] = ifaces

        logger.debug(f"Existed connections: {res}")
        return res
