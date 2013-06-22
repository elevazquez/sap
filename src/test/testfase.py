import unittest
from loginC import app

from test_helper import login


class FaseTestCase(unittest.TestCase):
    """Clase que implementa los test para el caso de uso Fase."""
    
    def setUp(self):
        """se llama al metodo antes de iniciar el test"""        
        print "Iniciando test"
        self.app = app.test_client()
        self.acceso = login(self.app)

    def tearDown(self):
        """ se llama al metodo al terminar el test"""
        print "Terminando test"

    def test_get_all_fases_bis(self):
        """verifica si se puede acceder al listado de faaes """
        request = self.app.get('/fase/administrarfase', follow_redirects=True)
        assert 'No posee los permisos suficientes para realizar la operacion' in request.data

    def test_get_all_fases(self):
        """verifica si se puede acceder al listado de faaes """
        request = self.app.get('/fase/administrarfase', follow_redirects=True)
        assert 'fase 2' in request.data
        self.assertEqual(request._status, '200 OK')
   
   
    def test_crear_fases(self):
        """  crea fase y verifica si  fue creado     """   
        request = self._crear_fase(1,'fase 2','testing','I',None,None, 1)     
        print "Respuesta satisfactoria, verificando si creo la fase"
        request_all = self.app.get('/fase/administrarfase', follow_redirects=True)
        assert 'La fase ha sido registrada con exito' in request_all.data
        print "fase creada correctamente"


    def test_crear_fase_duplicado(self):
        """prueba si se pueden crear fase duplicados    """
        #Ahora probamos vovler a crear
        request = self._crear_fase(1,'fase 2','testing','I',None,None, 1)  
        print "Respuesta satisfactoria, verificando si dejo crear la fase"
        assert 'Clave unica violada por favor ingrese otro NUMERO de Fase' in request.data


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
        
        
    def test_editar_fase(self):
        """  edita una fase    """        
        print "Probando editar proyecto"
        request = self._editar_fase(1,'fase 2','testing editar', 'I', None,None, 1 )   
        print "Respuesta satisfactoria, verificando si se edito la fase"
        request_all = self.app.get('/fase/administrarfase', follow_redirects=True)
        assert 'No se pueden modificar Fases que no se encuentren en estado Inicial' in request_all.data
        
    def test_editar_fase_bis(self):
        """  edita una fase    """        
        print "Probando editar proyecto"
        request = self._editar_fase(1,'fase 2','testing editar', 'P', None,None, 1 )   
        print "Respuesta satisfactoria, verificando si se edito la fase"
        request_all = self.app.get('/fase/administrarfase', follow_redirects=True)
        assert 'testing editar' in request_all.data
    
    def test_editar_fase_bis2(self):
        """  edita una fase    """        
        print "Probando editar proyecto"
        request = self._editar_fase(1,'fase 2','testing editar', 'P', '2013-05-01','2013-04-28', 1 )   
        print "Respuesta satisfactoria, verificando si se edito la fase"
        request_all = self.app.get('/fase/administrarfase', follow_redirects=True)
        assert 'La fecha de inicio no puede ser mayor que la fecha de finalizacion' in request_all.data

            
    def _crear_fase(self, nro_orden=1, nombre='fase 2', descripcion='testing', estado='I', fecha_inicio=None,
    fecha_fin=None, id_proyecto=1):     
        request = self.app.post('/fase/nuevafase', data=dict(
            nro_orden = nro_orden,
            nombre = nombre,
            descripcion = descripcion,
            estado = estado,
            fecha_inicio = fecha_inicio,
            fecha_fin = fecha_fin,
            id_proyecto = id_proyecto), follow_redirects=True)
        return request
    
    def _editar_fase(self, nro_orden=1, nombre='fase 2', descripcion='testing editar', estado='I', fecha_inicio=None,
    fecha_fin=None, id_proyecto=1):     
        request = self.app.post('/fase/editarfase', data=dict(
            nro_orden = nro_orden,
            nombre = nombre,
            descripcion = descripcion,
            estado = estado,
            fecha_inicio = fecha_inicio,
            fecha_fin = fecha_fin,
            id_proyecto = id_proyecto), follow_redirects=True)
        return request

#    def _eliminar_proyecto(self, codigo='rolprueba2', descripcion='borrar'):     
#        request = self.app.post('/eliminar', data=dict(
#            codigo=codigo, descripcion=descripcion), follow_redirects=True)
#        return request
    
    def _get(self, url ='/fase/administrarfase'):
        """obtiene la pagina administrar fases """
        return self.app.get(url, follow_redirects=True)
        
if __name__ == '__main__':
    unittest.main()