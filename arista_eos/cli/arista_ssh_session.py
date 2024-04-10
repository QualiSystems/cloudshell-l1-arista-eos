from cloudshell.cli.service.cli_service_impl import CliServiceImpl
from cloudshell.cli.service.command_mode_helper import CommandModeHelper
from cloudshell.cli.session.ssh_session import SSHSession

from arista_eos.cli.arista_command_modes import (
    AristaConfigCommandMode,
    AristaEnableCommandMode,
)


class AristaSSHSession(SSHSession):
    def _connect_actions(self, prompt, logger):
        self.hardware_expect(
            None,
            expected_string=prompt,
            timeout=self._timeout,
            logger=logger,
        )
        self._on_session_start(logger)

    def _on_session_start(self, logger) -> None:
        """Send default commands to configure/clear session outputs."""
        modes = CommandModeHelper.create_command_mode()
        cli_service = CliServiceImpl(self, modes[AristaEnableCommandMode], logger)
        cli_service.send_command("terminal length 0", AristaEnableCommandMode.PROMPT)
        cli_service.send_command("terminal width 300", AristaEnableCommandMode.PROMPT)
        with cli_service.enter_mode(modes[AristaConfigCommandMode]) as config_session:
            config_session.send_command(
                "no logging console", AristaConfigCommandMode.PROMPT
            )
