from unittest import TestCase

"""
    iso.3.6.1.2.1.1.1.0 = Hex-STRING: 41 6C 6C 69 65 64 57 61 72 65 20 50 6C 75 73 20 
    28 54 4D 29 20 32 2E 31 2E 32 CE 20
"""


class SnmpTestCase(TestCase):

    def test_snmp2_module_exists(self):
        try:
            import snmp2
        except ModuleNotFoundError:
            self.fail('Module snmp2 not found')

    def test_check_hex_string_exists(self):
        import snmp2
        self.assertTrue(
            hasattr(snmp2, 'check_hex_string')
        )

    def test_check_hex_string_args(self):
        from snmp2 import check_hex_string
        try:
            check_hex_string('string')
        except TypeError:
            self.fail('Function must take one arg')

    def test_check_hex_string_raises_on_invalid_argument_type(self):
        from snmp2 import check_hex_string
        with self.assertRaises(TypeError):
            check_hex_string(None)

    def test_check_hex_string_returns_string_type(self):
        from snmp2 import check_hex_string
        result = check_hex_string('string')
        self.assertIsInstance(result, str)

    def test_check_hex_string_returns_right_value(self):
        from snmp2 import check_hex_string
        arg = 'iso.3.6.1.2.1.1.1.0 = Hex-STRING: 41 6C 6C 69 65 64 57 61 72 65 20 50 6C 75 73 20'
        result = check_hex_string(arg)
        self.assertEqual(result, 'AlliedWare Plus')

    def test_check_hex_string_must_be_hex_value(self):
        from snmp2 import check_hex_string
        arg = 'iso.3.6.1.2.1.1.1.0 = Hex-STRING: x'
        try:
            check_hex_string(arg)
        except ValueError:
            self.fail('arg must be hex value')

    def test_check_hex_string_must_returns_string(self):
        pass
        from snmp2 import check_hex_string
        arg = 'Hex-STRING: 41 6C 6C 69 65 64 57 61 72 65 20 50 6C 75 73 20 28 54 4D 29 20 32 2E 31 2E 32 CE 20'
        try:
            check_hex_string(arg)
        except TypeError:
            self.fail('must_returns_string')

    def test_check_hex_string_returns_right_value2(self):
        from snmp2 import check_hex_string
        result = check_hex_string('string')
        self.assertEqual(result, 'string')
