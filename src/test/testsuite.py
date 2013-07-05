from test.testrol import RolTestCase
from test.testproyecto import ProyectoTestCase
from test.testusuario import UsuarioTestCase
from test.testtipoAtributo import TipoATributoTestCase
from test.testpermiso import PermisoTestCase
from test.testfase import FaseTestCase
from test.testmiembroscomite import MiembrosComiteTestCase
from test.testrecurso import RecursoTestCase
from test.testatributo import AtributoTestCase
from test.testtipoitem import TipoItemTestCase
import unittest

def suite():
    suite = unittest.TestSuite()
    suite.addTest(ProyectoTestCase())
    suite.addTest(RolTestCase())
    suite.addTest(UsuarioTestCase())
    suite.addTest(TipoATributoTestCase())
    suite.addTest(PermisoTestCase)
    suite.addTest(FaseTestCase)
    suite.addTest(MiembrosComiteTestCase)
    suite.addTest(RecursoTestCase)
    suite.addTest(AtributoTestCase)
    suite.addTest(TipoItemTestCase)
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    test_suite = suite()
    runner.run (test_suite)