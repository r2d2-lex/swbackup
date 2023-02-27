from dataclasses import dataclass


@dataclass
class Huawei:
    console_prompt: str = '[>#]'
    password_prompt: str = '[Pp]assword'
    backup_command: str = ''
    space_wait: str = '---- More ----'
