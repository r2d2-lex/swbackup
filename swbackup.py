import config
from device_vendor import Huawei
from detect_vendor import detect_vendor
import datetime
import pexpect


class Switch:
    def __init__(self, switch_name, switch_service, switch_port, switch_username, switch_password):
        self.switch_name = switch_name
        self.switch_username = switch_username
        self.switch_password = switch_password
        self.switch_context = None
        self.switch_port = switch_port
        self.connection_command = switch_service

    def __enter__(self):
        self.switch_context = pexpect.spawn(f'{self.connection_command} {self.switch_name}')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.switch_context:
            self.switch_context.close()

    def send_switch_command(self, switch_command):
        self.switch_context.expect(switch_command)


def get_date_time():
    return datetime.datetime.now().strftime('%Y%m%d')


def open_switch_filename(filename):
    with open(filename, 'r') as fs:
        switches = fs.read().splitlines()
        return switches


def backup_tftp_config(switch_name):
    date_part = get_date_time()
    print(f'Start backup of: {switch_name}')
    vendor = detect_vendor(switch_name)
    if vendor:
        backup_command = vendor.make_backup_command(config.TFTP_SERVER, switch_name, date_part)
        print(backup_command)
        print('\n')


def main():
    print(f'Backup switches configuration on TFTP: {config.TFTP_SERVER}\n')
    switches = open_switch_filename(config.SWITCHES_FILE)
    if switches:
        for switch in switches:
            backup_tftp_config(switch)


if __name__ == '__main__':
    main()
