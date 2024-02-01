from unittest import TestCase, mock
from snmp2 import check_hex_string, start_shell_command


class StartShellCommandTestCase(TestCase):
    def test_start_shell_command_function_exists(self):
        import snmp2
        self.assertTrue(
            hasattr(snmp2, 'start_shell_command')
        )

    def test_start_shell_command_is_string_argument(self):
        with self.assertRaises(AttributeError):
            start_shell_command(1)

    def test_start_shell_command_is_string_argument2(self):
        with self.assertRaises(AttributeError):
            start_shell_command(None)

    def test_start_shell_command_must_take_one_argument(self):
        with self.assertRaises(TypeError):
            start_shell_command('1','2')

    def test_start_shell_command_execution_returns_string(self):
        self.assertTrue(isinstance(start_shell_command('echo 123'), str))

    # except (FileNotFoundError, OSError, PermissionError, IndexError) as err:
    def test_start_shell_command_exists(self):
        try:
            start_shell_command('/sbin/XyZwQwerty')
        except FileNotFoundError:
            self.fail('File must be exists')

    def test_start_shell_command_right_format(self):
        try:
            start_shell_command('/etc/issue')
        except OSError:
            self.fail('Exec format error')

    def test_start_shell_command_not_empty_string(self):
        try:
            start_shell_command('')
        except IndexError:
            self.fail('File must be exists')

    def test_start_shell_command_must_permissions(self):
        try:
            start_shell_command('/root')
        except PermissionError:
            self.fail('File must be exists')

    def test_start_shell_command_execution_returns(self):
        self.assertEqual(start_shell_command('echo 123'), '123\n')


"""
    iso.3.6.1.2.1.1.1.0 = Hex-STRING: 41 6C 6C 69 65 64 57 61 72 65 20 50 6C 75 73 20 
    28 54 4D 29 20 32 2E 31 2E 32 CE 20
"""


class CheckHexStringTestCase(TestCase):

    def test_snmp2_module_exists(self):
        try:
            import snmp2
        except ModuleNotFoundError:
            self.fail('Module snmp2 not found')

    def test_check_hex_string_function_exists(self):
        import snmp2
        self.assertTrue(
            hasattr(snmp2, 'check_hex_string')
        )

    def test_check_hex_string_args(self):
        try:
            check_hex_string('string')
        except TypeError:
            self.fail('Function must take one arg')

    def test_check_hex_string_raises_on_invalid_argument_type(self):
        with self.assertRaises(TypeError):
            check_hex_string(None)

    def test_check_hex_string_returns_string_type(self):
        result = check_hex_string('string')
        self.assertIsInstance(result, str)

    def test_check_hex_string_returns_right_value(self):
        arg = 'iso.3.6.1.2.1.1.1.0 = Hex-STRING: 41 6C 6C 69 65 64 57 61 72 65 20 50 6C 75 73 20'
        result = check_hex_string(arg)
        self.assertEqual(result, 'AlliedWare Plus')

    def test_check_hex_string_must_be_hex_value(self):
        arg = 'iso.3.6.1.2.1.1.1.0 = Hex-STRING: x'
        try:
            check_hex_string(arg)
        except ValueError:
            self.fail('arg must be hex value')

    def test_check_hex_string_must_returns_string(self):
        arg = 'Hex-STRING: 41 6C 6C 69 65 64 57 61 72 65 20 50 6C 75 73 20 28 54 4D 29 20 32 2E 31 2E 32 CE 20'
        try:
            check_hex_string(arg)
        except TypeError:
            self.fail('must_returns_string')

    def test_check_hex_string_returns_right_value2(self):
        result = check_hex_string('string')
        self.assertEqual(result, 'string')
