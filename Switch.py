import pexpect
import re
from device_vendor import BaseVendor
from functools import wraps

from loguru import logger as logging

SERVICE_SSH_ACCESS = 'ssh'
SERVICE_TELNET_ACCESS = 'telnet'
SERVICE_TFTP_ACCESS = 'tftp'
REQUIRED_PROMPT = True
NOT_REQUIRED_PROMPT = False


class Switch:
    def __init__(self, switch_name, switch_vendor, switch_port, switch_username, switch_password):
        self.switch_name = switch_name
        self.switch_vendor = switch_vendor
        self.switch_context = None
        self.authenticated = False
        self.errors = False
        self.switch_port = switch_port

        # Set vendor variables
        self.switch_ssh_options = self.switch_vendor.console_options if self.switch_vendor.console_options else BaseVendor.console_options
        self.switch_username = self.switch_vendor.username if self.switch_vendor.username else switch_username
        self.switch_password = self.switch_vendor.password if self.switch_vendor.password else switch_password
        self.switch_service = self.switch_vendor.service if self.switch_vendor.service else BaseVendor.service
        self.backup_success_message = self.switch_vendor.backup_success_message if self.switch_vendor.backup_success_message else BaseVendor.backup_success_message
        self.login_prompt = self.switch_vendor.login_prompt if self.switch_vendor.login_prompt else BaseVendor.login_prompt
        self.password_prompt = self.switch_vendor.password_prompt if self.switch_vendor.password_prompt else BaseVendor.password_prompt
        self.console_prompt = self.switch_vendor.console_prompt if self.switch_vendor.console_prompt else BaseVendor.console_prompt
        self.quit_command = self.switch_vendor.quit_command if self.switch_vendor.quit_command else BaseVendor.quit_command

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
        self.log_info_context = f'SW: {self.switch_name}'
        connection_command = None
        if self.switch_service == SERVICE_SSH_ACCESS:
            connection_command = f'ssh {self.switch_ssh_options} {self.switch_username}@{self.switch_name}'

        if self.switch_service == SERVICE_TELNET_ACCESS:
            connection_command = f'telnet {self.switch_name}'

        logging.debug(f'{self.log_info_context} Connection command: {connection_command}')
        try:
            self.switch_context = pexpect.spawn(connection_command, timeout=30)
        except pexpect.exceptions.TIMEOUT:
            logging.error(f'{self.log_info_context} Timeout exceeded to: {self.switch_name}')
            return self

        # ----------------------------------------------------------------------------------------------
        if self.switch_service == SERVICE_TELNET_ACCESS:
            if not self.send_login_password(self.login_prompt, self.switch_username):
                self.set_error_flag(f'{self.log_info_context} get login prompt: {self.login_prompt} with Username: {self.switch_username}')
                return self

        if not self.send_login_password(self.password_prompt, self.switch_password):
            self.set_error_flag(f'{self.log_info_context} get password prompt: {self.password_prompt}')
            return self

        if not self.wait_console_prompt():
            self.set_error_flag(f'{self.log_info_context} get console prompt: {self.console_prompt}')
            return self

        self.authenticated = True
        # ----------------------------------------------------------------------------------------------
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logging.debug(f'{self.log_info_context} Connection closed for {self.switch_name}...')
        if self.switch_context:
            self.switch_context.close()

    def set_error_flag(self, error_string: str):
        logging.error(f'{self.log_info_context} - {error_string}')
        self.errors = True
        return

    @check_error
    def send_login_password(self, requested_prompt: str, custom_request: str) -> bool:
        if self.wait_console_prompt(requested_prompt):
            logging.debug(f'{self.log_info_context} Send Custom_request - {custom_request}')
            return_prompt = self.switch_context.sendline(custom_request)
            if return_prompt:
                return True
        logging.error(f'{self.log_info_context} Error interaction to: {self.switch_name}')
        return False

    @check_error
    @check_authenticated
    def send_switch_custom_command(self, custom_command: str, waiting_prompt: str, required_prompt: bool) -> None:
        logging.debug(f'{self.log_info_context} Send switch custom command: "{custom_command}" - waiting_prompt: "{waiting_prompt}"')
        self.switch_context.sendline(custom_command)

        if self.wait_console_prompt(waiting_prompt):
            logging.info(f'{self.log_info_context} SUCCESS custom command: {custom_command}')
        else:
            logging.warning(f'{self.log_info_context} FAIL custom command: {custom_command}')

        if required_prompt:
            self.wait_console_prompt()

    @check_error
    @check_authenticated
    def send_switch_command(self, switch_command: str) -> None:
        logging.debug(f'{self.log_info_context} Send switch command: {switch_command}')
        self.switch_context.sendline(switch_command)
        self.wait_console_prompt()

    @check_error
    def wait_console_prompt(self, waiting_prompt: str = '') -> bool:
        context_output = ''
        console_prompt = waiting_prompt if waiting_prompt else self.console_prompt
        logging.debug(f'{self.log_info_context} wait_console_prompt: {console_prompt}')
        try:
            while True:
                match = self.switch_context.expect([console_prompt, self.switch_vendor.space_wait])
                page = self.switch_context.before
                page = page.decode('utf-8')
                page = page.replace("\r\n", "\n")
                page = re.sub(" +\x08+ +\x08+", "\n", page)
                context_output += page

                if match == 0:
                    break
                elif match == 1:
                    self.switch_context.send(" ")
                else:
                    raise pexpect.exceptions.TIMEOUT
            logging.debug(f'{self.log_info_context}\n----\n{context_output}\n---\n')
            return True
        except pexpect.exceptions.EOF:
            logging.error(f'{self.log_info_context} EOF get console prompt: {console_prompt}')
            return False

        except pexpect.exceptions.TIMEOUT:
            logging.error(f'{self.log_info_context} TIMEOUT get console prompt: {console_prompt}')
            return False

    @check_error
    @check_authenticated
    def switch_quit_command(self)  -> None:
        logging.debug(f'{self.log_info_context} Switch quit command: {self.quit_command}')
        self.switch_context.sendline(self.quit_command)
