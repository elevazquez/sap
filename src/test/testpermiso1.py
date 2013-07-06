from loginC import app

from flask_principal import identity_loaded
from test_helper import login,_on_principal_init, logout, TEST_USER
import unittest

RECURSOID = 10
COD = 'testPermiso' 
DES = 'test permiso des'
PATRON = 'test'
PARAM = 'codigo'

class Permiso1TestCase(unittest.TestCase):
    """Clase que implementa los test para el caso de uso permisos."""   
        
    def setUp(self):
        """se llama al metodo antes de iniciar el test"""        
        self.client = app.test_client()
        self.acceso = login(self.client)
        identity_loaded.connect(_on_principal_init)

    def tearDown(self):
        """ se llama al metodo al terminar el test"""
        self.client = app.test_client()
        self.salir = logout(self.client)

    def test_a_get_all_permisos(self):
        """verifica si se puede acceder al listado de roles """
        print '##----++++ PRUEBA UNITARIA PERMISO ++++----##'
        print '+++ Obtener todos los permisos +++'
        request = self.client.get('/permiso/administrarpermiso', follow_redirects=True)
        self.assertNotIn('Sin permisos para administrar proyectos', request.data, 'No tiene permisos para ver los permisos')
        self.assertEqual(request._status, '200 OK', 'Error al obtener los permisos como '+ TEST_USER)
        print '*-- Obtiene todos los usuarios -- request result: ' + request._status + ' --*'
        print'*---test 1 permiso---*'

    def test_b_crear_permiso(self):
        """crea el permiso y verifica si el permiso fue creado"""
        print '+++ Creacion de usuario +++'
        request = self._crear_permiso(COD, DES, RECURSOID)
        print '*-- datos de prueba ::: ' + COD + ', ' + DES + ', ' + str(RECURSOID) +' --*'
        self.assertNotIn('Sin permisos para agregar permisos', request.data, 'No tiene permisos para crear permisos')
        self.assertNotIn('Error', request.data, 'Tiene errores el form')
        self.assertIn('El permiso ha sido registrado con exito', request.data, 'Error al crear permiso')
        print '*-- request result: ' + request._status + ' --*'
        self.assertIn(COD, request.data, 'El usuario creado no se encuentra en la tabla')
        print '*-- '+ COD +' creado correctamente, aparece en la tabla de permisos--*'
        print '*---test 2 permiso---*'

    def test_c_crear_permiso_duplicado(self):
        """prueba si se pueden crear permisos duplicados"""
        print '+++ Creacion de usuario +++'
        request = self._crear_permiso(COD, DES, RECURSOID)
        print '*-- datos de prueba ::: ' + COD + ', ' + DES + ', ' + str(RECURSOID) +' --*'
        self.assertNotIn('Sin permisos para agregar permisos', request.data, 'No tiene permisos para crear permisos')
        self.assertIn('Clave unica violada por favor ingrese otra combinacion de permiso con recurso unica', request.data, 'Permiso creado, no existe la combinacion codigo, recurso del nuevo permiso')
        print '*-- Verificacion completa, no se pueden crear dos permisos con la misma combinacion --*'
        print '*---test 3 permiso---*'
        
    def test_d_buscar_permiso(self):
        """Prueba de busqueda de un permiso"""
        print '+++ Buscar un permiso existente por codigo+++'
        request = self._buscar_permiso(PATRON, PARAM)
        print '*-- datos de prueba ::: patron = '+ PATRON +', parametro = '+PARAM+' --*'
        self.assertNotIn('Sin permisos para buscar permisos', request.data, 'No tiene permisos para ver los permisos')
        self.assertNotIn('Sin registro de permisos', request.data, 'No se encontro un permiso con dicho parametro')
        self.assertIn(PATRON, request.data, 'El permisos no existe en la tabla')
        print '*-- Permiso encontrado exitosamente --*'
        print '*---test 4 permiso---*'
        
    def test_e_editar_permiso(self):
        """Prueba de edicion de un permiso"""        
        print '+++ Editar permiso existente +++'
        request = self._editar_permiso(COD, 'test permiso modificado', RECURSOID)
        print '*-- datos de prueba ::: ' + COD + ', test permiso modificado, ' + str(RECURSOID) +' --*'
        self.assertNotIn('Sin permisos para modificar permisos', request.data, 'No tiene permisos para editar permisos')
        self.assertIn('El permiso ha sido modificado con exito', request.data, 'Error al modificar usuario')  
        self.assertIn('test permiso modificado',request.data,'El permiso no se encuentra editado en la tabla')
        print '*-- Permiso editado correctamente --*'
        print '*---test 5 permiso---*'

    def test_f_eliminar_permiso(self):
        """Prueba de verificacion si se puede eliminar un permiso"""
        print '+++ Eliminacion de permiso existente +++'
        borrar_request = self._eliminar_permiso(COD)
        print '*-- datos de prueba ::: codigo = ' + COD +' --*'
        self.assertNotIn('Sin permisos para eliminar permisos', borrar_request.data, 'No tiene permisos eliminar permisos')
        self.assertIn('El permiso ha sido eliminado con exito', borrar_request.data, 'Permiso creado, no existe el codigo del permiso')
        self.assertNotIn(COD, borrar_request.data, 'El permiso no ha sido borrado')
        print '*-- Verificacion completa, se elimino correctamente--*'
        print '*---test 6 permiso---*'
        print '##----++++ FIN PRUEBA UNITARIA PERMISO ++++----##'

    def _get(self, url ='/permiso/administrarpermiso'):
        """obtiene la pagina administrar permisos """
        return self.client.get(url, follow_redirects=True)
            
    def _crear_permiso(self, codigo=COD, descripcion=DES, id_recurso=RECURSOID):     
        request = self.client.post('/permiso/nuevopermiso', data=dict(
            codigo = codigo,
            descripcion = descripcion, 
            id_recurso = id_recurso), follow_redirects=True)
        return request
    
    def _buscar_permiso(self, patron = PATRON , parametro = PARAM ):
        request = self.client.get('/permiso/buscarpermiso?patron='+patron+'&parametro='+parametro+'&Buscar=Buscar', follow_redirects=True)
        return request
    
    def _editar_permiso(self, codigo=COD, descripcion=DES, id_recurso=RECURSOID):     
        request = self.client.post('/permiso/editarpermiso', data=dict(
            codigo = codigo,
            descripcion = descripcion, 
            id_recurso = id_recurso), follow_redirects=True)
        return request

    def _eliminar_permiso(self, codigo=COD):     
        request = self.client.post('/permiso/eliminarpermiso?codigo='+codigo, follow_redirects=True)
        return request    
        
if __name__ == '__main__':
    unittest.main()