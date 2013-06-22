from test.testrol import RolTestCase
from test.testproyecto import ProyectoTestCase
from test.testusuario import UsuarioTestCase
from test.testtipoAtributo import TipoATributoTestCase
from test.testpermiso import PermisoTestCase
import unittest

def suite_2():
    suite = unittest.TestSuite()
    suite.addTest(ProyectoTestCase())
    suite.addTest(RolTestCase())
    suite.addTest(UsuarioTestCase())
    suite.addTest(TipoATributoTestCase())
    suite.addTest(PermisoTestCase)
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    test_suite = suite_2()
    runner.run (test_suite)