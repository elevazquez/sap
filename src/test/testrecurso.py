from loginC import app

from flask_principal import identity_loaded
from test_helper import login,_on_principal_init, logout, TEST_USER, getRecursoByNombre
import unittest
NOMBRE = 'RECURSOTEST'
PROYECTO = 'None'
FASE = '8'
PATRON = NOMBRE
PARAM = 'nombre'

class RecursoTestCase(unittest.TestCase):
    """Clase que implementa los test para el caso de uso Recurso."""
    
    def setUp(self):
        """se llama al metodo antes de iniciar el test"""        
        self.client = app.test_client()
        self.acceso = login(self.client)
        identity_loaded.connect(_on_principal_init)

    def tearDown(self):
        """ se llama al metodo al terminar el test"""
        self.client = app.test_client()
        self.salir = logout(self.client)

    def test_a_get_all_recurso(self):
        """Prueba que verifica si se puede acceder al listado de recursos"""
        print '##----++++ PRUEBA UNITARIA RECURSO ++++----##'
        print '+++ Obtener todos los recursos +++'
        request = self.client.get('/recurso/administrarrecurso', follow_redirects=True)
        self.assertNotIn('Sin permisos para administrar recursos', request.data, 'No tiene permisos para ver los recursos')
        self.assertEqual(request._status, '200 OK', 'Error al obtener los recursos como '+ TEST_USER)
        print '*-- Obtiene todos los recursos -- request result: ' + request._status + ' --*'
        print'*---test 1 recurso---*'
  
    def test_b_crear_recurso(self):
        """ Prueba de creacion el recurso y verifica si el recurso fue creado"""
        print '+++ Creacion de recurso +++'
        request = self._crear_recurso(NOMBRE, PROYECTO, FASE)
        print '*-- datos de prueba ::: ' + NOMBRE + ', ' + str(PROYECTO) + ', '+ str(FASE) + ' --*'
        self.assertNotIn('Sin permisos para agregar recursos', request.data, 'No tiene permisos para crear recursos')
        self.assertNotIn('Error', request.data, 'Tiene errores el form')
        self.assertIn('El Recurso ha sido registrado con exito', request.data, 'Error al crear el recurso')
        print '*-- request result: ' + request._status + ' --*'
        self.assertIn(NOMBRE, request.data, 'El RECURSO creado no se encuentra en la tabla')
        print '*-- ' + NOMBRE + ' creado correctamente, aparece en la tabla de proyectos--*'
        print '*---test 2 recurso---*'
 
    def test_c_buscar_recurso(self):
        """Prueba de busqueda de un recurso"""
        print '+++ Buscar un recurso existente por nombre +++'
        request = self._buscar_recurso(PATRON, PARAM)
        print '*-- datos de prueba ::: patron = '+ PATRON +', parametro = '+PARAM+' --*'
        self.assertNotIn('Sin permisos para buscar recursos', request.data, 'No tiene permisos para ver los recursos')
        self.assertNotIn('Sin registro de Recursos', request.data, 'No se encontro recursos con dicho parametro')
        self.assertIn(PATRON, request.data, 'El recurso no existe en la tabla')
        print '*-- Recurso encontrado exitosamente --*'
        print '*---test 3 recurso---*'

    def test_d_eliminar_recurso(self):
        """Prueba de verificacion si se puede eliminar un recurso"""
        print '+++ Eliminacion de recurso existente +++'
        recurso = getRecursoByNombre(NOMBRE)
        borrar_request = self._eliminar_recurso(recurso.id)
        print '*-- datos de prueba ::: nombre = ' + NOMBRE +' --*'
        self.assertNotIn('Sin permisos para eliminar recursos', borrar_request.data, 'No tiene permisos para ver los recursos')
        self.assertIn('El recurso ha sido eliminado con exito', borrar_request.data, 'Recurso no existe el nombre del recurso')
        self.assertNotIn(NOMBRE, borrar_request.data, 'El recurso no ha sido borrado')
        print '*-- Verificacion completa, se elimino correctamente--*'
        print '*---test 4 recurso---*'
        print '##----++++ FIN PRUEBA UNITARIA RECURSO ++++----##'
            
    def _get(self, url ='/recurso/administrarrecurso'):
        """obtiene la pagina administrar proyectos """
        return self.client.get(url, follow_redirects=True)
    
    def _crear_recurso(self,nombre=NOMBRE, id_proyecto=PROYECTO, id_fase=FASE):     
        request = self.client.post('/recurso/nuevorecurso', data=dict(
            nombre = nombre,
            id_proyecto = id_proyecto,
            id_fase = id_fase), follow_redirects=True)
        return request
    
    def _buscar_recurso(self, patron = PATRON , parametro = PARAM ):
        request = self.client.get('/recurso/buscarrecurso?patron='+patron+'&parametro='+parametro+'&Buscar=Buscar', follow_redirects=True)
        return request

    def _eliminar_recurso(self, idr=None):     
        request = self.client.post('/recurso/eliminarrecurso?id_recurso='+str(idr), follow_redirects=True)
        return request
        
if __name__ == '__main__':
    unittest.main()