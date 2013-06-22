from loginC import app
from flask_principal import identity_loaded
from test_helper import login,_on_principal_init, logout, TEST_USER

import unittest

#falta asignar y eliminar permiso usuario

class RolTestCase(unittest.TestCase):
    """Clase que implementa los test para el caso de uso Rol."""
        
    def setUp(self):
        """se llama al metodo antes de iniciar el test"""        
        self.client = app.test_client()
        self.acceso = login(self.client)
        identity_loaded.connect(_on_principal_init)

    def tearDown(self):
        """ se llama al metodo al terminar el test"""
        self.client = app.test_client()
        self.salir = logout(self.client)
    #===========================================================================
    # def test_get_all_roles(self):
    #    """verifica si se puede acceder al listado de roles """
    #    request = self.client.get('/administrarrol', follow_redirects=True)
    #    print "preueba "+request.data
    #    assert 'sin permisos' in request.data
    #    print "No posee permisos"
    #===========================================================================
        
    def test_a_get_all_roles(self):
        """Prueba de verificacion si se puede acceder al listado de roles"""
        print '##----++++ PRUEBA UNITARIA ROL ++++----##'
        print '+++ Obtener todos los roles +++'
        request = self.client.get('/administrarrol', follow_redirects=True)
        self.assertNotIn('Sin permisos para administrar roles', request.data, 'No tiene permisos para ver los roles')
        self.assertEqual(request._status, '200 OK', 'Error al obtener roles como '+ TEST_USER)
        print '*-- Obtiene todos los roles -- request result: ' + request._status + ' --*'
        print'*---test 1 rol---*'
   
    def test_b_crear_rol(self):
        """ Prueba de creacion el rol y verifica si el rol fue creado"""
        print '+++ Creacion de rol +++'
        request = self._crear_rol('rolprueba', 'este es un rol de prueba')
        print '*-- datos de prueba ::: codigo = rolprueba, descripcion = este es un rol de prueba --*'
        self.assertNotIn('Sin permisos para agregar roles', request.data, 'No tiene permisos para crear roles')
        self.assertIn('El rol ha sido registrado con exito', request.data, 'Error al crear el rol')
        print '*-- request result: ' + request._status + ' --*'
        self.assertIn('rolprueba', request.data, 'El rol creado no se encuentra en la tabla')
        print '*-- Rol creado correctamente, aparece en la tabla de roles --*'
        print '*---test 2 rol---*'

    def test_c_crear_rol_duplicado(self):
        """Prueba si se pueden crear roles duplicados"""
        print '+++ Creacion de rol con nombre repetido +++'
        request = self._crear_rol('rolprueba', 'este es un rol de prueba')
        print '*-- datos de prueba ::: codigo = rolprueba, descripcion = este es un rol de prueba --*'
        self.assertNotIn('Sin permisos para agregar roles', request.data, 'No tiene permisos para crear roles')
        self.assertIn('Clave unica violada por favor ingrese otro CODIGO de Rol', request.data, 'Rol creado, no existe el codigo de rol')
        print '*-- Verificacion completa, no se pueden crear dos roles con el mismo nombre --*'
        print '*---test 3 rol---*'
        
    def test_d_buscar_rol(self):
        """Prueba de busqueda de un rol"""
        print '+++ Buscar un rol existente por codigo +++'
        request = self._buscar_rol('rolprueba', 'codigo')
        print '*-- datos de prueba ::: patron = rolprueba, parametro = codigo --*'
        self.assertNotIn('Sin permisos para buscar roles', request.data, 'No tiene permisos para buscar roles')
        self.assertNotIn('Sin registro de roles', request.data, 'No se encontro roles con dicho parametro')
        self.assertIn('rolprueba', request.data, 'El rol no existe en la tabla')
        print '*-- Rol encontrado exitosamente --*'
        print '*---test 4 rol---*'
        
    def test_e_editar_rol(self):
        """Prueba de edicion de un rol    """        
        print '+++ Editar rol existente +++'
        request = self._editar_rol('rolprueba', 'este es un rol de prueba editado')
        print '*-- datos de prueba ::: codigo = rolprueba, descripcion = este es un rol de prueba editado --*'
        self.assertNotIn('Sin permisos para editar roles', request.data, 'No tiene permisos para editar los roles')
        self.assertIn('El rol ha sido modificado con exito', request.data, 'Error al modificar rol')  
        self.assertIn('este es un rol de prueba editado',request.data,'El rol no se encuentra editado en la tabla')
        print '*-- Rol editado correctamente --*'
        print '*---test 5 rol---*'

    def test_f_eliminar_rol(self):
        """Prueba de verificacion si se puede eliminar un rol"""
        print '+++ Eliminacion de rol existente +++'
        borrar_request = self._eliminar_rol('rolprueba')
        print '*-- datos de prueba ::: codigo = rolprueba --*'
        self.assertNotIn('Sin permisos para eliminar roles', borrar_request.data, 'No tiene permisos para eliminar roles')
        self.assertIn('El rol ha sido eliminado con exito', borrar_request.data, 'Rol creado, no existe el codigo de rol')
        self.assertNotIn('rolprueba', borrar_request.data, 'El rol no ha sido borrado')
        print '*-- Verificacion completa, se elimino correctamente--*'
        print '*---test 6 rol---*'
        print '##----++++ FIN PRUEBA UNITARIA ROL ++++----##'
        
    def test_g_asignar_rol(self):
        """Prueba para asignar un permiso al rol"""
        
            
    def _get(self, url ='/administrarrol'):
        """obtiene la pagina administrar roles """
        return self.client.get(url, follow_redirects=True)
    
    def _crear_rol(self, codigo='rolprueba', descripcion='este es un rol de prueba'):     
        request = self.client.post('/add', data=dict(
           codigo=codigo,
           descripcion=descripcion), follow_redirects=True)
        return request
   
    def _buscar_rol(self, patron = 'rolprueba', parametro = 'codigo'):
        request = self.client.get('/buscar?patron='+patron+'&parametro='+parametro+'&Buscar=Buscar', follow_redirects=True)
        return request
    
    def _editar_rol(self, codigo='rolprueba', descripcion='este es un rol de prueba editado'):     
        request = self.client.post('/editar', data=dict(
           codigo=codigo,
           descripcion=descripcion), follow_redirects=True)
        return request

    def _eliminar_rol(self, codigo='rolprueba'):     
        request = self.client.post('/eliminar?cod='+codigo, follow_redirects=True)
        return request
        
if __name__ == '__main__':
    unittest.main()
