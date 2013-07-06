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
from test.testrol1 import Rol1TestCase
from test.testproyecto1 import Proyecto1TestCase
from test.testusuario1 import Usuario1TestCase
from test.testtipoAtributo1 import TipoATributo1TestCase
from test.testpermiso1 import Permiso1TestCase
from test.testfase1 import Fase1TestCase
from test.testmiembroscomite1 import MiembrosComite1TestCase
from test.testrecurso1 import Recurso1TestCase
from test.testatributo1 import Atributo1TestCase
from test.testtipoitem1 import TipoItem1TestCase
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
    suite.addTest(Proyecto1TestCase())
    suite.addTest(Rol1TestCase())
    suite.addTest(Usuario1TestCase())
    suite.addTest(TipoATributo1TestCase())
    suite.addTest(Permiso1TestCase)
    suite.addTest(Fase1TestCase)
    suite.addTest(MiembrosComite1TestCase)
    suite.addTest(Recurso1TestCase)
    suite.addTest(Atributo1TestCase)
    suite.addTest(TipoItem1TestCase)
    
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    test_suite = suite()
    runner.run (test_suite)