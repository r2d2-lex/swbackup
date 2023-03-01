import pexpect

SSH_OPTIONS = '-o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no'


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
        if self.switch_vendor.service == 'ssh':
            connection_command = f'ssh {SSH_OPTIONS} {self.switch_username}@{self.switch_name}'

        if self.switch_vendor.service == 'telnet':
            connection_command = f'telnet {self.switch_name}'

        print(f'Connection command: {connection_command}')
        self.switch_context = pexpect.spawn(connection_command, timeout=300)
        # pexpect.exceptions.TIMEOUT: Timeout exceeded.

        password_request = self.switch_context.expect('[Pp]assword:')
        if password_request == 0:
            print(f'SUCCESS: Connection to - {self.switch_name}')
            print(f'... {self.switch_context.before}')

            if self.switch_context.sendline(self.switch_password):
                print(f'SUCCESS: send password - {self.switch_password}')
                self.expect_return_view()

            else:
                print(f'ERROR: send password:: {self.switch_password}')
                print(f'... {self.switch_context.before}')

        else:
            print(f'ERROR: Connection to: {self.switch_name}')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.switch_context:
            self.switch_context.close()
            print('INFO: connection closed...')

    def send_switch_command(self, switch_command):
        print(f'INFO: send switch command: {switch_command}')
        self.switch_context.sendline(switch_command)
        self.expect_return_view()

    def expect_return_view(self):
        if self.switch_context.expect(self.switch_vendor.console_prompt) == 0:
            print(f'SUCCESS: get console prompt - {self.switch_vendor.console_prompt}')
            print(f'... {self.switch_context.before}')
        else:
            print('WARNING: cannot get console prompt')

    def switch_quit_command(self):
        print(f'INFO: switch quit command: self.switch_vendor.quit_command')
        self.switch_context.sendline(self.switch_vendor.quit_command)
