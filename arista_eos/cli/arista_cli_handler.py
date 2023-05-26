from __future__ import annotations

from cloudshell.cli.service.command_mode_helper import CommandModeHelper


from arista_eos.cli.l1_cli_handler import L1CliHandler
from arista_eos.cli.arista_command_modes import (
    AristaDefaultCommandMode,
    AristaEnableCommandMode,
    AristaConfigCommandMode
)
from arista_eos.cli.arista_ssh_session import AristaSSHSession
from arista_eos.cli.arista_telnet_session import AristaTelnetSession


class AristaCliHandler(L1CliHandler):
    def __init__(self):
        super().__init__()
        self.modes = CommandModeHelper.create_command_mode()
        self._defined_session_types = {
            "SSH": AristaSSHSession,
            "TELNET": AristaTelnetSession,
        }

    @property
    def default_mode(self):
        return self.modes[AristaDefaultCommandMode]

    @property
    def enable_mode(self):
        return self.modes[AristaEnableCommandMode]

    @property
    def config_mode(self):
        return self.modes[AristaConfigCommandMode]
