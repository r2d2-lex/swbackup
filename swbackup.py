from device_vendor import detect_vendor, BaseVendor
import Switch as swSwitch
import config
import datetime
import logging

# logging.basicConfig(level=logging.CRITICAL, filename=config.LOG_FILE, filemode='w')
logging.basicConfig(level=logging.DEBUG)


def get_date_time():
    return datetime.datetime.now().strftime('%Y%m%d')


def open_switch_filename(filename):
    with open(filename, 'r') as fs:
        switches = fs.read().splitlines()
        return switches


def backup_over_console(switch_name, vendor):
    tftp_server = config.TFTP_SERVER
    if vendor.tftp_server:
        tftp_server = vendor.tftp_server

    backup_command = vendor.make_backup_command(tftp_server, switch_name, get_date_time())
    with swSwitch.Switch(switch_name, vendor, 22, config.USERNAME, config.PASSWORD) as switch:
        switch.send_switch_backup_config(backup_command)
        # switch.send_switch_command('display lldp neighbor brief')
        switch.switch_quit_command()


def backup_over_tftp(switch_name, vendor):
    pass


def backup_tftp_config(switch_name):
    logging.info(f'Start backup of: {switch_name}')
    vendor = detect_vendor(switch_name)
    if vendor:
        if vendor.service == BaseVendor.SERVICE_SSH_ACCESS:
            backup_over_console(switch_name, vendor)

        if vendor.service == BaseVendor.SERVICE_TELNET_ACCESS:
            backup_over_console(switch_name, vendor)

        if vendor.service == BaseVendor.SERVICE_TFTP_ACCESS:
            backup_over_tftp(switch_name, vendor)

    else:
        logging.warning(f'Fail backup {switch_name}')


def main():
    logging.info(f'Backup switches configuration on TFTP: {config.TFTP_SERVER}')
    switches = open_switch_filename(config.SWITCHES_FILE)
    if switches:
        for switch in switches:
            backup_tftp_config(switch)
            print('\n')
            # input('Press any key...')


if __name__ == '__main__':
    main()
