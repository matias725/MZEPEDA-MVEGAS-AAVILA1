import unittest
from validaciones import validar_email, validar_fecha_iso, validar_horas, validar_no_vacio


class TestValidaciones(unittest.TestCase):
    def test_validar_email(self):
        self.assertTrue(validar_email('usuario@example.com'))
        self.assertFalse(validar_email('usuario@@example'))
        self.assertFalse(validar_email(''))

    def test_validar_fecha_iso(self):
        self.assertTrue(validar_fecha_iso('2025-12-02'))
        self.assertFalse(validar_fecha_iso('02-12-2025'))
        self.assertFalse(validar_fecha_iso('2025/12/02'))

    def test_validar_horas(self):
        self.assertTrue(validar_horas('8'))
        self.assertTrue(validar_horas(7.5))
        self.assertFalse(validar_horas('0'))
        self.assertFalse(validar_horas('25'))
        self.assertFalse(validar_horas('abc'))

    def test_validar_no_vacio(self):
        self.assertTrue(validar_no_vacio('hola'))
        self.assertFalse(validar_no_vacio('   '))
        self.assertFalse(validar_no_vacio(''))


if __name__ == '__main__':
    unittest.main()
