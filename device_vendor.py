from dataclasses import dataclass
import snmp
import config
import logging

logging.basicConfig(level=logging.DEBUG)

HUAWEI_VENDOR = 'Huawei'
AT_VENDOR = 'AlliedTelesis'
AW_VENDOR = 'AlliedWare'
HP_VENDOR = 'HP'
T3COM_VENDOR = '3COM'
VENDOR_OID = 'sysDescr'


@dataclass()
class BaseVendor:
    SERVICE_SSH_ACCESS = 'ssh'
    SERVICE_TELNET_ACCESS = 'telnet'
    SERVICE_TFTP_ACCESS = 'tftp'
    ALL_BACKUP_SERVICES = (
        SERVICE_SSH_ACCESS,
        SERVICE_TELNET_ACCESS,
        SERVICE_TFTP_ACCESS,
    )

    vendor_name: str = ''
    space_wait: str = ''
    service: str = ''
    backup_command: str = ''
    base_words: tuple = ()
    console_prompt: str = '[>#]'
    password_prompt: str = '[Pp]assword:'
    login_prompt: str = ''
    quit_command: str = ''
    backup_success_message: str = ''
    tftp_server: str = ''

    def make_backup_command(self, tftp_server, switch_name, backup_date):
        return self.backup_command.format(TFTP_SERVER=tftp_server,
                                          SWITCH_NAME=switch_name,
                                          BACKUP_DATE=backup_date)


@dataclass
class Huawei(BaseVendor):
    vendor_name: str = HUAWEI_VENDOR
    backup_command: str = 'tftp {TFTP_SERVER} put vrpcfg.zip {SWITCH_NAME}-{BACKUP_DATE}.zip'
    backup_success_message: str = 'TFTP: Uploading the file successfully.'
    space_wait: str = '---- More ----'
    service: str = BaseVendor.SERVICE_SSH_ACCESS
    quit_command: str = 'quit'

    base_words = (
        'Huawei',
        'S5735',
    )


@dataclass
class AlliedTelesis(BaseVendor):
    vendor_name: str = AT_VENDOR
    backup_command: str = 'Upload Method=tftp DestFile={SWITCH_NAME}-{BACKUP_DATE}.cfg Server={TFTP_SERVER} ' \
                          'srcFile=flash:boot.cfg '
    service: str = BaseVendor.SERVICE_SSH_ACCESS
    base_words = (
        'Allied Telesis',
        'AT-9448Ts',
    )


@dataclass
class AlliedWare(BaseVendor):
    vendor_name: str = AW_VENDOR
    service: str = BaseVendor.SERVICE_TELNET_ACCESS
    login_prompt: str = '[Ll]ogin:'
    base_words = (
        'AlliedWare',
    )


@dataclass
class HP(BaseVendor):
    vendor_name: str = HP_VENDOR
    service: str = BaseVendor.SERVICE_TFTP_ACCESS
    base_words = (
        'HPE OfficeConnect',
        '1820 48G J9981A',
    )


@dataclass
class T3COM(BaseVendor):
    vendor_name: str = T3COM_VENDOR
    service: str = BaseVendor.SERVICE_TELNET_ACCESS
    backup_command: str = 'tftp {TFTP_SERVER} put startup.cfg {SWITCH_NAME}-{BACKUP_DATE}.cfg'
    backup_success_message: str = 'File uploaded successfully.'
    login_prompt: str = 'Username:'
    quit_command: str = 'quit'
    tftp_server: str = config.TFTP_SERVER2
    base_words = (
        '3Com',
    )


ALL_DEVICE_VENDORS = (Huawei, AlliedTelesis, HP, T3COM, AlliedWare)


def search_vendor_word(vendor_value):
    vendor_word = ''
    result = ''

    vendor_value = vendor_value.lower()
    vendor_value = ' '.join(vendor_value.split())
    logging.debug(f'VENDOR STRING: {vendor_value}')
    for _class in ALL_DEVICE_VENDORS:
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
    if vendor_word == AW_VENDOR:
        result = AlliedWare()
    if vendor_word == HP_VENDOR:
        result = HP()
    if vendor_word == T3COM_VENDOR:
        result = T3COM()
    return result


def detect_snmp_vendor(device_name):
    vendor = ''
    vendor_value = snmp.snmp_get(device_name, config.SNMP_COMMUNITY, VENDOR_OID)
    if vendor_value:
        vendor = search_vendor_word(vendor_value)
        if vendor:
            logging.info(f'Device name: {device_name} - {vendor.vendor_name}')
    return vendor


def detect_vendor(device_name):
    return detect_snmp_vendor(device_name)
