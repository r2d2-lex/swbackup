from device_vendor import detect_vendor, BaseVendor
import Switch as swSwitch
import config
import datetime


def get_date_time():
    return datetime.datetime.now().strftime('%Y%m%d')


def open_switch_filename(filename):
    with open(filename, 'r') as fs:
        switches = fs.read().splitlines()
        return switches


def backup_over_ssh(switch_name, vendor):
    backup_command = vendor.make_backup_command(config.TFTP_SERVER, switch_name, get_date_time())
    with swSwitch.Switch(switch_name, vendor, 22, config.USERNAME, config.PASSWORD) as switch:
        switch.send_switch_command(backup_command)


def backup_over_telnet(switch_name, vendor):
    pass


def backup_over_tftp(switch_name, vendor):
    pass


def backup_tftp_config(switch_name):
    result = ''
    print(f'Start backup of: {switch_name}')
    vendor = detect_vendor(switch_name)
    if vendor:
        if vendor.service == BaseVendor.SERVICE_SSH_ACCESS:
            backup_over_ssh(switch_name, vendor)

        if vendor.service == BaseVendor.SERVICE_TELNET_ACCESS:
            backup_over_telnet(switch_name, vendor)

        if vendor.service == BaseVendor.SERVICE_TFTP_ACCESS:
            backup_over_tftp(switch_name, vendor)

        print('\n')
    else:
        print(f'Fail backup {switch_name}')


def main():
    print(f'Backup switches configuration on TFTP: {config.TFTP_SERVER}\n')
    switches = open_switch_filename(config.SWITCHES_FILE)
    if switches:
        for switch in switches:
            backup_tftp_config(switch)
            input('Press any key...')


if __name__ == '__main__':
    main()
