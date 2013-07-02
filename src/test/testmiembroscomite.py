from loginC import app
from flask_principal import identity_loaded
from test_helper import login,_on_principal_initL, logout, TEST_USER_LIDER, seleccionar_proyecto

import unittest
PROYECTOID=23
USU='testdesa'

class MiembrosComiteTestCase(unittest.TestCase):
    """Clase que implementa los test para el caso de uso Miembros Comite."""
   
    def setUp(self):
        """se llama al metodo antes de iniciar el test"""        
        self.client = app.test_client()
        self.acceso = login(self.client)
        identity_loaded.connect(_on_principal_initL)
        self.proyse= seleccionar_proyecto(self.client, PROYECTOID)
        with app.test_client() as c:
            with c.session_transaction() as sess:
                sess['pry'] = PROYECTOID

    def tearDown(self):
        """ se llama al metodo al terminar el test"""
        self.client = app.test_client()
        self.salir = logout(self.client)
    
    def test_a_get_all_miembrosComite(self):
        """Prueba que verifica si se puede acceder al listado de proyectos"""
        print '##----++++ PRUEBA UNITARIA MIEMBROSCOMITE ++++----##'
        print '+++ Obtener todos los miembrosComite +++'
        request = self.client.get('/miembrosComite/administrarmiembrosComite', follow_redirects=True)
        self.assertNotIn('Sin permisos para administrar miembros Comite', request.data, 'No tiene permisos para ver los miembros del comite')
        self.assertEqual(request._status, '200 OK', 'Error al obtener los miembros del comite como '+ TEST_USER_LIDER)
        print '*-- Obtiene todos los miembros del comite -- request result: ' + request._status + ' --*'
        print'*---test 1 miembrosComite---*'
   
    def test_b_crear_miembrosComite(self):     
        """ Prueba de creacion de un miembrosComite y verifica si miembrosComite fue creado"""
        print '+++ Creacion de miembrosComite +++'
        request = self._crear_miembrosComite(USU)
        print '*-- datos de prueba ::: ' + USU +' --*'
        self.assertNotIn('Sin permisos para agregar usuarios', request.data, 'No tiene permisos para crear usuarios')
        self.assertNotIn('Las contrasenhas deben coincidir', request.data, 'Las contrasenhas no coinciden')
        self.assertNotIn('Error', request.data, 'Tiene errores el form')
        self.assertIn('El Usuario ha sido registrado con exito', request.data, 'Error al crear usuario')
        print '*-- request result: ' + request._status + ' --*'
        self.assertIn(USU, request.data, 'El usuario creado no se encuentra en la tabla')
        print '*-- '+ USU +' creado correctamente, aparece en la tabla de usuarios--*'
        print '*---test 2 usuario---*'

    def test_crear_miembrosComite_duplicado(self):
        """prueba si se pueden crear roles duplicados"""
        print '+++ Creacion de rol con nombre repetido +++'
        request = self._crear_rol('rolprueba', 'este es un rol de prueba')
        print '*-- datos de prueba ::: codigo = rolprueba, descripcion = este es un rol de prueba --*'
        self.assertIn('Clave unica violada por favor ingrese otro CODIGO de Rol', request.data, 'Rol creado, no existe el codigo de rol')
        print '*-- Verificacion completa, no se pueden crear dos roles con el mismo nombre --*'
        print '*---test 3 rol---*'
        
    def test_editar_miembrosComite(self):
        """  edita un rol    """        
        print '+++ Editar rol existente +++'
        request = self._editar_rol('rolprueba', 'este es un rol de prueba editado')   
        print '*-- datos de prueba ::: codigo = rolprueba, descripcion = este es un rol de prueba editado --*'
        self.assertIn('El rol ha sido modificado con exito', request.data, 'Error al modificar rol')  
        self.assertIn('este es un rol de prueba editado',request.data,'El rol no se encuentra editado en la tabla')
        print 'Rol editado correctamente'
        print '*---test 4 rol---*'

    def test_eliminar_miembrosComite(self):
        """verifica si se puede eliminar un rol   """
        print '+++ Eliminacion de rol existente +++'
        borrar_request = self._eliminar_rol('rolprueba')
        print '*-- datos de prueba ::: codigo = rolprueba --*'
        self.assertIn('El rol ha sido eliminado con exito', borrar_request.data, 'Rol creado, no existe el codigo de rol')
        self.assertNotIn('rolprueba', borrar_request.data, 'El rol no ha sido borrado')
        print '*-- Verificacion completa, se elimino correctamente--*'
        print '*---test 5 rol---*'
           
    def _crear_miembrosComite(self, codigo='rolprueba', descripcion='este es un rol de prueba'):     
        request = self.client.post('/add', data=dict(
           codigo=codigo,
           descripcion=descripcion), follow_redirects=True)
        return request
   
    def _editar_miembrosComite(self, codigo='rolprueba', descripcion='este es un rol de prueba editado'):     
        request = self.client.post('/editar', data=dict(
           codigo=codigo,
           descripcion=descripcion), follow_redirects=True)
        return request

    def _eliminar_miembrosComite(self, codigo='rolprueba'):     
        request = self.client.post('/eliminar?cod='+codigo, follow_redirects=True)
        return request
   
    def _get(self, url ='/administrarrol'):
        """obtiene la pagina administrar roles """
        return self.client.get(url, follow_redirects=True)
    
if __name__ == '__main__':
    unittest.main()