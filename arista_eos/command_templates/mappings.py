from cloudshell.cli.command_template.command_template import CommandTemplate


CONFIG_PATCH_PANEL = CommandTemplate("patch panel")
CREATE_PATCH_PANEL = CommandTemplate("patch {name}")
DELETE_PATCH_PANEL = CommandTemplate("no patch {name}")

CREATE_CONNECTOR = CommandTemplate("connector {id} interface {port_type} {port_id}")
