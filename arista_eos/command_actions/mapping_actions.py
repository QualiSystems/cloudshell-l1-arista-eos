from __future__ import annotations

from cloudshell.cli.command_template.command_template_executor import (
    CommandTemplateExecutor,
)
from cloudshell.cli.service.cli_service import CliService
from cloudshell.layer_one.core.helper.logger import get_l1_logger

import arista_eos.command_templates.mappings as command_template

logger = get_l1_logger(name=__name__)


class MappingActions:
    """Mapping actions."""

    BIDI_TEMPLATE = "QualiBIDI_{src}_TO_{dst}"
    TAP_TEMPLATE = "QualiTAP_{src}_TO_{dst}"
    INTERFACE_TYPE = "Ethernet"

    def __init__(self, cli_service: CliService):
        self._cli_service = cli_service

    def create_mapping(self, src_port: str, dst_port: str, is_tap: bool = False):
        """Create patch panel for Source and Destination Ports."""
        src_port_dash = src_port.replace("/", "-")
        dst_port_dash = dst_port.replace("/", "-")
        if is_tap:
            patch_name = self.TAP_TEMPLATE.format(src=src_port_dash, dst=dst_port_dash)
            logger.debug("Try to create TAP Connection.")
        else:
            patch_name = self.BIDI_TEMPLATE.format(src=src_port_dash, dst=dst_port_dash)

        logger.debug(
            f"Try to create connection between ports: "
            f"SRC - {src_port}, DST - {dst_port}"
        )
        CommandTemplateExecutor(
            self._cli_service, command_template.CREATE_PATCH_PANEL
        ).execute_command(name=patch_name)

        CommandTemplateExecutor(
            self._cli_service, command_template.CREATE_CONNECTOR
        ).execute_command(id=1, port_type=self.INTERFACE_TYPE, port_id=src_port)

        CommandTemplateExecutor(
            self._cli_service, command_template.CREATE_CONNECTOR
        ).execute_command(id=2, port_type=self.INTERFACE_TYPE, port_id=dst_port)

    def remove_mapping(self, patch_names: set[str]):
        """Remove patches panel."""
        logger.debug(f"Try to remove patches: {patch_names}")
        for patch_name in patch_names:
            CommandTemplateExecutor(
                self._cli_service, command_template.DELETE_PATCH_PANEL
            ).execute_command(name=patch_name)
