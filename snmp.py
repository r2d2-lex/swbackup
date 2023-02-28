from pysnmp.hlapi import *
from pysnmp.smi import error

SNMPv1 = 0
SNMPv2c = 1
SNMP_MIB = 'SNMPv2-MIB'


def snmp_get(device_address, community, oid, device_port=161) -> str:
    result = ''

    iterator = getCmd(
        SnmpEngine(),
        CommunityData(community, mpModel=SNMPv2c),
        UdpTransportTarget((device_address, device_port)),
        ContextData(),
        ObjectType(ObjectIdentity(SNMP_MIB, oid, 0))
    )

    try:
        errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
    except error.SmiError:
        print(f'No symbol:{SNMP_MIB}::{oid}')
        return result

    if errorIndication:
        print(errorIndication)

    elif errorStatus:
        print('%s at %s' % (errorStatus.prettyPrint(),
                            errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))

    else:
        for varBind in varBinds:
            result = (' = '.join([x.prettyPrint() for x in varBind]))

    return result
