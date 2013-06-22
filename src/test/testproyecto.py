from loginC import app

from flask_principal import identity_loaded
from test_helper import login,_on_principal_init, logout, TEST_USER
import datetime
import unittest

NOMBRE = 'prytest'
PARAM = 'nombre'
PATRON = NOMBRE
USERLIDER = 2
TODAY = datetime.date.today()
FECHAINICIO = TODAY
FECHAFIN = '2014-12-30'

#falta finalizar e inicializar proyecto

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
  
    def test_b_crear_proyecto(self):
        """ Prueba de creacion el proyecto y verifica si el proyecto fue creado"""
        print '+++ Creacion de proyecto +++'
        request = self._crear_proyecto(NOMBRE, 'proytesting', 'N', 3, FECHAINICIO, FECHAFIN, TODAY, USERLIDER)
        print '*-- datos de prueba ::: ' + NOMBRE + ', proytesting, N, 3, ' + str(FECHAINICIO) +', '+ str(FECHAFIN) +', '+ str(TODAY) +', ' + str(USERLIDER) +' --*'
        self.assertNotIn('Sin permisos para agregar proyectos', request.data, 'No tiene permisos para crear proyectos')
        self.assertNotIn('Error', request.data, 'Tiene errores el form')
        self.assertIn('El Proyecto ha sido registrado con exito', request.data, 'Error al crear el proyecto')
        print '*-- request result: ' + request._status + ' --*'
        self.assertIn('prytest', request.data, 'El proyecto creado no se encuentra en la tabla')
        print '*-- prytest creado correctamente, aparece en la tabla de proyectos--*'
        print '*---test 2 proyecto---*'
       
    def test_c_crear_proyecto_duplicado(self):
        """ Prueba de crear proyectos con nombre duplicado"""
        print '+++ Creacion de proyecto con nombre duplicado +++'
        request = self._crear_proyecto(NOMBRE, 'proytesting', 'N', 3, FECHAINICIO, FECHAFIN, TODAY, USERLIDER)
        print '*-- datos de prueba ::: ' + NOMBRE + ', proytesting, N, 3, ' + str(FECHAINICIO) +', '+ str(FECHAFIN) +', '+ str(TODAY) +', ' + str(USERLIDER) +' --*'
        self.assertNotIn('Sin permisos para agregar proyectos', request.data, 'No tiene permisos para ver los proyectos')
        self.assertIn('Clave unica violada por favor ingrese otro NOMBRE de Proyecto', request.data, 'Rol creado, no existe el codigo de rol')
        self.assertIn('prytest', request.data, 'El proyecto creado no se encuentra en la tabla')
        print '*-- Verificacion completa, no se pueden crear dos proyectos con el mismo nombre --*'
        print '*---test 3 proyecto---*'

#PARA ELIMINAR UN PROYECTO SE DEBE ELIMINAR EL PERMISO PARA CONSULTA
#ELIMINAR ROL MIEMBRO COMITE SI YA NO TIENE PERMISOS
#ELIMINAR RECURSO PROYECTO
#ELIMINAR ROL USUARIO LIDER PROYECTO
#ELIMINAR MIEMBRO COMITE AL LIDER
    def test_d_buscar_proyecto(self):
        """Prueba de busqueda de un proyecto"""
        print '+++ Buscar un proyecto existente por nombre +++'
        request = self._buscar_proyecto(PATRON, PARAM)
        print '*-- datos de prueba ::: patron = '+ PATRON +', parametro = '+PARAM+' --*'
        self.assertNotIn('Sin permisos para buscar proyectos', request.data, 'No tiene permisos para ver los proyectos')
        self.assertNotIn('Sin registro de proyectos', request.data, 'No se encontro proyectos con dicho parametro')
        self.assertIn(PATRON, request.data, 'El proyecto no existe en la tabla')
        print '*-- Proyecto encontrado exitosamente --*'
        print '*---test 4 proyecto---*'

    def test_e_editar_proyecto(self):     
        """Prueba de edicion de un proyecto"""        
        print '+++ Editar proyecto existente +++'
        request = self._editar_proyecto(NOMBRE, 'proytesting editado', 'Nuevo', 3, FECHAINICIO, FECHAFIN, TODAY, USERLIDER)   
        print '*-- datos de prueba ::: ' + NOMBRE + ', proytesting editado, Nuevo, 3, ' + str(FECHAINICIO) +', '+ str(FECHAFIN) +', '+ str(TODAY) +', ' + str(USERLIDER) +' --*'
        self.assertNotIn('Sin permisos para editar proyectos', request.data, 'No tiene permisos para editar proyecto')
        self.assertIn('El Proyecto ha sido modificado con exito', request.data, 'Error al modificar rol')  
        self.assertIn('proytesting editado',request.data,'El rol no se encuentra editado en la tabla')
        print '*-- Proyecto editado correctamente --*'
        print '*---test 5 proyecto---*'
        
    def test_f_eliminar_proyecto(self):
        """Prueba de verificacion si se puede eliminar un proyecto"""
        print '+++ Eliminacion de proyecto existente +++'
        borrar_request = self._eliminar_proyecto(NOMBRE)
        print '*-- datos de prueba ::: nombre = ' + NOMBRE +' --*'
        self.assertNotIn('Sin permisos para eliminar proyectos', borrar_request.data, 'No tiene permisos para ver los proyectos')
        self.assertIn('El proyecto ha sido eliminado con exito', borrar_request.data, 'Proyecto creado, no existe el nombre del proyecto')
        self.assertNotIn(NOMBRE, borrar_request.data, 'El proyecto no ha sido borrado')
        print '*-- Verificacion completa, se elimino correctamente--*'
        print '*---test 6 proyecto---*'
        print '##----++++ FIN PRUEBA UNITARIA PROYECTO ++++----##'
            
    def _get(self, url ='/proyecto/administrarproyecto'):
        """obtiene la pagina administrar proyectos """
        return self.client.get(url, follow_redirects=True)
    
    def _crear_proyecto(self,nombre=NOMBRE, descripcion='proytesting', estado='N', cant_miembros=3, fecha_inicio=FECHAINICIO,
                        fecha_fin=FECHAFIN, fecha_ultima_mod=TODAY, id_usuario_lider=USERLIDER):     
        request = self.client.post('/proyecto/nuevoproyecto', data=dict(
            nombre = nombre,
            descripcion = descripcion,
            estado = estado,
            cant_miembros = cant_miembros,
            fecha_inicio = fecha_inicio,
            fecha_fin = fecha_fin,
            fecha_ultima_mod = fecha_ultima_mod,
            id_usuario_lider = id_usuario_lider), follow_redirects=True)
        return request
    
    def _editar_proyecto(self, nombre=NOMBRE, descripcion='proytesting editado', estado='Nuevo', cant_miembros=3, fecha_inicio=FECHAINICIO,
                        fecha_fin=FECHAFIN, fecha_ultima_mod= TODAY, id_usuario_lider=USERLIDER):     
        request = self.client.post('/proyecto/editarproyecto', data=dict(
            nombre = nombre,
            descripcion = descripcion,
            estado = estado,
            cant_miembros = cant_miembros,
            fecha_inicio = fecha_inicio,
            fecha_fin = fecha_fin,
            fecha_ultima_mod = fecha_ultima_mod,
            id_usuario_lider = id_usuario_lider), follow_redirects=True)
        return request
    
    def _buscar_proyecto(self, patron = PATRON , parametro = PARAM ):
        request = self.client.get('/proyecto/buscarproyecto?patron='+patron+'&parametro='+parametro+'&Buscar=Buscar', follow_redirects=True)
        return request

    def _eliminar_proyecto(self, nombre=NOMBRE):     
        request = self.client.post('/proyecto/eliminarproyecto?nom='+nombre, follow_redirects=True)
        return request
        
if __name__ == '__main__':
    unittest.main()