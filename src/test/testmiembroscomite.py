from loginC import app
from flask_principal import identity_loaded
from test_helper import login,_on_principal_initL, logout, TEST_USER_LIDER, seleccionar_proyecto, getMiembroComite,getIdUsuario

import unittest
PROYECTOID=23
USU='testdesa'
PATRON=USU
PARAM='usuario'

class MiembrosComiteTestCase(unittest.TestCase):
    """Clase que implementa los test para el caso de uso Miembros Comite."""
   
    def setUp(self):
        """se llama al metodo antes de iniciar el test"""        
        self.client = app.test_client()
        self.acceso = login(self.client)
        identity_loaded.connect(_on_principal_initL)
        self.proyse= seleccionar_proyecto(self.client, PROYECTOID)
        with app.test_client() as c:
            with c.session_transaction() as sess:
                sess['pry'] = PROYECTOID

    def tearDown(self):
        """ se llama al metodo al terminar el test"""
        self.client = app.test_client()
        self.salir = logout(self.client)
    
    def test_a_get_all_miembrosComite(self):
        """Prueba que verifica si se puede acceder al listado de miembrosComite"""
        print '##----++++ PRUEBA UNITARIA MIEMBROSCOMITE ++++----##'
        print '+++ Obtener todos los miembrosComite +++'
        request = self.client.get('/miembrosComite/administrarmiembrosComite', follow_redirects=True)
        self.assertNotIn('Sin permisos para administrar miembros Comite', request.data, 'No tiene permisos para ver los miembros del comite')
        self.assertEqual(request._status, '200 OK', 'Error al obtener los miembros del comite como '+ TEST_USER_LIDER)
        print '*-- Obtiene todos los miembros del comite -- request result: ' + request._status + ' --*'
        print'*---test 1 miembrosComite---*'
   
    def test_b_crear_miembrosComite(self):     
        """ Prueba de creacion de un miembrosComite y verifica si miembrosComite fue creado"""
        print '+++ Creacion de miembrosComite +++'
        request = self._crear_miembrosComite(USU)
        print '*-- datos de prueba ::: ' + USU +' --*'
        self.assertNotIn('No posee los permisos suficientes para realizar la operacion', request.data, 'No tiene permisos para crear un miembro Comite')
        self.assertNotIn('No se pueden asignar Miembros al Comite de Cambios', request.data, 'Solo se puede asignar miembros cuando el proyecto tiene el estado Nuevo')
        self.assertNotIn('No se pueden asignar Miembros al Comite de Cambios, numero maximo de miembros alcanzado', request.data, 'El numero maximo de miembros del comite ya fue alcanzado')
        self.assertNotIn('Error en la Base de Datos', request.data, 'Error al tratar de insertar en la base de datos')
        self.assertIn('Se ha asignado el usuario al Comite de Cambios', request.data, 'Error al asignar usuario como miembro del comite')
        print '*-- request result: ' + request._status + ' --*'
        self.assertIn(USU, request.data, 'El usuario como miembro no se encuentra en la tabla')
        print '*-- Miembro '+ USU +' creado correctamente, aparece en la tabla de miembros del comite--*'
        print '*---test 2 miembrosComite---*'

    def test_c_crear_miembrosComite_duplicado(self):
        """ Prueba si se pueden crear miembrosComite duplicados """
        print '+++ Creacion de miembrosComite con usuario repetido +++'
        request = self._crear_miembrosComite(USU)
        print '*-- Datos de prueba ::: ' + USU +' --*'
        self.assertNotIn('Sin permisos para agregar miembrosComite', request.data, 'No tiene permisos para crear usuarios')
        self.assertIn('Clave unica violada por favor ingrese otro usuario', request.data, 'Usuario creado como miembro, no existe como miembro del comite')
        print '*-- Verificacion completa, no se pueden crear miembros con el mismo usuario --*'
        print '*---test 3 miembrosComite---*'
        
    def test_d_buscar_miembrosComite(self):
        """Prueba de busqueda de un miembro de comite"""
        print '+++ Buscar un usuario existente como miembro del proyecto+++'
        request = self._buscar_miembrosComite(PATRON, PARAM)
        print '*-- datos de prueba ::: patron = '+ PATRON +', parametro = '+PARAM+' --*'
        self.assertNotIn('No posee los permisos suficientes para realizar la operacion', request.data, 'No tiene permisos para ver los miembros del comite')
        self.assertNotIn('Sin registro de Miembros Comite', request.data, 'No se encontro un miembro del comite con dicho parametro')
        self.assertIn(PATRON, request.data, 'El miembro del comite no existe en la tabla')
        print '*-- MiembroComite encontrado exitosamente --*'
        print '*---test 4 miembroComite---*'

    def test_e_eliminar_miembrosComite(self):
        """ Prueba de verificacion si se puede eliminar un usuario """
        print '+++ Eliminacion de miembroComite existente +++'
        idusu=getIdUsuario(USU)
        miem_com= getMiembroComite(PROYECTOID, idusu)
        print str(miem_com.id)
        borrar_request = self._eliminar_miembrosComite(miem_com.id, idusu)
        print '*-- datos de prueba ::: usuario = ' + USU +' --*'
        self.assertNotIn('No posee los permisos suficientes para realizar la operacion', borrar_request.data, 'No tiene permisos eliminar usuarios')
        self.assertNotIn('Error en la Base de Datos', borrar_request.data, 'Error al eliminar miembro')
        self.assertIn('El Miembro ha sido eliminado con exito', borrar_request.data, 'No existe el miembro del comite')
        self.assertNotIn(USU, borrar_request.data, 'El usuario no ha sido borrado')
        print '*-- Verificacion completa, se elimino correctamente--*'
        print '*---test 5 usuario---*'

    def test_f_get_all_usuarios(self):
        """Prueba que verifica si se puede acceder al listado de usuarios"""
        print '+++ Obtener todos los usuarios +++'
        request = self.client.get('/miembrosComite/listarusuarios', follow_redirects=True)
        self.assertNotIn('No posee los permisos suficientes para realizar la operacion', request.data, 'No tiene permisos para ver los usuarios para asignar como miembro')
        self.assertEqual(request._status, '200 OK', 'Error al obtener los usuarios como '+ TEST_USER_LIDER)
        print '*-- Obtiene todos los usuarios -- request result: ' + request._status + ' --*'
        print'*---test 6 miembrosComite---*'

    def test_g_buscar_miembrosComite2(self):
        """Prueba de busqueda de un usuario"""
        print '+++ Buscar un usuario existente como miembro del proyecto+++'
        request = self._buscar_miembrosComite2(PATRON, PARAM)
        print '*-- datos de prueba ::: patron = '+ PATRON +', parametro = '+PARAM+' --*'
        self.assertNotIn('No posee los permisos suficientes para realizar la operacion', request.data, 'No tiene permisos para ver los usuarios')
        self.assertNotIn('Sin registro de usuarios', request.data, 'No se encontro usuario segun patron')
        self.assertIn(PATRON, request.data, 'El usuario no existe en la tabla')
        print '*-- Usuario encontrado exitosamente --*'
        print '*---test 7 miembroComite---*'
        print '##----++++ FIN PRUEBA UNITARIA MIEMBROSCOMITE ++++----##'
                   
    def _crear_miembrosComite(self, usuario=USU):     
        request = self.client.post('/miembrosComite/nuevomiembrosComite?usu='+usuario, follow_redirects=True)
        return request
    
    def _buscar_miembrosComite(self, patron = PATRON , parametro = PARAM ):
        request = self.client.get('/miembrosComite/buscarmiembrosComite?patron='+patron+'&parametro='+parametro+'&Buscar=Buscar', follow_redirects=True)
        return request
    
    def _buscar_miembrosComite2(self, patron = PATRON , parametro = PARAM ):
        request = self.client.get('/miembrosComite/buscarmiembrosComite2?patron='+patron+'&parametro='+parametro+'&Buscar=Buscar', follow_redirects=True)
        return request

    def _eliminar_miembrosComite(self, miembro=None,usu=None):     
        request = self.client.post('/miembrosComite/eliminarmiembrosComite?id_mc='+str(miembro)+'&usu='+str(usu), follow_redirects=True)
        return request
   
    def _get(self, url ='/miembrosComite/administrarmiembrosComite'):
        """obtiene la pagina administrar miembrosComite """
        return self.client.get(url, follow_redirects=True)
    
if __name__ == '__main__':
    unittest.main()