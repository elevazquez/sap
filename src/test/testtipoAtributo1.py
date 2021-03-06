from loginC import app

from flask_principal import identity_loaded
from test_helper import login,_on_principal_initL, logout, TEST_USER_LIDER, TEST_PASS_LIDER
import unittest
from test.test_helper import seleccionar_proyecto

PROYECTOID = 23

class TipoATributo1TestCase(unittest.TestCase):
    """Clase que implementa los test para el caso de uso Tipo Atributo."""
    
    def setUp(self):
        """se llama al metodo antes de iniciar el test"""        
        self.client = app.test_client()
        self.acceso = login(self.client, TEST_USER_LIDER, TEST_PASS_LIDER)
        identity_loaded.connect(_on_principal_initL)
        self.proyse= seleccionar_proyecto(self.client, PROYECTOID)
        with app.test_client() as c:
            with c.session_transaction() as sess:
                sess['pry'] = PROYECTOID

    def tearDown(self):
        """ se llama al metodo al terminar el test"""
        self.client = app.test_client()
        self.salir = logout(self.client)

    def test_a_get_all_Tipos(self):
        """verifica si se puede acceder al listado de tipos de atributos """
        request = self.client.get('/tipoAtributo/administrartipoAtributo', follow_redirects=True)
        self.assertEqual(request._status, '200 OK')   
   
    def test_b_crear_tipoatt(self):
        """  crea el proyecto y verifica si el tipo de atri. fue creado     """        
        print "Probando crear un tipo de att"
        request = self._crear_tipoatt('testprueba', 'testdesc' )     
        print "Respuesta satisfactoria, verificando si creo el tipo de att"
        assert 'testprueba' in request.data
        print "tipo att creado correctamente"


    def test_c_crear_tipoatt_duplicado(self): 
        """prueba si se pueden crear tipo att duplicados    """
        print "Creacion de tipo att con nombre repetido"
        request = self._crear_tipoatt('testprueba', 'testdesc' )    
        print "Respuesta satisfactoria, verificando si dejo crear el tipo att"
        assert 'Clave unica violada por favor ingrese otro CODIGO para el Tipo de Atributo' in request.data
        print "Clave unica violada por favor ingrese otro CODIGO para el Tipo de Atributo"

        
    def test_e_editar_tipoatt(self):
        """  edita un tipo att    """        
        print "Probando editar tipoatt"
        request = self._editar_tipoatt('testprueba', 'testdescedit')   
        print "Respuesta satisfactoria, verificando si se edito el tipo att"
        assert 'testdescedit' in request.data
        print "tipoatt editado correctamente"

    def test_d_eliminar_tipoatt(self):
        """verifica si se puede eliminar un atributo  """
        print "Eliminando atributo"
        borrar_request = self._eliminar_tipoatt('testprueba')
        print "verificar si se elimino"
        assert 'testprueba' not in  borrar_request.data
        self.assertEqual(borrar_request._status, '200 OK')
        print "verificacion completa, se elimino"
            
    def _crear_tipoatt(self,nombre='testprueba', descripcion='testdesc'):     
        request = self.client.post('/tipoAtributo/nuevotipoAtributo', data=dict(
            nombre = nombre,
            descripcion = descripcion), follow_redirects=True)
        return request
    
    def _editar_tipoatt(self, nombre='testprueba', descripcion='testdesc'):     
        request = self.client.post('/tipoAtributo/editartipoAtributo', data=dict(
            cnombre = nombre,
            descripcion = descripcion), follow_redirects=True)
        return request

    def _eliminar_tipoatt(self, codigo='testprueba'):     
        request = self.client.post('/tipoAtributo/eliminartipoAtributo?nombre=' + codigo, follow_redirects=True)
        return request
    
    def _get(self, url ='/tipoAtributo/administrartipoAtributo'):
        """obtiene la pagina administrar tipo att """
        return self.client.get(url, follow_redirects=True)
        
if __name__ == '__main__':
    unittest.main()