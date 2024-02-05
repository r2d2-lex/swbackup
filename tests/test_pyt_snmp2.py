# Тесты для PyTest
from unittest.mock import patch
from snmp2 import check_hex_string, start_shell_command, snmp_get_description
import pytest
import subprocess

'''
    snmp_get_description tests
'''
def test_snmp_get_description_function_exists():
    import snmp2
    assert hasattr(snmp2, 'snmp_get_description')


'''
    start_shell_command tests
'''
def test_start_shell_command_function_exists():
    import snmp2
    assert hasattr(snmp2, 'start_shell_command')

@pytest.mark.parametrize('input_data, exception_type', [
    pytest.param(
        (1,), AttributeError,
        id='Argument must be string (1)',
    ),
    pytest.param(
        (None,), AttributeError,
        id='Argument must be string (2)',
    ),
    pytest.param(
        ('/sbin/XyZwQwerty',), FileNotFoundError,
        id='File must be exists',
    ),
    pytest.param(
        ('/etc/issue',), OSError,
        id='Exec format error',
    ),
    pytest.param(
        ('',), IndexError,
        id='Argument must be not empty string',
    ),
    pytest.param(
        ('/root',), PermissionError,
        id='Must have permissions to run the file',
    ),
]
)
def test_start_shell_command_exception_handling(input_data, exception_type):
    try:
        start_shell_command(*input_data)
    except exception_type:
        pytest.fail('Fail')

def test_start_shell_command_must_take_one_argument():
    with pytest.raises(TypeError):
        start_shell_command('1','2')

def test_start_shell_command_execution_returns_string():
    assert isinstance(start_shell_command('echo 123'), str)

def test_start_shell_command_execution_returns():
    assert start_shell_command('echo 123') == '123\n'

@patch.object(subprocess, 'run')
def test_start_shell_command_execution_returns_right_value1(mock_subprocess_run):
    mock_subprocess_run.return_value = subprocess.CompletedProcess(args=[], returncode=0, stdout='123\n')
    result = start_shell_command('echo 123')
    assert result == '123\n'


"""
    check_hex_string tests
    
    iso.3.6.1.2.1.1.1.0 = Hex-STRING: 41 6C 6C 69 65 64 57 61 72 65 20 50 6C 75 73 20
    28 54 4D 29 20 32 2E 31 2E 32 CE 20
"""
def test_snmp2_module_exists():
    try:
        import snmp2
    except ModuleNotFoundError:
        pytest.fail('Module snmp2 not found')

def test_check_hex_string_function_exists():
    import snmp2
    assert hasattr(snmp2, 'check_hex_string')

@pytest.mark.parametrize('input_data, exception_type', [
    pytest.param(
        ('string',), TypeError,
        id='Function must take one arg',
    ),
    pytest.param(
        ('Hex-STRING: 41 6C 6C 69 65 64 57 61 72 65 20 50 6C 75 73 20 28 54 4D 29 20 32 2E 31 2E 32 CE 20',), TypeError,
        id='Function must returns string',
    ),
    pytest.param(
        ('iso.3.6.1.2.1.1.1.0 = Hex-STRING: x',), ValueError,
        id='Function arg must be contains hex value',
    ),
]
)
def test_check_hex_string_exception_handling(input_data, exception_type):
    try:
        check_hex_string(*input_data)
    except exception_type:
        pytest.fail('Fail')

def test_check_hex_string_raises_on_invalid_argument_type():
    with pytest.raises(TypeError):
        check_hex_string(None)

def test_check_hex_string_returns_string_type():
    result = check_hex_string('string')
    assert isinstance(result, str)

@pytest.mark.parametrize('input_data, expected_data', [
    pytest.param(
        ('iso.3.6.1.2.1.1.1.0 = Hex-STRING: 41 6C 6C 69 65 64 57 61 72 65 20 50 6C 75 73 20',), 'AlliedWare Plus',
        id='Function must return right value',
    ),
    pytest.param(
        ('string',), 'string',
        id='Function must return right value',
    ),
]
)
def test_check_hex_string_returns_right_value(input_data, expected_data):
    result = check_hex_string(*input_data)
    assert result == expected_data
