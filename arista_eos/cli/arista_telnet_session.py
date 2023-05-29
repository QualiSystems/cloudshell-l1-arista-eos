from __future__ import annotations

from cloudshell.cli.session.telnet_session import TelnetSession

from arista_eos.cli.arista_command_modes import AristaDefaultCommandMode


class AristaTelnetSession(TelnetSession):
    def _connect_actions(self, prompt, logger):
        command = f"logon {self.username} {self.password}"

        prompt = AristaDefaultCommandMode.PROMPT

        self.hardware_expect(
            "",
            expected_string=prompt,
            timeout=self._timeout,
            logger=logger,
        )

        self.hardware_expect(
            command,
            expected_string=prompt,
            timeout=self._timeout,
            logger=logger,
        )
        self._on_session_start(logger)
