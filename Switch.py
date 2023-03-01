import pexpect
import logging

logging.basicConfig(level=logging.INFO)


SSH_OPTIONS = '-o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no'
SERVICE_SSH_ACCESS = 'ssh'
SERVICE_TELNET_ACCESS = 'telnet'
SERVICE_TFTP_ACCESS = 'tftp'


class Switch:
    def __init__(self, switch_name, switch_vendor, switch_port, switch_username, switch_password):
        self.switch_name = switch_name
        self.switch_vendor = switch_vendor
        self.switch_username = switch_username
        self.switch_password = switch_password
        self.switch_context = None
        self.switch_port = switch_port

    def __enter__(self):
        connection_command = None
        if self.switch_vendor.service == SERVICE_SSH_ACCESS:
            connection_command = f'ssh {SSH_OPTIONS} {self.switch_username}@{self.switch_name}'

        if self.switch_vendor.service == SERVICE_TELNET_ACCESS:
            connection_command = f'telnet {self.switch_name}'

        logging.debug(f'Connection command: {connection_command}')
        try:
            self.switch_context = pexpect.spawn(connection_command, timeout=300)
        except pexpect.exceptions.TIMEOUT:
            logging.error(f'Timeout exceeded to: {self.switch_name}')

        password_request = self.switch_context.expect('[Pp]assword:')
        if password_request == 0:
            logging.info(f'Connection to - {self.switch_name}')
            logging.debug(f'... {self.switch_context.before}')

            if self.switch_context.sendline(self.switch_password):
                logging.debug(f'Send password - {self.switch_password}')
                self.expect_return_view()
            else:
                logging.debug(f'Send password:: {self.switch_password}')
                logging.debug(f'... {self.switch_context.before}')

        else:
            logging.error(f'Connection to: {self.switch_name}')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.switch_context:
            self.switch_context.close()
            logging.debug('Connection closed...')

    def send_switch_backup_config(self, backup_command):
        logging.debug(f'Send switch backup config command: {backup_command}')
        self.switch_context.sendline(backup_command)
        if self.switch_context.expect(self.switch_vendor.backup_sucess_message) == 0:
            logging.info(f'SUCCESS backup config: {self.switch_name}')
        else:
            logging.warning(f'FAIL backup config: {self.switch_name}')

    def send_switch_command(self, switch_command):
        logging.debug(f'Send switch command: {switch_command}')
        self.switch_context.sendline(switch_command)
        self.expect_return_view()

    def expect_return_view(self):
        if self.switch_context.expect(self.switch_vendor.console_prompt) == 0:
            logging.debug(f'\n----\n{self.switch_context.before}\n---\n')
        else:
            logging.error(f'Cannot get console prompt: {self.switch_vendor.console_prompt}')

    def switch_quit_command(self):
        self.switch_context.sendline(self.switch_vendor.quit_command)
        logging.debug(f'Switch quit command: {self.switch_vendor.quit_command}')
