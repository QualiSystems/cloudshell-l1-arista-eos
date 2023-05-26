from __future__ import annotations

from collections import OrderedDict

from cloudshell.cli.session.telnet_session import TelnetSession

from arista_eos.cli.arista_command_modes import AristaDefaultCommandMode


class AristaTelnetSession(TelnetSession):
    def _connect_actions(self, prompt, logger):
        command = f"logon {self.username} {self.password}"
        error_map = OrderedDict(
            [
                ("[Aa]ccess [Dd]enied", "Invalid username/password for login"),
            ]
        )
        error_map.update(GENERIC_ERRORS)
        action_map = OrderedDict()
        action_map["Accept/Decline"] = lambda session, logger: session.send_line(
            "A", logger
        )

        prompt = AristaDefaultCommandMode.PROMPT

        self.hardware_expect(
            "",
            expected_string=prompt,
            timeout=self._timeout,
            logger=logger,
            action_map=action_map,
            error_map=error_map,
        )

        self.hardware_expect(
            command,
            expected_string=prompt,
            timeout=self._timeout,
            logger=logger,
            action_map=action_map,
            error_map=error_map,
        )
        self._on_session_start(logger)
