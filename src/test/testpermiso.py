import unittest
from loginC import app

from test_helper import login

class PermisoTestCase(unittest.TestCase):
    """Clase que implementa los test para el caso de uso permisos."""
   
        
    def setUp(self):
        """se llama al metodo antes de iniciar el test"""        
        print "Iniciando test"
        self.app = app.test_client()
        self.acceso = login(self.app)

    def tearDown(self):
        """ se llama al metodo al terminar el test"""
        print "Terminando test"


    def test_get_all_permisos(self):
        """verifica si se puede acceder al listado de roles """
        request = self.app.get('/permiso/administrarpermiso', follow_redirects=True)
        print "preueba "+request.data
        assert 'sin permisos' in request.data
        print "No posee permisos"
        
        
    def test_get_all_permisos2(self):
        """verifica si se puede acceder al listado de roles """
        request = self.app.get('/permiso/administrarpermiso', follow_redirects=True)
        print "preueba2 "+request.data
        assert 'ADMINISTRADOR' in request.data
        self.assertEqual(request._status, '200 OK')
   
   
    def test_crear_permiso(self):
        """  crea el rol y verifica si el rol fue creado     """  
        request = self._crear_permiso('testperm', 'test permiso des',1)   
        print "Respuesta satisfactoria, verificando si creo el permiso"
        request_all = self.app.get('/permiso/administrarpermiso', follow_redirects=True)
        assert 'El permiso ha sido registrado con exito' in request_all.data


    def test_crear_permiso_duplicado(self):
        """prueba si se pueden crear roles duplicados    """
        #Ahora probamos vovler a crear
        print "Creacion de rol con nombre repetido"
        request = self._crear_rol('testperm', 'test permiso des',1) 
        print "Respuesta satisfactoria, verificando si dejo crear el permiso"
        assert 'Clave unica violada por favor ingrese otro CODIGO de Permiso' in request.data


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
#        request_all = self._get() #self.app.get('/permiso/administrarpermiso', follow_redirects=True)
#        assert 'rolprueba2' not in  request_all.data
#        self.assertEqual(request_all._status, '200 OK')
#        print "verificacion completa, se elimino"
        
        
    def test_editar_permiso(self):
        """  edita un rol    """        
        print "Probando editar rol"
        request = self._editar_permiso('testperm', 'test permiso des edit',1)    
        print "Respuesta satisfactoria, verificando si se edito el rol"
        request_all = self.app.get('/permiso/administrarpermiso', follow_redirects=True)
        assert 'test permiso des edit' in request_all.data

            
    def _crear_permiso(self, codigo='testperm', descripcion='test permiso des', id_fase=1):     
        request = self.app.post('/permiso/nuevopermiso', data=dict(
            codigo = codigo,
            descripcion = descripcion, 
            id_fase = id_fase), follow_redirects=True)
        return request
    
    def _editar_permiso(self, codigo='testperm', descripcion='test permiso des edit', id_fase=1):     
        request = self.app.post('/permiso/editarpermiso', data=dict(
            codigo = codigo,
            descripcion = descripcion, 
            id_fase = id_fase), follow_redirects=True)
        return request

#    def _eliminar_rol(self, codigo='rolprueba2', descripcion='borrar'):     
#        request = self.app.post('/eliminar', data=dict(
#            codigo=codigo, descripcion=descripcion), follow_redirects=True)
#        return request
    
    def _get(self, url ='/permiso/administrarpermiso'):
        """obtiene la pagina administrar permisos """
        return self.app.get(url, follow_redirects=True)
    

        
if __name__ == '__main__':
    unittest.main()