from dataclasses import dataclass
import snmp
import config

HUAWEI_VENDOR = 'Huawei'
AT_VENDOR = 'alliedtelesis'
HP_VENDOR = 'hp'
THREE_COM_VENDOR = '3com'
VENDOR_OID = 'sysDescr'


@dataclass()
class BaseVendor:
    vendor_name: str = ''
    space_wait: str = ''
    service: str = ''
    backup_command: str = ''
    base_words: tuple = ()
    console_prompt: str = '[>#]'
    password_prompt: str = '[Pp]assword'
    login_prompt: str = ''

    def make_backup_command(self, tftp_server, switch_name, backup_date):
        return self.backup_command.format(TFTP_SERVER=tftp_server,
                                          SWITCH_NAME=switch_name,
                                          BACKUP_DATE=backup_date)


@dataclass
class Huawei(BaseVendor):
    vendor_name: str = HUAWEI_VENDOR
    backup_command: str = 'tftp {TFTP_SERVER} put vrpcfg.zip {SWITCH_NAME}-{BACKUP_DATE}.zip'
    space_wait: str = '---- More ----'
    service: str = 'ssh'
    base_words = (
        'Huawei',
        'S5735',
    )


@dataclass
class AlliedTelesis(BaseVendor):
    vendor_name: str = AT_VENDOR
    backup_command: str = 'Upload Method=tftp DestFile={SWITCH_NAME}-{BACKUP_DATE}.cfg Server={TFTP_SERVER} ' \
                          'srcFile=flash:boot.cfg '
    service: str = 'telnet'
    login_prompt: str = 'Login:'
    base_words = (
        'Allied Telesis',
        'AT-9448Ts',
    )


@dataclass
class HP(BaseVendor):
    vendor_name: str = HP_VENDOR


@dataclass
class Three_COM(BaseVendor):
    vendor_name: str = THREE_COM_VENDOR


ALL_DEVICE_VENDORS = (Huawei, AlliedTelesis, HP, Three_COM)


def search_vendor_word(vendor_value):
    vendor_word = ''
    result = ''

    vendor_value = vendor_value.lower()
    vendor_value = ' '.join(vendor_value.split())
    print(f'VENDOR STRING: {vendor_value}')
    for _class in ALL_DEVICE_VENDORS:
        print(f'Class {_class.vendor_name} - class base-words: {_class.base_words}')
        for word in _class.base_words:
            word = word.lower()
            if vendor_value.find(word) != -1:
                vendor_word = _class.vendor_name
                break
        if vendor_word:
            break

    if vendor_word == HUAWEI_VENDOR:
        result = Huawei()
    if vendor_word == AT_VENDOR:
        result = AlliedTelesis()
    if vendor_word == HP_VENDOR:
        result = HP()
    if vendor_word == THREE_COM_VENDOR:
        result = Three_COM()
    return result


def detect_snmp_vendor(device_name):
    vendor = ''
    vendor_value = snmp.snmp_get(device_name, config.SNMP_COMMUNITY, VENDOR_OID)
    if vendor_value:
        vendor = search_vendor_word(vendor_value)
        if vendor:
            print(f'Device name: {device_name} - {vendor.vendor_name}')
    # code search vendor in result
    # vendor = Huawei()
    return vendor


def detect_vendor(device_name):
    return detect_snmp_vendor(device_name)
