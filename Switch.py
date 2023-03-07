import pexpect
import logging
from functools import wraps

logging.basicConfig(level=logging.DEBUG)

SERVICE_SSH_ACCESS = 'ssh'
SERVICE_TELNET_ACCESS = 'telnet'
SERVICE_TFTP_ACCESS = 'tftp'


class Switch:
    def __init__(self, switch_name, switch_vendor, switch_port, switch_username, switch_password):
        self.switch_name = switch_name
        self.switch_vendor = switch_vendor
        self.switch_context = None
        self.authenticated = False
        self.errors = False
        self.switch_port = switch_port

        # Set vendor variables
        self.switch_ssh_options = self.switch_vendor.console_options if self.switch_vendor.console_options else ''
        self.switch_username = self.switch_vendor.username if self.switch_vendor.username else switch_username
        self.switch_password = self.switch_vendor.password if self.switch_vendor.password else switch_password
        self.switch_service = self.switch_vendor.service if self.switch_vendor.service else SERVICE_SSH_ACCESS
        self.backup_success_message = self.switch_vendor.backup_success_message if self.switch_vendor.backup_success_message else ''
        self.login_prompt = self.switch_vendor.login_prompt if self.switch_vendor.login_prompt else ''
        self.password_prompt = self.switch_vendor.password_prompt if self.switch_vendor.password_prompt else ''
        self.console_prompt = self.switch_vendor.console_prompt if self.switch_vendor.console_prompt else ''
        self.quit_command = self.switch_vendor.quit_command if self.switch_vendor.quit_command else ''

    def check_authenticated(func):
        @wraps(func)
        def wrap(self, *args, **kwargs):
            if self.authenticated:
                return func(self, *args, **kwargs)
            else:
                logging.debug('Not authenticated...')
                return
        return wrap

    def check_error(func):
        @wraps(func)
        def wrap(self, *args, **kwargs):
            if self.errors:
                logging.debug('To more errors...')
                return
            else:
                return func(self, *args, **kwargs)
        return wrap

    def __enter__(self):
        connection_command = None
        if self.switch_service == SERVICE_SSH_ACCESS:
            connection_command = f'ssh {self.switch_ssh_options} {self.switch_username}@{self.switch_name}'

        if self.switch_service == SERVICE_TELNET_ACCESS:
            connection_command = f'telnet {self.switch_name}'

        logging.debug(f'Connection command: {connection_command}')
        try:
            self.switch_context = pexpect.spawn(connection_command, timeout=30)
        except pexpect.exceptions.TIMEOUT:
            logging.error(f'Timeout exceeded to: {self.switch_name}')
            return self

        # ----------------------------------------------------------------------------------------------
        if self.switch_service == SERVICE_TELNET_ACCESS:
            if not self.send_login_password(self.login_prompt, self.switch_username):
                self.set_error_flag(f'get login prompt: {self.login_prompt} with Username: {self.switch_username}')
                return self

        if not self.send_login_password(self.password_prompt, self.switch_password):
            self.set_error_flag(f'get password prompt: {self.password_prompt}')
            return self

        if not self.wait_console_prompt():
            self.set_error_flag(f'get console prompt: {self.console_prompt}')
            return self

        self.authenticated = True
        # ----------------------------------------------------------------------------------------------
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.switch_context:
            self.switch_context.close()
            logging.debug('Connection closed...')

    def set_error_flag(self, error_string):
        logging.error(error_string)
        self.errors = True
        return

    @check_error
    def send_login_password(self, requested_prompt, custom_request) -> bool:
        if self.wait_console_prompt(requested_prompt):
            logging.debug(f'Send Custom_request - {custom_request}')
            return_prompt = self.switch_context.sendline(custom_request)
            if return_prompt:
                return True
        logging.error(f'Error interaction to: {self.switch_name}')
        return False

    @check_error
    @check_authenticated
    def send_switch_backup_config(self, backup_command):
        logging.debug(f'Send switch backup config command: {backup_command}')
        self.switch_context.sendline(backup_command)

        if self.wait_console_prompt(self.backup_success_message):
            logging.info(f'SUCCESS backup config: {self.switch_name}')
        else:
            logging.warning(f'FAIL backup config: {self.switch_name}')

        self.wait_console_prompt()

    @check_error
    @check_authenticated
    def send_switch_command(self, switch_command):
        logging.debug(f'Send switch command: {switch_command}')
        self.switch_context.sendline(switch_command)
        self.wait_console_prompt()

    @check_error
    def wait_console_prompt(self, waiting_prompt='') -> bool:
        console_prompt = waiting_prompt if waiting_prompt else self.console_prompt
        logging.debug(f'wait_console_prompt: {console_prompt}')
        try:
            if self.switch_context.expect(console_prompt) == 0:
                logging.debug(f'\n----\n{self.switch_context.before}\n---\n')
                return True
        except pexpect.exceptions.EOF:
            logging.error(f'EOF get console prompt: {console_prompt}')
            return False

        except pexpect.exceptions.TIMEOUT:
            logging.error(f'TIMEOUT get console prompt: {console_prompt}')
            return False

    @check_error
    @check_authenticated
    def switch_quit_command(self):
        logging.debug(f'Switch quit command: {self.quit_command}')
        self.switch_context.sendline(self.quit_command)
