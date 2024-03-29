import datetime
import socket
import sys
import time
from multiprocessing.pool import ThreadPool

from device_vendor import *
from Switch import *
from HPSwitch import HPSwitch
import config

from loguru import logger as logging
logging.remove(0)
logging.add(sys.stderr, level=config.LOGGING_LEVEL)

# Кол-во одновременных backup - заданий
THREAD_COUNT = 4


def compare_octets(switch_octets: list[str], tftp_octets: list[str]) -> bool:
    """
        Сравнивает 3 первых октета tftp сервера с октетами свитча
    """
    octet_index = 0
    for sw_octet in switch_octets:
        if octet_index == 3:
            return True
        try:
            if sw_octet == tftp_octets[octet_index]:
                octet_index += 1
                continue
        except(IndexError, KeyError):
            logging.info('Data error')
        return False


def detect_tftp_server(switch_name: str, tftp_servers: list) -> str:
    tftp_ip = BaseVendor.tftp_server
    try:
        switch_ip = socket.gethostbyname(switch_name)
        logging.info(f'Swith IP: {switch_ip}')
        switch_octets = switch_ip.split('.', 4)
        for server in tftp_servers:
            server_ip = socket.gethostbyname(server)
            tftp_octets = server_ip.split('.', 4)
            if compare_octets(switch_octets , tftp_octets):
                return server_ip
    except socket.gaierror as error:
        logging.info(error)
    return tftp_ip


def get_date_time() -> str:
    return datetime.datetime.now().strftime('%Y%m%d')


def open_switch_filename(filename: str) -> list:
    with open(filename, 'r') as fs:
        switches = fs.read().splitlines()
        return switches


def backup_over_console(switch_name: str, tftp_server: str, vendor: ALL_DEVICE_VENDORS) -> None:

    backup_command = vendor.make_backup_command(tftp_server, switch_name, get_date_time())
    with Switch(switch_name, vendor, 22, config.USERNAME, config.PASSWORD) as switch:
        if vendor.vendor_name == HP.vendor_name:
            switch.send_switch_custom_command('_cmdline-mode on', '[Y/N]', NOT_REQUIRED_PROMPT)
            switch.send_switch_custom_command('Y', 'password:', NOT_REQUIRED_PROMPT)
            switch.send_switch_custom_command(HP.secret_password, 'Warning:', REQUIRED_PROMPT)
            switch.send_switch_custom_command(backup_command, vendor.backup_success_message, REQUIRED_PROMPT)

        elif vendor.vendor_name == AlliedWare.vendor_name:
            config_name = vendor.generate_switch_config_name(switch_name)
            logging.debug(f'AW config_name: "{config_name}"')
            switch.send_switch_command('enable')
            switch.send_switch_command(f'copy boot.cfg {config_name}')
            switch.send_switch_custom_command(backup_command, vendor.backup_success_message, REQUIRED_PROMPT)
            switch.send_switch_custom_command(f'delete {config_name}', '(y/n)', NOT_REQUIRED_PROMPT)
            switch.send_switch_custom_command('y'+CR_LF, 'Deleting.....', REQUIRED_PROMPT)
        else:
            switch.send_switch_custom_command(backup_command, vendor.backup_success_message, REQUIRED_PROMPT)
        switch.switch_quit_command()


def backup_over_snmp(switch_name, tftp_server: str, vendor):
    pass


def backup_over_http(switch_name: str, tftp_server: str, vendor: ALL_DEVICE_VENDORS) -> None:
    config_name = switch_name + '-' + get_date_time() + '.cfg'
    if vendor.vendor_name == HP_OC.vendor_name:
        with HPSwitch(switch_name,
                      config.USERNAME,
                      config.PASSWORD,
                      tftp_server,
                      config_name,
                      ) as switch:
            status = switch.upload_to_tftp()
            if status:
                message = f'Success upload config {config_name} on {config.TFTP_SERVER}'
            else:
                message = f'Error upload config {config_name} on {config.TFTP_SERVER}'
            logging.info(message)


def backup_tftp_config(switch_name: str) -> None:
    logging.info(f'Start backup of: {switch_name}')
    vendor = detect_vendor(switch_name)
    tftp_server = detect_tftp_server(switch_name, config.TFTP_SERVERS)
    args = (switch_name, tftp_server, vendor)
    if vendor:
        if vendor.service == BaseVendor.SERVICE_SSH_ACCESS:
            backup_over_console(*args)

        if vendor.service == BaseVendor.SERVICE_TELNET_ACCESS:
            backup_over_console(*args)

        if vendor.service == BaseVendor.SERVICE_SNMP_ACCESS:
            backup_over_snmp(*args)

        if vendor.service == BaseVendor.SERVICE_HTTP_ACCESS:
            backup_over_http(*args)

    else:
        logging.warning(f'Vendor not found. Fail backup switch: {switch_name}')
    logging.info(f'End backup of {switch_name}...\r\n')


def main():
    logging.info(f'Backup switches configuration on TFTP: {config.TFTP_SERVER}')
    switches = open_switch_filename(config.SWITCHES_FILE)
    time_start = time.time()
    if switches:
        pool = ThreadPool(THREAD_COUNT)
        pool.map(backup_tftp_config, switches)
    time_end = time.time()
    logging.info('Finished backup of commutators in {:.3f} seconds !!!', time_end - time_start)


if __name__ == '__main__':
    main()
