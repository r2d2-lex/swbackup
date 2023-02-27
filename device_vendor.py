from dataclasses import dataclass


@dataclass
class Huawei:
    vendor_name: str = 'Huawei'
    console_prompt: str = '[>#]'
    password_prompt: str = '[Pp]assword'
    backup_command: str = 'tftp {TFTP_SERVER} put vrpcfg.zip {SWITCH_NAME}-{BACKUP_DATE}.zip'
    space_wait: str = '---- More ----'

    def make_backup_command(self, tftp_server, switch_name, backup_date):
        return self.backup_command.format(TFTP_SERVER=tftp_server,
                                          SWITCH_NAME=switch_name,
                                          BACKUP_DATE=backup_date)
