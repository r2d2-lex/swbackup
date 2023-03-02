import pexpect
import logging

logging.basicConfig(level=logging.DEBUG)


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
            self.switch_context = pexpect.spawn(connection_command, timeout=30)
        except pexpect.exceptions.TIMEOUT:
            logging.error(f'Timeout exceeded to: {self.switch_name}')

        # ----------------------------------------------------------------------------------------------
        if self.switch_vendor.service == SERVICE_TELNET_ACCESS:
            if not self.send_custom_request(self.switch_vendor.login_prompt, self.switch_username):
                return

        if not self.send_custom_request(self.switch_vendor.password_prompt, self.switch_password):
            return

        # !!! send_custom_request не ждёт приглашение консоли...
        self.expect_return_view()
        # ----------------------------------------------------------------------------------------------
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.switch_context:
            self.switch_context.close()
            logging.debug('Connection closed...')

    def send_custom_request(self, requested_prompt, custom_request) -> bool:
        return_prompt = self.switch_context.expect(requested_prompt)
        if return_prompt == 0:
            logging.debug(f'Requested_prompt: {requested_prompt}\nReturn: {self.switch_context.before}')

            logging.debug(f'Send Custom_request - {custom_request}')
            return_prompt = self.switch_context.sendline(custom_request)
            logging.debug(f'\nReturn: {self.switch_context.before}')
            if return_prompt:
                print('Return TRUE')
                return True
            else:
                print('Return False')
                return False
        else:
            logging.error(f'Error interaction to: {self.switch_name}')
            return False

    def send_switch_backup_config(self, backup_command):
        logging.debug(f'Send switch backup config command: {backup_command}')
        self.switch_context.sendline(backup_command)
        if self.switch_context.expect(self.switch_vendor.backup_success_message) == 0:
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
