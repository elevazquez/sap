import unittest
from loginC import app

from test_helper import login


class   TipoATributoTestCase(unittest.TestCase):
    """Clase que implementa los test para el caso de uso Tipo Atributo."""
    
    def setUp(self):
        """se llama al metodo antes de iniciar el test"""        
        print "Iniciando test"
        self.app = app.test_client()
        self.acceso = login(self.app)

    def tearDown(self):
        """ se llama al metodo al terminar el test"""
        print "Terminando test"


    def test_get_all_Tipos(self):
        """verifica si se puede acceder al listado de tipos de atributos """
        request = self.app.get('/tipoAtributo/administrartipoAtributo', follow_redirects=True)
        assert 'BOOLEAN' in request.data
        self.assertEqual(request._status, '200 OK')
   
   
    def test_crear_tipoatt(self):
        """  crea el proyecto y verifica si el tipo de atri. fue creado     """        
        print "Probando crear un tipo de att"
        request = self._crear_tipoatt('test', 'testdesc' )     
        print "Respuesta satisfactoria, verificando si creo el tipo de att"
        request_all = self.app.get('/tipoAtributo/administrartipoAtributo', follow_redirects=True)
        assert 'test' in request_all.data
        print "tipo att creado correctamente"


    def test_crear_tipoatt_duplicado(self):
        """prueba si se pueden crear tipo att duplicados    """
        #Ahora probamos vovler a crear
        print "Creacion de tipo att con nombre repetido"
        request = self._crear_tipoatt('test', 'testdesc' )    
        print "Respuesta satisfactoria, verificando si dejo crear el tipo att"
        assert 'Clave unica violada por favor ingrese otro CODIGO para el Tipo de Atributo' in request.data
        print "Clave unica violada por favor ingrese otro CODIGO para el Tipo de Atributo"


#    def test_eliminar_proyecto(self):
#        """verifica si se puede eliminar un proyecto  """
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
        
        
    def test_editar_tipoatt(self):
        """  edita un tipo att    """        
        print "Probando editar tipoatt"
        request = self._editar_tipoatt('test', 'testdescedit')   
        print "Respuesta satisfactoria, verificando si se edito el tipo att"
        request_all = self.app.get('/tipoAtributo/administrartipoAtributo', follow_redirects=True)
        assert 'test' in request_all.data
        print "tipoatt editado correctamente"

            
    def _crear_tipoatt(self,nombre='test', descripcion='testdesc'):     
        request = self.app.post('/tipoAtributo/nuevotipoAtributo', data=dict(
            nombre = nombre,
            descripcion = descripcion), follow_redirects=True)
        return request
    
    def _editar_tipoatt(self, nombre='test', descripcion='testdesc'):     
        request = self.app.post('/tipoAtributo/editartipoAtributo', data=dict(
            cnombre = nombre,
            descripcion = descripcion), follow_redirects=True)
        return request

#    def _eliminar_proyecto(self, codigo='rolprueba2', descripcion='borrar'):     
#        request = self.app.post('/eliminar', data=dict(
#            codigo=codigo, descripcion=descripcion), follow_redirects=True)
#        return request
    
    def _get(self, url ='/tipoAtributo/administrartipoAtributo'):
        """obtiene la pagina administrar tipo att """
        return self.app.get(url, follow_redirects=True)
    

        
if __name__ == '__main__':
    unittest.main()