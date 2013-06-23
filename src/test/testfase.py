from loginC import app

from flask_principal import identity_loaded
from test_helper import login,_on_principal_initL, logout, TEST_USER_LIDER, TEST_PASS_LIDER
import unittest
import datetime
from test.test_helper import seleccionar_proyecto

TODAY = datetime.date.today()
PROYECTOID = 2
nro_orden = 4
nombre = 'TEST FASE 1 P4'
descripcion = 'test fase 1 des'
estado = 'I'
fecha_inicio = TODAY
fecha_fin = '2014-05-20'
id_proyecto = PROYECTOID
PATRON = nombre
PARAM = 'nombre'

class FaseTestCase(unittest.TestCase):
    """Clase que implementa los test para el caso de uso Fase."""
    
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
        self.salir = logout(self.client)

    def test_a_get_all_fases(self):
        """Prueba que verifica si se puede acceder al listado de fases"""
        print '##----++++ PRUEBA UNITARIA FASE ++++----##'
        print '+++ Obtener todas las fases +++'
        request = self.client.get('/fase/administrarfase', follow_redirects=True)
        self.assertNotIn('No posee los permisos suficientes para realizar la operacion', request.data, 'No tiene permisos para ver las fases')
        self.assertEqual(request._status, '200 OK', 'Error al obtener las fases como '+ TEST_USER_LIDER)
        print '*-- Obtiene todos las fases -- request result: ' + request._status + ' --*'
        print'*---test 1 fase---*'
   
    def test_b_crear_fases(self):    
        """ Prueba de creacion de fase y verifica si la fase fue creada"""
        print '+++ Creacion de fase +++'
        request = self._crear_fase(nro_orden, nombre, descripcion, estado, fecha_inicio, fecha_fin, id_proyecto)
        print '*-- datos de prueba ::: ' + str(nro_orden) + ', '+ nombre+', '+  descripcion+', ' +estado + ', ' + str(fecha_inicio) +', '+ str(fecha_fin) +', '+ str(id_proyecto) +' --*'
        self.assertNotIn('No posee los permisos suficientes para realizar la operacion', request.data, 'No tiene permisos para crear fases')
        self.assertNotIn('Error', request.data, 'Tiene errores el form')
        self.assertIn('La fase ha sido registrada con exito', request.data, 'Error al crear la fase')
        print '*-- request result: ' + request._status + ' --*'
        self.assertIn(nombre, request.data, 'La fase creada no se encuentra en la tabla')
        print '*-- '+nombre+' creada correctamente, aparece en la tabla de fases--*'
        print '*---test 2 fase---*'

    def test_c_crear_fase_duplicado(self):
        """prueba si se pueden crear fase duplicados"""
        print '+++ Creacion de fase con mismo numero orden duplicado +++'
        request = self._crear_fase(nro_orden, nombre, descripcion, estado, fecha_inicio, fecha_fin, id_proyecto)
        print '*-- datos de prueba ::: ' + str(nro_orden) + ', '+ nombre+', '+  descripcion+', ' +estado + ', ' + str(fecha_inicio) +', '+ str(fecha_fin) +', '+ str(id_proyecto) +' --*'
        self.assertNotIn('No posee los permisos suficientes para realizar la operacion', request.data, 'No tiene permisos para crear fases')
        self.assertNotIn('Error', request.data, 'Tiene errores el form')
        self.assertIn('Clave unica violada por favor ingrese otro NUMERO de Fase', request.data, 'Fase creada, no existe el numero de orden para la nueva fase')
        self.assertIn(str(nro_orden), request.data, 'La fase creada no se encuentra en la tabla')
        print '*-- Verificacion completa, no se pueden crear dos fases con el mismo numero de orden --*'
        print '*---test 3 fase---*'
    
    def test_d_buscar_fase(self):
        """Prueba de busqueda de una fase"""
        print '+++ Buscar una fase existente por nombre +++'
        request = self._buscar_fase(PATRON, PARAM)
        print '*-- datos de prueba ::: patron = '+ PATRON +', parametro = '+PARAM+' --*'
        self.assertNotIn('Sin permisos para buscar fase', request.data, 'No tiene permisos para ver las fases')
        self.assertNotIn('Sin registro de fases', request.data, 'No se encontro fases con dicho parametro')
        self.assertIn(PATRON, request.data, 'La fase no existe en la tabla')
        print '*-- Fase encontrada exitosamente --*'
        print '*---test 4 fase---*'

    def test_e_editar_fase(self):
        """  edita una fase    """        
        print '+++ Edicion de fase +++'
        request = self._editar_fase(nro_orden, nombre, 'decrip editada', estado, fecha_inicio, fecha_fin, id_proyecto)
        print '*-- datos de prueba ::: ' + str(nro_orden) + ', '+ nombre+', '+ 'decrip editada'+', ' +estado + ', ' + str(fecha_inicio) +', '+ str(fecha_fin) +', '+ str(id_proyecto) +' --*'
        self.assertNotIn('No posee los permisos suficientes para realizar la operacion', request.data, 'No tiene permisos para editar fases')
        self.assertNotIn('Error', request.data, 'Tiene errores el form')
        self.assertIn('La fase ha sido editada con exito', request.data, 'Error al crear la fase')
        print '*-- request result: ' + request._status + ' --*'
        self.assertIn(nombre, request.data, 'La fase creada no se encuentra en la tabla')
        print '*-- '+nombre+' creada correctamente, aparece en la tabla de fases--*'
        print '*---test 5 fase---*'

    def test_f_eliminar_fase(self):
        """Prueba de verificacion si se puede eliminar una fase"""
        print '+++ Eliminacion de proyecto existente +++'
        borrar_request = self._eliminar_fase(nro_orden)
        print '*-- datos de prueba ::: numero orden = ' + str(nro_orden) +' --*'
        self.assertNotIn('No posee los permisos suficientes para realizar la operacion', borrar_request.data, 'No tiene permisos para eliminar fases')
        self.assertIn('La fase ha sido eliminado con exito', borrar_request.data, 'Fase creada, no existe el nro_oden fase')
        self.assertNotIn(str(nombre), borrar_request.data, 'La fase no ha sido borrado')
        print '*-- Verificacion completa, se elimino correctamente--*'
        print '*---test 6 fase---*'
        print '##----++++ FIN PRUEBA UNITARIA FASE ++++----##'
            
    def _crear_fase(self, nro_orden=nro_orden, nombre=nombre, descripcion=descripcion, estado=estado, fecha_inicio=fecha_inicio,
    fecha_fin=fecha_fin, id_proyecto=id_proyecto):     
        request = self.client.post('/fase/nuevafase', data=dict(
            nro_orden = nro_orden,
            nombre = nombre,
            descripcion = descripcion,
            estado = estado,
            fecha_inicio = fecha_inicio,
            fecha_fin = fecha_fin,
            id_proyecto = id_proyecto), follow_redirects=True)
        return request
    
    def _editar_fase(self, nro_orden=nro_orden, nombre=nombre, descripcion='decrip editada', estado=estado, fecha_inicio=fecha_inicio,
    fecha_fin=fecha_fin, id_proyecto=id_proyecto):     
        request = self.client.post('/fase/editarfase', data=dict(
            nro_orden = nro_orden,
            nombre = nombre,
            descripcion = descripcion,
            estado = estado,
            fecha_inicio = fecha_inicio,
            fecha_fin = fecha_fin,
            id_proyecto = id_proyecto), follow_redirects=True)
        return request
    
    def _buscar_fase(self, patron = PATRON , parametro = PARAM ):
        request = self.client.get('/fase/buscarfase2?patron='+patron+'&parametro='+parametro+'&Buscar=Buscar', follow_redirects=True)
        return request

    def _eliminar_fase(self, nro_orden=nro_orden):     
        request = self.client.post('/fase/eliminarfase?nro='+str(nro_orden), follow_redirects=True)
        return request
    
    def _get(self, url ='/fase/administrarfase'):
        """obtiene la pagina administrar fases """
        return self.client.get(url, follow_redirects=True)
        
if __name__ == '__main__':
    unittest.main()