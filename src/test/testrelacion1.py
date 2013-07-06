from loginC import app

from flask_principal import identity_loaded
from test_helper import login,_on_principal_initL, logout, TEST_USER_LIDER, TEST_PASS_LIDER
import unittest
from test.test_helper import seleccionar_proyecto

PROYECTOID = 23
nombre = 'relacionTest'
descripcion = 'relacion descri'
id_tipo_relacion=1
PATRON = nombre
PARAM = 'nombre'

class Relacion1TestCase(unittest.TestCase):
    """Clase que implementa los test para el caso de uso Relacion."""
    
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

    def test_a_get_all_relacion(self):
        """Prueba que verifica si se puede acceder al listado de relacions"""
        print '##----++++ PRUEBA UNITARIA RELACION ++++----##'
        print '+++ Obtener todas los relacions +++'
        request = self.client.get('/relacion/administrarrelacion', follow_redirects=True)
        self.assertNotIn('Debe loguearse primeramente!!!!', request.data, 'No se ha logueado correctamente')
        self.assertNotIn('No posee los permisos suficientes para realizar la operacion', request.data, 'No tiene permisos para ver las relacions')
        self.assertEqual(request._status, '200 OK', 'Error al obtener los relacions como '+ TEST_USER_LIDER)
        print '*-- Obtiene todos los relacions -- request result: ' + request._status + ' --*'
        print'*---test 1 relacion---*'
   
    def test_b_crear_relacion(self):    
        """ Prueba de creacion de relacion y verifica si la relacion fue creada"""
        print '+++ Creacion de relacion +++'
        request = self._crear_relacion(nombre, descripcion, id_tipo_relacion)
        print '*-- datos de prueba ::: ' + nombre + ', '+  descripcion +', ' + str(id_tipo_relacion)  +' --*'
        self.assertNotIn('Debe loguearse primeramente!!!!', request.data, 'No se ha logueado correctamente')
        self.assertNotIn('No posee los permisos suficientes para realizar la operacion', request.data, 'No tiene permisos para crear relacions')
        self.assertNotIn('Error', request.data, 'Tiene errores el form o en la base de datos')
        self.assertIn('El Relacion ha sido registrado con exito', request.data, 'Error al crear el relacion')
        print '*-- request result: ' + request._status + ' --*'
        self.assertIn(nombre, request.data, 'El relacion creada no se encuentra en la tabla')
        print '*-- '+nombre+' creado correctamente, aparece en la tabla de relacions--*'
        print '*---test 2 relacion---*'
 
    def test_c_crear_relacion_duplicado(self):
        """Prueba si se pueden crear relacion duplicados"""
        print '+++ Creacion de relacion con mismo numero orden duplicado +++'
        request = self._crear_relacion(nombre, descripcion, id_tipo_relacion)
        print '*-- datos de prueba ::: ' + nombre + ', '+  descripcion +', ' + str(id_tipo_relacion)  +' --*'
        self.assertNotIn('Debe loguearse primeramente!!!!', request.data, 'No se ha logueado correctamente')
        self.assertNotIn('No posee los permisos suficientes para realizar la operacion', request.data, 'No tiene permisos para crear relacions')
        self.assertNotIn('Error', request.data, 'Tiene errores el form')
        self.assertIn('Clave unica violada por favor ingrese otro NOMBRE de Relacion', request.data, 'Relacion creado porque no existe el nombre para el nuevo')
        self.assertIn(nombre, request.data, 'El relacion creado no se encuentra en la tabla')
        print '*-- Verificacion completa, no se pueden crear dos relacions con el mismo NOMBRE --*'
        print '*---test 3 relacion---*'
    
    def test_d_buscar_relacion(self):
        """Prueba de busqueda de una relacion"""
        print '+++ Buscar una relacion existente por nombre +++'
        request = self._buscar_relacion(PATRON, PARAM)
        print '*-- datos de prueba ::: patron = '+ PATRON +', parametro = '+PARAM+' --*'
        self.assertNotIn('Debe loguearse primeramente!!!!', request.data, 'No se ha logueado correctamente')
        self.assertNotIn('No posee los permisos suficientes para realizar la operacion', request.data, 'No tiene permisos para ver las relacions')
        self.assertNotIn('Sin registro de Relacions', request.data, 'No se encontro relacions con dicho parametro')
        self.assertIn(PATRON, request.data, 'El relacion no existe en la tabla')
        print '*-- Relacion encontrado exitosamente --*'
        print '*---test 4 relacion---*'
  
    def test_e_editar_relacion(self):
        """ Prueba para editar una relacion """        
        print '+++ Edicion de relacion +++'
        request = self._editar_relacion(nombre, 'descrip editada','String')
        print '*-- datos de prueba ::: ' + nombre+', '+ 'descrip editada' + ', ' + str(id_tipo_relacion) +' --*'
        self.assertNotIn('Debe loguearse primeramente!!!!', request.data, 'No se ha logueado correctamente')
        self.assertNotIn('No posee los permisos suficientes para realizar la operacion', request.data, 'No tiene permisos para editar relacions')
        self.assertNotIn('Error', request.data, 'Tiene errores el form')
        self.assertIn('El relacion ha sido editado con exito', request.data, 'Error al editar la relacion')
        print '*-- request result: ' + request._status + ' --*'
        self.assertIn(nombre, request.data, 'El relacion creado no se encuentra en la tabla')
        print '*-- '+nombre+' creado correctamente, aparece en la tabla de relacions--*'
        print '*---test 5 relacion---*'
 
    def test_f_eliminar_relacion(self):
        """Prueba de verificacion si se puede eliminar una relacion"""
        print '+++ Eliminacion de proyecto existente +++'
        borrar_request = self._eliminar_relacion(nombre)
        print '*-- datos de prueba ::: nombre = ' + str(nombre) +' --*'
        self.assertNotIn('Debe loguearse primeramente!!!!', borrar_request.data, 'No se ha logueado correctamente')
        self.assertNotIn('No posee los permisos suficientes para realizar la operacion', borrar_request.data, 'No tiene permisos para eliminar relacions')
        self.assertIn('El relacion ha sido eliminado con exito', borrar_request.data, 'Relacion no existe el nombre relacion')
        self.assertNotIn(str(nombre), borrar_request.data, 'El relacion no ha sido borrado')
        print '*-- Verificacion completa, se elimino correctamente--*'
        print '*---test 6 relacion---*'
        print '##----++++ FIN PRUEBA UNITARIA relacion ++++----##'
            
    def _crear_relacion(self, nombre=nombre, descripcion=descripcion, id_tipo_relacion=id_tipo_relacion):     
        request = self.client.post('/relacion/nuevorelacion', data=dict(
            nombre = nombre,
            descripcion = descripcion,
            id_tipo_relacion = id_tipo_relacion), follow_redirects=True)
        return request
    
    def _buscar_relacion(self, patron = PATRON , parametro = PARAM ):
        request = self.client.get('/relacion/buscarrelacion?patron='+patron+'&parametro='+parametro+'&Buscar=Buscar', follow_redirects=True)
        return request

    def _editar_relacion(self, nombre=nombre, descripcion='decrip editada', id_tipo_relacion = id_tipo_relacion):     
        request = self.client.post('/relacion/editarrelacion?nom=' + nombre, data=dict(
            nombre = nombre,
            descripcion = descripcion,
            id_tipo_relacion = id_tipo_relacion), follow_redirects=True)
        return request

    def _eliminar_relacion(self, nombre=nombre):     
        request = self.client.post('/relacion/eliminarrelacion?nom='+str(nombre), follow_redirects=True)
        return request
    
    def _get(self, url ='/relacion/administrarrelacion'):
        """obtiene la pagina administrar relacions """
        return self.client.get(url, follow_redirects=True)
        
if __name__ == '__main__':
    unittest.main()