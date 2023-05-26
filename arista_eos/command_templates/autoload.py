from cloudshell.cli.command_template.command_template import CommandTemplate


SHOW_DEVICE_INFO = CommandTemplate("show version | json")
"""
{
    "mfgName": "Arista",
    "modelName": "vEOS-lab",
    "hardwareRevision": "",
    "serialNumber": "EBB5276DCA926A75122C12571552E485",
    "systemMacAddress": "00:50:56:3b:3a:61",
    "hwMacAddress": "00:00:00:00:00:00",
    "configMacAddress": "00:00:00:00:00:00",
    "version": "4.29.0.2F",
    "architecture": "x86_64",
    "internalVersion": "4.29.0.2F-29226602.42902F",
    "internalBuildId": "b32bd8f9-3baf-4332-8f58-45e1afe2f695",
    "imageFormatVersion": "1.0",
    "imageOptimization": "None",
    "bootupTimestamp": 1683551217.840197,
    "uptime": 1448899.52,
    "memTotal": 3999948,
    "memFree": 2386088,
    "isIntlVersion": false
}
"""
SHOW_PORTS = CommandTemplate("show interfaces | json")
"""
{
    "interfaces": {
        "Management1": {
            "name": "Management1",
            "forwardingModel": "routed",
            "lineProtocolStatus": "up",
            "interfaceStatus": "connected",
            "hardware": "ethernet",
            "interfaceAddress": [
                {
                    "primaryIp": {
                        "address": "192.168.105.29",
                        "maskLen": 24
                    },
                    "secondaryIps": {},
                    "secondaryIpsOrderedList": [],
                    "virtualIp": {
                        "address": "0.0.0.0",
                        "maskLen": 0
                    },
                    "virtualSecondaryIps": {},
                    "virtualSecondaryIpsOrderedList": [],
                    "broadcastAddress": "255.255.255.255",
                    "dhcp": true
                }
            ],
            "physicalAddress": "00:50:56:89:00:e1",
            "burnedInAddress": "00:50:56:89:00:e1",
            "description": "",
            "bandwidth": 1000000000,
            "mtu": 1500,
            "l3MtuConfigured": false,
            "l2Mru": 0,
            "lastStatusChangeTimestamp": 1683551357.7520134,
            "interfaceStatistics": {
                "updateInterval": 300.0,
                "inBitsRate": 9410.512522620218,
                "inPktsRate": 6.162673119482194,
                "outBitsRate": 512.5704316369284,
                "outPktsRate": 0.3867115720329665
            },
            "interfaceCounters": {
                "inOctets": 8606746966,
                "inUcastPkts": 14548705,
                "inMulticastPkts": 0,
                "inBroadcastPkts": 0,
                "inDiscards": 0,
                "inTotalPkts": 14548705,
                "outOctets": 11895622,
                "outUcastPkts": 61612,
                "outMulticastPkts": 0,
                "outBroadcastPkts": 0,
                "outDiscards": 0,
                "outTotalPkts": 61612,
                "linkStatusChanges": 4,
                "totalInErrors": 0,
                "inputErrorsDetail": {
                    "runtFrames": 0,
                    "giantFrames": 0,
                    "fcsErrors": 0,
                    "alignmentErrors": 0,
                    "symbolErrors": 0,
                    "rxPause": 0
                },
                "totalOutErrors": 0,
                "outputErrorsDetail": {
                    "collisions": 0,
                    "lateCollisions": 0,
                    "deferredTransmissions": 0,
                    "txPause": 0
                },
                "counterRefreshTime": 1685000182.258323
            },
            "duplex": "duplexFull",
            "autoNegotiate": "success",
            "loopbackMode": "loopbackNone",
            "lanes": 0
        },
        "Ethernet7": {
            "name": "Ethernet7",
            "forwardingModel": "bridged",
            "lineProtocolStatus": "up",
            "interfaceStatus": "connected",
            "hardware": "ethernet",
            "interfaceAddress": [],
            "physicalAddress": "00:50:56:89:37:9f",
            "burnedInAddress": "00:50:56:89:37:9f",
            "description": "",
            "bandwidth": 1000000000,
            "mtu": 9214,
            "l3MtuConfigured": false,
            "l2Mru": 0,
            "lastStatusChangeTimestamp": 1683551369.9765966,
            "interfaceStatistics": {
                "updateInterval": 300.0,
                "inBitsRate": 0.0,
                "inPktsRate": 0.0,
                "outBitsRate": 0.0,
                "outPktsRate": 0.0
            },
            "interfaceCounters": {
                "inOctets": 689334489,
                "inUcastPkts": 231608,
                "inMulticastPkts": 4306974,
                "inBroadcastPkts": 454140,
                "inDiscards": 0,
                "inTotalPkts": 4992722,
                "outOctets": 19446436,
                "outUcastPkts": 846,
                "outMulticastPkts": 116796,
                "outBroadcastPkts": 9741,
                "outDiscards": 0,
                "outTotalPkts": 127383,
                "linkStatusChanges": 2,
                "totalInErrors": 0,
                "inputErrorsDetail": {
                    "runtFrames": 0,
                    "giantFrames": 0,
                    "fcsErrors": 0,
                    "alignmentErrors": 0,
                    "symbolErrors": 0,
                    "rxPause": 0
                },
                "totalOutErrors": 0,
                "outputErrorsDetail": {
                    "collisions": 0,
                    "lateCollisions": 0,
                    "deferredTransmissions": 0,
                    "txPause": 0
                },
                "counterRefreshTime": 1685000182.266076
            },
            "duplex": "duplexFull",
            "autoNegotiate": "unknown",
            "loopbackMode": "loopbackNone",
            "lanes": 0
        }
    }
}
"""
SHOW_CONNECTIONS = CommandTemplate("show patch panel | json")
"""
{
    "patches": {
        "alex": {
            "status": "down",
            "connectors": {
                "2": {
                    "connType": "port",
                    "status": "noLocalEnd",
                    "portConnectorInfo": {
                        "interface": "Ethernet501"
                    },
                    "alternatives": {}
                },
                "1": {
                    "connType": "port",
                    "status": "noLocalEnd",
                    "portConnectorInfo": {
                        "interface": "Ethernet500"
                    },
                    "alternatives": {}
                }
            },
            "lastStatusChange": 1684999194.3736515
        }
    }
}
"""


SHOW_VERSION_JSON = CommandTemplate("show version | json")
SHOW_VERSION = CommandTemplate("show version")
