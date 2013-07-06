from loginC import app

from flask_principal import identity_loaded
from test_helper import login,_on_principal_initL, logout, TEST_USER_LIDER, TEST_PASS_LIDER
import unittest
from test.test_helper import seleccionar_proyecto

PROYECTOID = 23
nombre = 'atributoTest'
descripcion = 'atributo descri'
id_tipo_atributo=1
PATRON = nombre
PARAM = 'nombre'

class Atributo1TestCase(unittest.TestCase):
    """Clase que implementa los test para el caso de uso Atributo."""
    
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

    def test_a_get_all_atributo(self):
        """Prueba que verifica si se puede acceder al listado de atributos"""
        print '##----++++ PRUEBA UNITARIA ATRIBUTO ++++----##'
        print '+++ Obtener todas los atributos +++'
        request = self.client.get('/atributo/administraratributo', follow_redirects=True)
        self.assertNotIn('Debe loguearse primeramente!!!!', request.data, 'No se ha logueado correctamente')
        self.assertNotIn('No posee los permisos suficientes para realizar la operacion', request.data, 'No tiene permisos para ver las atributos')
        self.assertEqual(request._status, '200 OK', 'Error al obtener los atributos como '+ TEST_USER_LIDER)
        print '*-- Obtiene todos los atributos -- request result: ' + request._status + ' --*'
        print'*---test 1 atributo---*'
   
    def test_b_crear_atributo(self):    
        """ Prueba de creacion de atributo y verifica si la atributo fue creada"""
        print '+++ Creacion de atributo +++'
        request = self._crear_atributo(nombre, descripcion, id_tipo_atributo)
        print '*-- datos de prueba ::: ' + nombre + ', '+  descripcion +', ' + str(id_tipo_atributo)  +' --*'
        self.assertNotIn('Debe loguearse primeramente!!!!', request.data, 'No se ha logueado correctamente')
        self.assertNotIn('No posee los permisos suficientes para realizar la operacion', request.data, 'No tiene permisos para crear atributos')
        self.assertNotIn('Error', request.data, 'Tiene errores el form o en la base de datos')
        self.assertIn('El Atributo ha sido registrado con exito', request.data, 'Error al crear el atributo')
        print '*-- request result: ' + request._status + ' --*'
        self.assertIn(nombre, request.data, 'El atributo creada no se encuentra en la tabla')
        print '*-- '+nombre+' creado correctamente, aparece en la tabla de atributos--*'
        print '*---test 2 atributo---*'
 
    def test_c_crear_atributo_duplicado(self):
        """Prueba si se pueden crear atributo duplicados"""
        print '+++ Creacion de atributo con mismo numero orden duplicado +++'
        request = self._crear_atributo(nombre, descripcion, id_tipo_atributo)
        print '*-- datos de prueba ::: ' + nombre + ', '+  descripcion +', ' + str(id_tipo_atributo)  +' --*'
        self.assertNotIn('Debe loguearse primeramente!!!!', request.data, 'No se ha logueado correctamente')
        self.assertNotIn('No posee los permisos suficientes para realizar la operacion', request.data, 'No tiene permisos para crear atributos')
        self.assertNotIn('Error', request.data, 'Tiene errores el form')
        self.assertIn('Clave unica violada por favor ingrese otro NOMBRE de Atributo', request.data, 'Atributo creado porque no existe el nombre para el nuevo')
        self.assertIn(nombre, request.data, 'El atributo creado no se encuentra en la tabla')
        print '*-- Verificacion completa, no se pueden crear dos atributos con el mismo NOMBRE --*'
        print '*---test 3 atributo---*'
    
    def test_d_buscar_atributo(self):
        """Prueba de busqueda de una atributo"""
        print '+++ Buscar una atributo existente por nombre +++'
        request = self._buscar_atributo(PATRON, PARAM)
        print '*-- datos de prueba ::: patron = '+ PATRON +', parametro = '+PARAM+' --*'
        self.assertNotIn('Debe loguearse primeramente!!!!', request.data, 'No se ha logueado correctamente')
        self.assertNotIn('No posee los permisos suficientes para realizar la operacion', request.data, 'No tiene permisos para ver las atributos')
        self.assertNotIn('Sin registro de Atributos', request.data, 'No se encontro atributos con dicho parametro')
        self.assertIn(PATRON, request.data, 'El atributo no existe en la tabla')
        print '*-- Atributo encontrado exitosamente --*'
        print '*---test 4 atributo---*'
  
    def test_e_editar_atributo(self):
        """ Prueba para editar una atributo """        
        print '+++ Edicion de atributo +++'
        request = self._editar_atributo(nombre, 'descrip editada','String')
        print '*-- datos de prueba ::: ' + nombre+', '+ 'descrip editada' + ', ' + str(id_tipo_atributo) +' --*'
        self.assertNotIn('Debe loguearse primeramente!!!!', request.data, 'No se ha logueado correctamente')
        self.assertNotIn('No posee los permisos suficientes para realizar la operacion', request.data, 'No tiene permisos para editar atributos')
        self.assertNotIn('Error', request.data, 'Tiene errores el form')
        self.assertIn('El atributo ha sido editado con exito', request.data, 'Error al editar la atributo')
        print '*-- request result: ' + request._status + ' --*'
        self.assertIn(nombre, request.data, 'El atributo creado no se encuentra en la tabla')
        print '*-- '+nombre+' creado correctamente, aparece en la tabla de atributos--*'
        print '*---test 5 atributo---*'
 
    def test_f_eliminar_atributo(self):
        """Prueba de verificacion si se puede eliminar una atributo"""
        print '+++ Eliminacion de proyecto existente +++'
        borrar_request = self._eliminar_atributo(nombre)
        print '*-- datos de prueba ::: nombre = ' + str(nombre) +' --*'
        self.assertNotIn('Debe loguearse primeramente!!!!', borrar_request.data, 'No se ha logueado correctamente')
        self.assertNotIn('No posee los permisos suficientes para realizar la operacion', borrar_request.data, 'No tiene permisos para eliminar atributos')
        self.assertIn('El atributo ha sido eliminado con exito', borrar_request.data, 'Atributo no existe el nombre atributo')
        self.assertNotIn(str(nombre), borrar_request.data, 'El atributo no ha sido borrado')
        print '*-- Verificacion completa, se elimino correctamente--*'
        print '*---test 6 atributo---*'
        print '##----++++ FIN PRUEBA UNITARIA atributo ++++----##'
            
    def _crear_atributo(self, nombre=nombre, descripcion=descripcion, id_tipo_atributo=id_tipo_atributo):     
        request = self.client.post('/atributo/nuevoatributo', data=dict(
            nombre = nombre,
            descripcion = descripcion,
            id_tipo_atributo = id_tipo_atributo), follow_redirects=True)
        return request
    
    def _buscar_atributo(self, patron = PATRON , parametro = PARAM ):
        request = self.client.get('/atributo/buscaratributo?patron='+patron+'&parametro='+parametro+'&Buscar=Buscar', follow_redirects=True)
        return request

    def _editar_atributo(self, nombre=nombre, descripcion='decrip editada', id_tipo_atributo = id_tipo_atributo):     
        request = self.client.post('/atributo/editaratributo?nom=' + nombre, data=dict(
            nombre = nombre,
            descripcion = descripcion,
            id_tipo_atributo = id_tipo_atributo), follow_redirects=True)
        return request

    def _eliminar_atributo(self, nombre=nombre):     
        request = self.client.post('/atributo/eliminaratributo?nom='+str(nombre), follow_redirects=True)
        return request
    
    def _get(self, url ='/atributo/administraratributo'):
        """obtiene la pagina administrar atributos """
        return self.client.get(url, follow_redirects=True)
        
if __name__ == '__main__':
    unittest.main()