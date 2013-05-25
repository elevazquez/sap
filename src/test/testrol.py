import unittest
from loginC import app

from test_helper import login
from UserPermission import UserRol
from flask import Flask, Response

from flask_principal import Principal, Permission, Denial, RoleNeed, \
    PermissionDenied, identity_changed, Identity, identity_loaded

anon_permission = Permission()
admin_permission = Permission(RoleNeed('ADMINISTRADOR'))
admin_or_editor = Permission(RoleNeed('ADMINISTRADOR'), RoleNeed('ADMINISTRADOR'))
editor_permission = Permission(RoleNeed('ADMINISTRADOR'))
admin_denied = Denial(RoleNeed('ADMINISTRADOR'))

def _on_principal_init(sender, identity):
        if identity.id == 'admin':
            identity.provides.add(RoleNeed('ADMINISTRADOR'))
            identity.provides.add(UserRol('ADMINISTRADOR'))


class RolTestCase(unittest.TestCase):
    """Clase que implementa los test para el caso de uso Rol."""
   
        
    def setUp(self):
        """se llama al metodo antes de iniciar el test"""        
        print "Iniciando test"
        self.app = app.test_client()
        self.acceso = login(self.app)
        identity_loaded.connect(_on_principal_init)

    def tearDown(self):
        """ se llama al metodo al terminar el test"""
        print "Terminando test"


    def test_get_all_roles(self):
        """verifica si se puede acceder al listado de roles """
        request = self.app.get('/administrarrol', follow_redirects=True)
        print "preueba "+request.data
        assert 'sin permisos' in request.data
        print "No posee permisos"
        
        
    def test_get_all_roles2(self):
        """verifica si se puede acceder al listado de roles """
        request = self.app.get('/administrarrol', follow_redirects=True)
        print "preueba2 "+request.data
        assert 'ADMINISTRADOR' in request.data
        self.assertEqual(request._status, '200 OK')
   
   
    def test_crear_rol(self):
        """  crea el rol y verifica si el rol fue creado     """        
        print "Probando crear un rol"
        request = self._crear_rol('rolprueba', 'este es un rol de prueba')     
        print "Respuesta satisfactoria, verificando si creo el rol"
        request_all = self.app.get('/administrarrol', follow_redirects=True)
        assert 'rolprueba' in request_all.data
        print "Rol creado correctamente"


    def test_crear_rol_duplicado(self):
        """prueba si se pueden crear roles duplicados    """
        #Ahora probamos vovler a crear
        print "Creacion de rol con nombre repetido"
        request = self._crear_rol('rolprueba', 'este es un rol de prueba')
        print "Respuesta satisfactoria, verificando si dejo crear el rol"
        assert 'Clave unica violada por favor ingrese otro CODIGO de Rol' in request.data
        print "Verificacion completa, no se pueden crear dos roles con el mismo nombre"


#    def test_eliminar_rol(self):
#        """verifica si se puede eliminar un rol   """
#        print "Creando rol con nombre 'rolprueba2'."
#        crear_request = self._crear_rol('rolprueba2', 'borrar')
#        print "Verificando si se creo el rol"
#        all_request = self._get()
#        assert 'rolprueba2' in all_request.data
#        print "Rol creado exitosamente"        
#        borrar_request = self._eliminar_rol('rolprueba2', 'borrar')
#        print "verificar si se elimino"
#        request_all = self._get() #self.app.get('/administrarrol', follow_redirects=True)
#        assert 'rolprueba2' not in  request_all.data
#        self.assertEqual(request_all._status, '200 OK')
#        print "verificacion completa, se elimino"
        
        
    def test_editar_rol(self):
        """  edita un rol    """        
        print "Probando editar rol"
        request = self._editar_rol('rolprueba', 'este es un rol de prueba editado')     
        print "Respuesta satisfactoria, verificando si se edito el rol"
        request_all = self.app.get('/administrarrol', follow_redirects=True)
        assert 'rolprueba' in request_all.data
        print "Rol editado correctamente"

            
    def _crear_rol(self, codigo='rolprueba', descripcion='este es un rol de prueba'):     
        request = self.app.post('/add', data=dict(
            codigo=codigo,
            descripcion=descripcion), follow_redirects=True)
        return request
    
    def _editar_rol(self, codigo='rolprueba', descripcion='este es un rol de prueba editado'):     
        request = self.app.post('/editar', data=dict(
            codigo=codigo,
            descripcion=descripcion), follow_redirects=True)
        return request

#    def _eliminar_rol(self, codigo='rolprueba2', descripcion='borrar'):     
#        request = self.app.post('/eliminar', data=dict(
#            codigo=codigo, descripcion=descripcion), follow_redirects=True)
#        return request
    
    def _get(self, url ='/administrarrol'):
        """obtiene la pagina administrar roles """
        return self.app.get(url, follow_redirects=True)
    

        
if __name__ == '__main__':
    unittest.main()