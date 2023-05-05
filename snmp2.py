import subprocess
import config

oidSysDescr = 'iso.3.6.1.2.1.1.1.0'
HEX_STRING = 'Hex-STRING: '


def check_hex_string(string: str) -> str:
    if not isinstance(string, str):
        raise TypeError
    if HEX_STRING in string:
        try:
            str_modify = string.split(HEX_STRING, 1)[1]
            str_modify = ''.join(str_modify.split())
            return bytes.fromhex(str_modify).decode('latin-1')
        except (ValueError, IndexError):
            pass
    return string


def start_shell_command(cmd):
    result = subprocess.run(cmd.split(), stdout=subprocess.PIPE)
    output = result.stdout.decode('utf-8')
    output = check_hex_string(output)
    return output


def snmp_get_description(switch: str):
    try:
        snmp_command = f'{config.SNMP_GET_COMMAND} -v2c -c {config.SNMP_COMMUNITY} {switch} {oidSysDescr}'
        result = start_shell_command(snmp_command)
    except TypeError:
        result = f'Fail command: {snmp_command}'
    return result
