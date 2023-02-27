from device_vendor import Huawei


def detect_vendor(device_name):
    # Temporary stub )
    vendor = Huawei()
    print(f'Device name: {device_name} - {vendor.vendor_name}')
    return vendor
