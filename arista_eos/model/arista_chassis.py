from cloudshell.layer_one.core.response.resource_info.entities.attributes import (
    StringAttribute,
)
from cloudshell.layer_one.core.response.resource_info.entities.chassis import Chassis


class AristaChassis(Chassis):
    MODEL_NAME = "Arista EOS Chassis"

    def __init__(self, resource_id, address):
        super().__init__(resource_id, address, self.MODEL_NAME)

    def set_ip_address(self, value):
        if value:
            self.attributes.append(StringAttribute("IP Address", value))
