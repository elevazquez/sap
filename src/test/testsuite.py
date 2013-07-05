from test.testrol import RolTestCase
from test.testproyecto import ProyectoTestCase
from test.testusuario import UsuarioTestCase
from test.testtipoAtributo import TipoATributoTestCase
from test.testpermiso import PermisoTestCase
from test.testfase import FaseTestCase
from test.testmiembroscomite import MiembrosComiteTestCase
from test.testrecurso import RecursoTestCase
import unittest

def suite_2():
    suite = unittest.TestSuite()
    suite.addTest(ProyectoTestCase())
    suite.addTest(RolTestCase())
    suite.addTest(UsuarioTestCase())
    suite.addTest(TipoATributoTestCase())
    suite.addTest(PermisoTestCase)
    suite.addTest(FaseTestCase)
    suite.addTest(MiembrosComiteTestCase)
    suite.addTest(RecursoTestCase)
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    test_suite = suite_2()
    runner.run (test_suite)