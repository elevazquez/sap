from loginC import app

from flask_principal import identity_loaded
from test_helper import login,_on_principal_init, logout, TEST_USER
import unittest

USU = 'unittest'
NOM = 'usuarioTest'
MODNOM = 'usuarioTest editado'
APE = 'usuarioTestApp'
PASS = '123'
MAIL = 'user@test.com'
DOMICI = 'test'
TEL = '123456'
FECHNAC = '1999-12-05'
PATRON = USU
PARAM= 'usuario'

class UsuarioTestCase(unittest.TestCase):
    """Clase que implementa los test para el caso de uso Usuario."""
    
    def setUp(self):
        """se llama al metodo antes de iniciar el test"""        
        self.client = app.test_client()
        self.acceso = login(self.client)
        identity_loaded.connect(_on_principal_init)

    def tearDown(self):
        """ se llama al metodo al terminar el test"""
        self.client = app.test_client()
        self.salir = logout(self.client)

    def test_a_get_all_usuarios(self):
        """Prueba que verifica si se puede acceder al listado de proyectos"""
        print '##----++++ PRUEBA UNITARIA USUARIO ++++----##'
        print '+++ Obtener todos los usuarios +++'
        request = self.client.get('/usuario/administrarusuario', follow_redirects=True)
        self.assertNotIn('sin permisos', request.data, 'No tiene permisos para ver los usuarios')
        self.assertEqual(request._status, '200 OK', 'Error al obtener los usuarios como '+ TEST_USER)
        print '*-- Obtiene todos los usuarios -- request result: ' + request._status + ' --*'
        print'*---test 1 usuario---*'
   
    def test_b_crear_usuario(self):
        """ Prueba de creacion de un usuario y verifica si el usuario fue creado"""
        print '+++ Creacion de usuario +++'
        request = self._crear_usuario(USU, NOM, APE, PASS, PASS, MAIL, DOMICI, TEL, FECHNAC)
        print '*-- datos de prueba ::: ' + USU + ', ' + NOM + ', ' + APE + ', ' + PASS + ', ' + MAIL +', '+ DOMICI +', '+ TEL +', '+str(FECHNAC)+' --*'
        self.assertNotIn('Sin permisos para agregar usuarios', request.data, 'No tiene permisos para crear usuarios')
        self.assertNotIn('Las contrasenhas deben coincidir', request.data, 'Las contrasenhas no coinciden')
        self.assertNotIn('Error', request.data, 'Tiene errores el form')
        self.assertIn('El Usuario ha sido registrado con exito', request.data, 'Error al crear usuario')
        print '*-- request result: ' + request._status + ' --*'
        self.assertIn(USU, request.data, 'El usuario creado no se encuentra en la tabla')
        print '*-- '+ USU +' creado correctamente, aparece en la tabla de usuarios--*'
        print '*---test 2 usuario---*'
 
    def test_c_crear_usuario_duplicado(self):
        """Prueba si se pueden crear usuarios duplicados"""
        print '+++ Creacion de usuario con usuario(nick) repetido +++'
        request = self._crear_usuario(USU, NOM, APE, PASS, PASS, MAIL, DOMICI, TEL, FECHNAC)
        print '*-- datos de prueba ::: ' + USU + ', ' + NOM + ', ' + APE + ', ' + PASS + ', ' + MAIL +', '+ DOMICI +', '+ TEL +', '+str(FECHNAC)+' --*'
        self.assertNotIn('Sin permisos para agregar usuarios', request.data, 'No tiene permisos para crear usuarios')
        self.assertIn('Clave unica violada por favor ingrese otro USUARIO para el registro', request.data, 'Usuario creado, no existe el usuario(nick) del nuevo usuario')
        print '*-- Verificacion completa, no se pueden crear dos usuarios con el mismo usuario --*'
        print '*---test 3 usuario---*'
 
    def test_d_buscar_proyecto(self):
        """Prueba de busqueda de un usuario"""
        print '+++ Buscar un usuario existente por usuario+++'
        request = self._buscar_usuario(PATRON, PARAM)
        print '*-- datos de prueba ::: patron = '+ PATRON +', parametro = '+PARAM+' --*'
        self.assertNotIn('Sin permisos para buscar usuarios', request.data, 'No tiene permisos para ver los usuarios')
        self.assertNotIn('Sin registro de usuarios', request.data, 'No se encontro un usuario con dicho parametro')
        self.assertIn(PATRON, request.data, 'El usuario no existe en la tabla')
        print '*-- Usuario encontrado exitosamente --*'
        print '*---test 4 usuario---*'
        
    def test_e_editar_usuario(self):
        """Prueba de edicion de un usuario"""        
        print '+++ Editar usuario existente +++'
        request = self._editar_usuario(USU, MODNOM, APE, PASS, PASS, MAIL, DOMICI, TEL, FECHNAC)
        print '*-- datos de prueba ::: ' + USU + ', ' + MODNOM + ', ' + APE + ', ' + PASS + ', ' + MAIL +', '+ DOMICI +', '+ TEL +', '+str(FECHNAC)+' --*'
        self.assertNotIn('Sin permisos para editar usuarios', request.data, 'No tiene permisos para editar usuario')
        self.assertIn('El usuario ha sido modificado con exito', request.data, 'Error al modificar usuario')  
        self.assertIn(MODNOM,request.data,'El usuario no se encuentra editado en la tabla')
        print '*-- Usuario editado correctamente --*'
        print '*---test 5 usuario---*'

    def test_f_eliminar_usuario(self):
        """Prueba de verificacion si se puede eliminar un usuario"""
        print '+++ Eliminacion de usuario existente +++'
        borrar_request = self._eliminar_usuario(USU)
        print '*-- datos de prueba ::: usuario = ' + USU +' --*'
        self.assertNotIn('Sin permisos para eliminar usuarios', borrar_request.data, 'No tiene permisos eliminar usuarios')
        self.assertIn('El usuario ha sido eliminado con exito', borrar_request.data, 'Usuario creado, no existe el usuario(nick) del usuario')
        self.assertNotIn(USU, borrar_request.data, 'El usuario no ha sido borrado')
        print '*-- Verificacion completa, se elimino correctamente--*'
        print '*---test 6 usuario---*'
        print '##----++++ FIN PRUEBA UNITARIA USUARIO ++++----##'
        
    def _get(self, url ='/usuario/administrarusuario'):
        """obtiene la pagina administrar usuarios """
        return self.client.get(url, follow_redirects=True)        
    
    def _crear_usuario(self,usuario=USU, nombre=NOM, apellido=APE, password=PASS, confirmar= PASS, correo=MAIL, 
                 domicilio=DOMICI, telefono=TEL, fecha_nac = FECHNAC):     
        request = self.client.post('/usuario/nuevousuario', data=dict(
            usuario = usuario,
            password = password,
            confirmar = confirmar,
            nombre = nombre,
            apellido = apellido,
            correo = correo,
            domicilio = domicilio,
            telefono = telefono,
            fecha_nac= fecha_nac), follow_redirects=True)
        return request
    
    def _buscar_usuario(self, patron = PATRON , parametro = PARAM ):
        request = self.client.get('/usuario/buscarusuario?patron='+patron+'&parametro='+parametro+'&Buscar=Buscar', follow_redirects=True)
        return request
    
    def _editar_usuario(self, usuario=USU, nombre=MODNOM, apellido=APE, password=PASS, confirmar=PASS, correo=MAIL, 
                 domicilio=DOMICI, telefono=TEL, fecha_nac=FECHNAC):     
        request = self.client.post('/usuario/editarusuario', data=dict(
            usuario = usuario,
            password = password,
            confirmar = confirmar,
            nombre = nombre,
            apellido = apellido,
            correo = correo,
            domicilio = domicilio,
            telefono = telefono,
            fecha_nac= fecha_nac), follow_redirects=True)
        return request

    def _eliminar_usuario(self, usuario=USU):     
        request = self.client.post('/usuario/eliminarusuario?usu='+usuario, follow_redirects=True)
        return request
        
if __name__ == '__main__':
    unittest.main()