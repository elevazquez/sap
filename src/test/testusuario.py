import unittest
from loginC import app

from test_helper import login


class UsuarioTestCase(unittest.TestCase):
    """Clase que implementa los test para el caso de uso Usuario."""
    
    def setUp(self):
        """se llama al metodo antes de iniciar el test"""        
        print "Iniciando test"
        self.app = app.test_client()
        self.acceso = login(self.app)

    def tearDown(self):
        """ se llama al metodo al terminar el test"""
        print "Terminando test"


    def test_get_all_roles(self):
        """verifica si se puede acceder al listado de usuarios """
        request = self.app.get('/usuario/administrarusuario', follow_redirects=True)
        assert 'raquel' in request.data
        self.assertEqual(request._status, '200 OK')
   
   
    def test_crear_usuario(self):
        """  crea el usuario y verifica si el usuario fue creado   """        
        print "Probando crear un usuario"
        request = self._crear_usuario('unittest','usuarioTest','usuarioTestApp','123', 'user@test.com', 
                 'test', '123456')    
        print "Respuesta satisfactoria, verificando si creo el usuario"
        request_all = self.app.get('/usuario/administrarusuario', follow_redirects=True)
        assert 'unittest' in request_all.data
        print "Usuario creado correctamente"


    def test_crear_usuario_duplicado(self):
        """prueba si se pueden crear usuarios duplicados    """
        #Ahora probamos vovler a crear
        print "Creacion de usuarios con usuario repetido"
        request = self._crear_usuario('unittest', 'usuarioTest', 'usuarioTestApp', '123', 'user@test.com', 
                 'test', '123456','14-02-2003') 
        print "Respuesta satisfactoria, verificando si dejo crear el usuario"
        assert 'Clave unica violada por favor ingrese otro USUARIO para el registro' in request.data
        print "Verificacion completa, no se pueden crear dos usuarios con el mismo usuario"


#    def test_eliminar_usuario(self):
#        """verifica si se puede eliminar un usuario   """
#        print "Creando usuario con usuario 'unittest2'."
#        crear_request = self._crear_usuario(usuario='unittest2', nombre='usuarioTest', apellido='usuarioTestApp', password='123', correo='user@test.com', 
#                 domicilio='test', telefono='123456', fecha_nac='14-02-2003')  
#        print "Verificando si se creo el usuario"
#        all_request = self._get()
#        assert 'unittest2' in all_request.data
#        print "Usuario creado exitosamente"        
#        borrar_request = self._eliminar_usuario(usuario='unittest2', nombre='usuarioTest', apellido='usuarioTestApp', password='123', correo='user@test.com', 
#                 domicilio='test', telefono='123456', fecha_nac='14-02-2003')  
#        print "verificar si se elimino"
#        request_all = self._get() #self.app.get('/administrarrol', follow_redirects=True)
#        assert 'unittest2' not in  request_all.data
#        self.assertEqual(request_all._status, '200 OK')
#        print "verificacion completa, se elimino"
        
        
    def test_editar_usuario(self):
        """  edita un usuario    """        
        print "Probando editar usuario"
        request = self._editar_usuario('unittest', 'usuarioTestmod', 'usuarioTestApp', '123', 'user@test.com', 
                 'testmodificado', '123456')  
        print "Respuesta satisfactoria, verificando si se edito el usuario"
        request_all = self.app.get('/usuario/administrarusuario', follow_redirects=True)
        assert 'unittest' in request_all.data
        print "Usuario editado correctamente"

            
    def _crear_usuario(self,usuario='unittest', nombre='usuarioTest', apellido='usuarioTestApp', password='123', correo='user@test.com', 
                 domicilio='test', telefono='123456'):     
        request = self.app.post('/usuario/nuevousuario', data=dict(
            usuario = usuario,
            nombre = nombre,
            apellido = apellido,
            password = password,
            correo = correo,
            domicilio = domicilio,
            telefono = telefono), follow_redirects=True)
        return request
    
    def _editar_usuario(self, usuario='unittest', nombre='usuarioTesteditado', apellido='usuarioTestApp', password='123', correo='user@test.com', 
                 domicilio='test', telefono='123456'):     
        request = self.app.post('/usuario/editarusuario', data=dict(
            usuario = usuario,
            nombre = nombre,
            apellido = apellido,
            password = password,
            correo = correo,
            domicilio = domicilio,
            telefono = telefono), follow_redirects=True)
        return request

#    def _eliminar_usuario(self, usuario='unittest2', nombre='usuarioTesteditado', apellido='usuarioTestApp', password='123', correo='user@test.com', 
#                 domicilio='test', telefono='123456', fecha_nac='14-02-2003'):     
#        request = self.app.post('/usuario/eliminarusuario', data=dict(
#            usuario = usuario,
#            nombre = nombre,
#            apellido = apellido,
#            password = password,
#            correo = correo,
#            domicilio = domicilio,
#            telefono = telefono,
#            fecha_nac = fecha_nac), follow_redirects=True)
#        return request
    
    def _get(self, url ='/usuario/administrarusuario'):
        """obtiene la pagina administrar usuarios """
        return self.app.get(url, follow_redirects=True)
    

        
if __name__ == '__main__':
    unittest.main()