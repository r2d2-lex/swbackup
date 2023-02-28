from device_vendor import detect_vendor
import config
import datetime


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
    else:
        print(f'Fail backup {switch_name}')


def main():
    print(f'Backup switches configuration on TFTP: {config.TFTP_SERVER}\n')
    switches = open_switch_filename(config.SWITCHES_FILE)
    if switches:
        for switch in switches:
            backup_tftp_config(switch)


if __name__ == '__main__':
    main()
