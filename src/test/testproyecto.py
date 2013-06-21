import unittest
from loginC import app

from flask_principal import identity_loaded
from test_helper import login,_on_principal_init, logout, TEST_USER


class ProyectoTestCase(unittest.TestCase):
    """Clase que implementa los test para el caso de uso Proyecto."""
    
    def setUp(self):
        """se llama al metodo antes de iniciar el test"""        
        self.client = app.test_client()
        self.acceso = login(self.client)
        identity_loaded.connect(_on_principal_init)

    def tearDown(self):
        """ se llama al metodo al terminar el test"""
        self.client = app.test_client()
        self.salir = logout(self.client)

    def test_a_get_all_proyectos(self):
        """Prueba que verifica si se puede acceder al listado de proyectos"""
        print '##----++++ PRUEBA UNITARIA PROYECTO ++++----##'
        print '+++ Obtener todos los proyectos +++'
        request = self.client.get('/proyecto/administrarproyecto', follow_redirects=True)
        self.assertNotIn('sin permisos', request.data, 'No tiene permisos para ver los proyectos')
        self.assertEqual(request._status, '200 OK', 'Error al obtener los proyectos como '+ TEST_USER)
        print '*-- Obtiene todos los proyectos -- request result: ' + request._status + ' --*'
        print'*---test 1 proyecto---*'
   
    def test_crear_proyecto(self):
        """  crea el proyecto y verifica si el proyecto fue creado     """        
        print "Probando crear un proyecto"
        request = self._crear_proyecto('prytest', 'proytesting', 'N','2', '14-05-2013','22-05-2013', None, '1' )     
        print "Respuesta satisfactoria, verificando si creo el proyecto"
        request_all = self.app.get('/proyecto/administrarproyecto', follow_redirects=True)
        assert 'prytest' in request_all.data
        print "proyecto creado correctamente"
 
    def test_crear_proyecto_duplicado(self):
        """prueba si se pueden crear proyectos duplicados    """
        #Ahora probamos vovler a crear
        print "Creacion de proyecto con nombre repetido"
        request = self._crear_proyecto('prytest', 'proytesting', 'N','2', '14-05-2013','22-05-2013', None, '1' )    
        print "Respuesta satisfactoria, verificando si dejo crear el proyecto"
        assert 'El Proyecto ha sido registrado con exito' in request.data
        print "Verificacion completa, no se pueden crear dos proyectos con el mismo nombre"

    #===========================================================================
    # def test_eliminar_proyecto(self):
    #    """verifica si se puede eliminar un proyecto  """
    #    print "Creando rol con nombre 'rolprueba2'."
    #    crear_request = self._crear_rol('rolprueba2', 'borrar')
    #    print "Verificando si se creo el rol"
    #    all_request = self._get()
    #    assert 'rolprueba2' in all_request.data
    #    print "Rol creado exitosamente"        
    #    borrar_request = self._eliminar_rol('rolprueba2', 'borrar')
    #    print "verificar si se elimino"
    #    request_all = self._get() #self.app.get('/administrarrol', follow_redirects=True)
    #    assert 'rolprueba2' not in  request_all.data
    #    self.assertEqual(request_all._status, '200 OK')
    #    print "verificacion completa, se elimino"
    #    
    #    
    # def test_editar_proyecto(self):
    #    """  edita un proyecto    """        
    #    print "Probando editar proyecto"
    #    request = self._editar_proyecto('prytest', 'proytesting', 'N','2', '14-05-2013','22-05-2013', None, '1' )   
    #    print "Respuesta satisfactoria, verificando si se edito el proyecto"
    #    request_all = self.app.get('/proyecto/administrarproyecto', follow_redirects=True)
    #    assert 'prytest' in request_all.data
    #    print "proyecto editado correctamente"
    #===========================================================================
            
    def _crear_proyecto(self,nombre='prytest', descripcion='proytesting', estado='N', cant_miembros='2', fecha_inicio='14-05-2013',
                        fecha_fin='22-05-2013', fecha_ultima_mod=None, id_usuario_lider='1'):     
        request = self.app.post('/proyecto/nuevoproyecto', data=dict(
            nombre = nombre,
            descripcion = descripcion,
            estado = estado,
            cant_miembros = cant_miembros,
            fecha_inicio = fecha_inicio,
            fecha_fin = fecha_fin,
            fecha_ultima_mod = fecha_ultima_mod,
            id_usuario_lider = id_usuario_lider), follow_redirects=True)
        return request
    
    def _editar_proyecto(self, nombre='prytest', descripcion='proytestingmod', estado='N', cant_miembros='2', fecha_inicio='14-05-2013',
                        fecha_fin='22-05-2013', fecha_ultima_mod=None, id_usuario_lider='1'):     
        request = self.app.post('/proyecto/editarproyecto', data=dict(
            cnombre = nombre,
            descripcion = descripcion,
            estado = estado,
            cant_miembros = cant_miembros,
            fecha_inicio = fecha_inicio,
            fecha_fin = fecha_fin,
            fecha_ultima_mod = fecha_ultima_mod,
            id_usuario_lider = id_usuario_lider), follow_redirects=True)
        return request

#    def _eliminar_proyecto(self, codigo='rolprueba2', descripcion='borrar'):     
#        request = self.app.post('/eliminar', data=dict(
#            codigo=codigo, descripcion=descripcion), follow_redirects=True)
#        return request
    
    def _get(self, url ='/proyecto/administrarproyecto'):
        """obtiene la pagina administrar proyectos """
        return self.app.get(url, follow_redirects=True)
    

        
if __name__ == '__main__':
    unittest.main()