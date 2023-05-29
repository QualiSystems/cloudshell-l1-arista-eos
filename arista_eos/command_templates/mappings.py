from collections import OrderedDict

from cloudshell.cli.command_template.command_template import CommandTemplate

from arista_eos.command_templates.errors import GENERIC_ERRORS

ERROR_MAP = OrderedDict()
ERROR_MAP.update(GENERIC_ERRORS)

CREATE_PATCH_PANEL = CommandTemplate(command="patch {name}", error_map=ERROR_MAP)
DELETE_PATCH_PANEL = CommandTemplate(command="no patch {name}", error_map=ERROR_MAP)
CREATE_CONNECTOR = CommandTemplate(
    command="connector {id} interface {port_type} {port_id}", error_map=ERROR_MAP
)
