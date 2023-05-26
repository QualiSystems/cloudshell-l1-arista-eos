from cloudshell.layer_one.core.response.resource_info.entities.attributes import (
    NumericAttribute,
)
from cloudshell.layer_one.core.response.resource_info.entities.port import Port


class AristaPort(Port):
    MODEL_NAME = "Arista EOS Generic L1 Port"

    def set_protocol(self, value):
        if value is not None:
            self.attributes.append(NumericAttribute("Protocol", value))

    def set_protocol_type(self, value):
        if value is not None:
            self.attributes.append(NumericAttribute("Protocol Type", value))

    def set_speed(self, value):
        if value is not None:
            self.attributes.append(NumericAttribute("Speed", value))
