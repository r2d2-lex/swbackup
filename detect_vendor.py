from device_vendor import Huawei
import snmp
import config

# 'iso.3.6.1.2.1.1.1.0'
VENDOR_OID = 'sysDescr'


def detect_vendor(device_name):
    vendor = ''
    vendor_value = snmp.snmp_get(device_name, config.SNMP_COMMUNITY, VENDOR_OID)
    if vendor_value:
        print(vendor_value)

        # code search vendor in result
        vendor = Huawei()
        print(f'Device name: {device_name} - {vendor.vendor_name}')
    return vendor
