from __future__ import annotations

import re
import time

from cloudshell.cli.service.command_mode import CommandMode

#ToDo
ENABLE_PASSWORD = "arista"


class AristaDefaultCommandMode(CommandMode):
    PROMPT = r">\s*$"
    ENTER_COMMAND = ""
    EXIT_COMMAND = ""

    def __init__(self):
        """Initialize Default command mode."""
        CommandMode.__init__(
            self,
            AristaDefaultCommandMode.PROMPT,
            AristaDefaultCommandMode.ENTER_COMMAND,
            AristaDefaultCommandMode.EXIT_COMMAND,
        )


class AristaEnableCommandMode(CommandMode):
    PROMPT = (
        r"((?<=\n)|(?<=\r)|(?<=^))"  # new line or begin of the line that don't match
        r"((?!\(config.*?\))(\w|\.|-|:|\(|\)))*"  # any \w,.,-,(), without (config)
        r"#\s*$"
    )
    # PROMPT = "Arista.vEOS#"
    ENTER_COMMAND = "enable"
    EXIT_COMMAND = ""

    def __init__(self):
        """Initialize Enable command mode - default command mode for Arista Shells."""
        CommandMode.__init__(
            self,
            AristaEnableCommandMode.PROMPT,
            AristaEnableCommandMode.ENTER_COMMAND,
            AristaEnableCommandMode.EXIT_COMMAND,
            enter_action_map=self.enter_action_map(),
        )

    def enter_action_map(self):
        return {
            "[Pp]assword": lambda session, logger: session.send_line(
                ENABLE_PASSWORD, logger
            )
        }


class AristaConfigCommandMode(CommandMode):
    MAX_ENTER_CONFIG_MODE_RETRIES = 5
    ENTER_CONFIG_RETRY_TIMEOUT = 5
    PROMPT = r"\(config.*\)#\s*$"
    ENTER_COMMAND = "configure terminal"
    EXIT_COMMAND = "end"

    def __init__(self):
        """Initialize Config command mode."""
        CommandMode.__init__(
            self,
            AristaConfigCommandMode.PROMPT,
            AristaConfigCommandMode.ENTER_COMMAND,
            AristaConfigCommandMode.EXIT_COMMAND,
            enter_action_map=self.enter_action_map(),
        )

    def enter_action_map(self):
        return {rf"{AristaEnableCommandMode.PROMPT}.*$": self._check_config_mode}

    def _check_config_mode(self, session, logger):
        error_message = "Failed to enter config mode, please check logs, for details"
        conf_prompt = AristaConfigCommandMode.PROMPT
        enable_prompt = AristaEnableCommandMode.PROMPT

        retry = 0
        output = session.hardware_expect("", f"{conf_prompt}|{enable_prompt}", logger)
        while (
            not re.search(conf_prompt, output)
            and retry < self.MAX_ENTER_CONFIG_MODE_RETRIES
        ):
            time.sleep(self.ENTER_CONFIG_RETRY_TIMEOUT)
            output = session.hardware_expect(
                AristaConfigCommandMode.ENTER_COMMAND,
                f"{enable_prompt}|{conf_prompt}",
                logger,
            )
            retry += 1

        if not re.search(conf_prompt, output):
            raise Exception(error_message)

        session.send_line("", logger)


CommandMode.RELATIONS_DICT = {
    AristaDefaultCommandMode: {AristaEnableCommandMode: {AristaConfigCommandMode: {}}}
}
