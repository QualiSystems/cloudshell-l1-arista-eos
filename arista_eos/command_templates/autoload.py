from collections import OrderedDict

from cloudshell.cli.command_template.command_template import CommandTemplate

from arista_eos.command_templates.errors import GENERIC_ERRORS

ERROR_MAP = OrderedDict()

ERROR_MAP.update(GENERIC_ERRORS)

SHOW_DEVICE_INFO = CommandTemplate(command="show version | json", error_map=ERROR_MAP)
SHOW_PORTS = CommandTemplate(command="show interfaces | json", error_map=ERROR_MAP)
SHOW_CONNECTIONS = CommandTemplate(
    command="show patch panel | json", error_map=ERROR_MAP
)
SHOW_VERSION_JSON = CommandTemplate(command="show version | json", error_map=ERROR_MAP)
SHOW_VERSION = CommandTemplate(command="show version", error_map=ERROR_MAP)
