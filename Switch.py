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
