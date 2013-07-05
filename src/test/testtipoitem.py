from loginC import app

from flask_principal import identity_loaded
from test_helper import login,_on_principal_initL, logout, TEST_USER_LIDER, TEST_PASS_LIDER
import unittest
from test.test_helper import seleccionar_proyecto

PROYECTOID = 23
codigo = 'tipoItemTest'
nombre = 'tipoItemTest'
descripcion = 'tipoItem descri'
id_fase = 8
PATRON = codigo
PARAM = 'codigo'

class TipoItemTestCase(unittest.TestCase):
    """Clase que implementa los test para el caso de uso TipoItem."""
    
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

    def test_a_get_all_tipoItem(self):
        """Prueba que verifica si se puede acceder al listado de Tipos de Items"""
        print '##----++++ PRUEBA UNITARIA TIPOITEM ++++----##'
        print '+++ Obtener todas los tipos Items +++'
        request = self.client.get('/tipoItem/administrartipoItem', follow_redirects=True)
        self.assertNotIn('Debe loguearse primeramente!!!!', request.data, 'No se ha logueado correctamente')
        self.assertNotIn('No posee los permisos suficientes para realizar la operacion', request.data, 'No tiene permisos para ver las tipoItems')
        self.assertEqual(request._status, '200 OK', 'Error al obtener los tipos de Items como '+ TEST_USER_LIDER)
        print '*-- Obtiene todos los tipos de Items -- request result: ' + request._status + ' --*'
        print'*---test 1 tipoItem---*'
   
    def test_b_crear_tipoItem(self):    
        """ Prueba de creacion de tipoItem y verifica si el tipoItem fue creada"""
        print '+++ Creacion de tipoItem +++'
        request = self._crear_tipoItem(codigo, nombre, descripcion, id_fase)
        print '*-- datos de prueba ::: ' + codigo + ', ' + nombre + ', '+  descripcion +', ' + str(id_fase)  +' --*'
        self.assertNotIn('Debe loguearse primeramente!!!!', request.data, 'No se ha logueado correctamente')
        self.assertNotIn('No posee los permisos suficientes para realizar la operacion', request.data, 'No tiene permisos para crear tipoItems')
        self.assertNotIn('Error', request.data, 'Tiene errores el form o en la base de datos')
        self.assertIn('El Tipo de Item ha sido registrado con exito', request.data, 'Error al crear el tipoItem')
        print '*-- request result: ' + request._status + ' --*'
        self.assertIn(codigo, request.data, 'El tipoItem creada no se encuentra en la tabla')
        print '*-- '+ codigo +' creado correctamente, aparece en la tabla de tipoItems--*'
        print '*---test 2 tipoItem---*'
 
    def test_c_crear_tipoItem_duplicado(self):
        """Prueba si se pueden crear tipoItem duplicados"""
        print '+++ Creacion de tipoItem con mismo numero orden duplicado +++'
        request = self._crear_tipoItem(codigo, nombre, descripcion, id_fase)
        print '*-- datos de prueba ::: ' + codigo + ', '+ nombre + ', '+  descripcion +', ' + str(id_fase)  +' --*'
        self.assertNotIn('Debe loguearse primeramente!!!!', request.data, 'No se ha logueado correctamente')
        self.assertNotIn('No posee los permisos suficientes para realizar la operacion', request.data, 'No tiene permisos para crear tipoItems')
        self.assertNotIn('Error', request.data, 'Tiene errores el form')
        self.assertIn('Clave unica violada por favor ingrese otro CODIGO de Tipo de Item', request.data, 'tipoItem creado porque no existe el codigo del nuevo')
        self.assertIn(nombre, request.data, 'El tipoItem creado no se encuentra en la tabla')
        print '*-- Verificacion completa, no se pueden crear dos tipoItems con el mismo NOMBRE --*'
        print '*---test 3 tipoItem---*'
    
    def test_d_buscar_tipoItem(self):
        """Prueba de busqueda de una tipoItem"""
        print '+++ Buscar una tipoItem existente por nombre +++'
        request = self._buscar_tipoItem(PATRON, PARAM)
        print '*-- datos de prueba ::: patron = '+ PATRON +', parametro = '+PARAM+' --*'
        self.assertNotIn('Debe loguearse primeramente!!!!', request.data, 'No se ha logueado correctamente')
        self.assertNotIn('No posee los permisos suficientes para realizar la operacion', request.data, 'No tiene permisos para ver las tipoItems')
        self.assertNotIn('Sin registro de Tipo Item', request.data, 'No se encontro tipoItems con dicho parametro')
        self.assertIn(PATRON, request.data, 'El tipoItem no existe en la tabla')
        print '*-- tipoItem encontrado exitosamente --*'
        print '*---test 4 tipoItem---*'
  
    def test_e_editar_tipoItem(self):
        """ Prueba para editar una tipoItem """        
        print '+++ Edicion de tipoItem +++'
        request = self._editar_tipoItem(codigo, nombre, 'descrip editada',id_fase)
        print '*-- datos de prueba ::: ' + codigo +', '+ nombre+', '+ 'descrip editada' + ', ' + str(id_fase) +' --*'
        self.assertNotIn('Debe loguearse primeramente!!!!', request.data, 'No se ha logueado correctamente')
        self.assertNotIn('No posee los permisos suficientes para realizar la operacion', request.data, 'No tiene permisos para editar tipoItems')
        self.assertNotIn('Error', request.data, 'Tiene errores el form')
        self.assertIn('El tipo item ha sido editado con exito', request.data, 'Error al editar la tipoItem')
        print '*-- request result: ' + request._status + ' --*'
        self.assertIn(codigo, request.data, 'El tipoItem creado no se encuentra en la tabla')
        print '*-- '+codigo+' creado correctamente, aparece en la tabla de tipoItems--*'
        print '*---test 5 tipoItem---*'
 
    def test_f_eliminar_tipoItem(self):
        """Prueba de verificacion si se puede eliminar una tipoItem"""
        print '+++ Eliminacion de proyecto existente +++'
        borrar_request = self._eliminar_tipoItem(codigo)
        print '*-- datos de prueba ::: codigo = ' + str(codigo) +' --*'
        self.assertNotIn('Debe loguearse primeramente!!!!', borrar_request.data, 'No se ha logueado correctamente')
        self.assertNotIn('No posee los permisos suficientes para realizar la operacion', borrar_request.data, 'No tiene permisos para eliminar tipoItems')
        self.assertNotIn('El Tipo de Item no puede ser eliminado, ya que esta siendo utilizado por algun Item', borrar_request.data, 'El tipo de item no debe puede ser eliminado')
        self.assertIn('El tipo item ha sido eliminado con exito', borrar_request.data, 'tipoItem no existe el nombre tipoItem')
        self.assertNotIn(codigo, borrar_request.data, 'El tipoItem no ha sido borrado')
        print '*-- Verificacion completa, se elimino correctamente--*'
        print '*---test 6 tipoItem---*'
        print '##----++++ FIN PRUEBA UNITARIA tipoItem ++++----##'
            
    def _crear_tipoItem(self, codigo=codigo, nombre=nombre, descripcion=descripcion, id_fase=id_fase):     
        request = self.client.post('/tipoItem/nuevotipoItem', data=dict(
            codigo=codigo,
            nombre = nombre,
            descripcion = descripcion,
            id_fase = id_fase), follow_redirects=True)
        return request
    
    def _buscar_tipoItem(self, patron = PATRON , parametro = PARAM ):
        request = self.client.get('/tipoItem/buscartipoItem?patron='+patron+'&parametro='+parametro+'&Buscar=Buscar', follow_redirects=True)
        return request

    def _editar_tipoItem(self, codigo=codigo,nombre=nombre, descripcion='decrip editada', id_fase = id_fase):     
        request = self.client.post('/tipoItem/editartipoItem?codigo=' + codigo, data=dict(
            codigo = codigo,
            nombre = nombre,
            descripcion = descripcion,
            id_fase = id_fase), follow_redirects=True)
        return request

    def _eliminar_tipoItem(self, codigo=codigo):     
        request = self.client.post('/tipoItem/eliminartipoItem?cod='+codigo, follow_redirects=True)
        return request
    
    def _get(self, url ='/tipoItem/administrartipoItem'):
        """obtiene la pagina administrar tipoItems """
        return self.client.get(url, follow_redirects=True)
        
if __name__ == '__main__':
    unittest.main()