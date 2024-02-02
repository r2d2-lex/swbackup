import subprocess
import config

from loguru import logger as logging

oidSysDescr = 'iso.3.6.1.2.1.1.1.0'
HEX_STRING = 'Hex-STRING: '


def check_hex_string(string: str) -> str:
    if not isinstance(string, str):
        raise TypeError
    if HEX_STRING in string:
        try:
            str_modify = string.split(HEX_STRING, 1)[1]
            result = bytes.fromhex(str_modify).decode('latin-1')
            result = ' '.join(result.split())
            return result
        except (ValueError, TypeError):
            pass
    return string


def start_shell_command(cmd: str) -> str:
    try:
        result = subprocess.run(cmd.split(), stdout=subprocess.PIPE, text=True)
        return result.stdout
    except (AttributeError, FileNotFoundError, OSError, PermissionError, IndexError) as err:
        print(f'Error running command: {cmd}\r\nDetails: {err}')
    return ''


def snmp_get_description(switch: str) -> str:
    result = ''
    try:
        snmp_command = f'{config.SNMP_GET_COMMAND} -v2c -c {config.SNMP_COMMUNITY} {switch} {oidSysDescr}'
        result = start_shell_command(snmp_command)
        result = check_hex_string(result)
    except TypeError:
        logging.error('Fail command: {}', result)
    return result


if __name__ == "__main__":
    arg = 'Hex-STRING: '
    print(check_hex_string(arg))
