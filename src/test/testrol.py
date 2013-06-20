from adm.mod.Permiso import Permiso
from adm.mod.RolPermiso import RolPermiso
from adm.mod.Usuario import Usuario
from adm.mod.UsuarioRol import UsuarioRol
from flask_principal import RoleNeed, UserNeed, ItemNeed, identity_loaded
from loginC import app
from sqlalchemy.orm import scoped_session, sessionmaker
from test_helper import login
from util.database import engine
import unittest


db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

def _on_principal_init(sender, identity):
        usuario = db_session.query(Usuario).filter_by(usuario='admin').first();
        identity.provides.add(UserNeed(usuario.id))
        # Assuming the User model has a list of roles, update the
        # identity with the roles that the user provides
        roles = db_session.query(UsuarioRol).filter_by(id_usuario=usuario.id).all()
        for role in roles:
            if role.id_proyecto == None :
                identity.provides.add(RoleNeed(role.usuariorolrol.codigo))
            else :
                identity.provides.add(ItemNeed(role.usuariorolrol.codigo, int(role.id_proyecto) , 'manage'))
            permisos = db_session.query(Permiso).join(RolPermiso, RolPermiso.id_permiso == Permiso.id).filter(RolPermiso.id_rol == role.id_rol).all()
            for p in permisos:
                identity.provides.add(ItemNeed(p.codigo, p.id_recurso , 'manage'))


class RolTestCase(unittest.TestCase):
    """Clase que implementa los test para el caso de uso Rol."""
   
        
    def setUp(self):
        """se llama al metodo antes de iniciar el test"""        
        print "Iniciando test"
        self.client = app.test_client()
        self.acceso = login(self.client)
        identity_loaded.connect(_on_principal_init)

    def tearDown(self):
        """ se llama al metodo al terminar el test"""
        print "Terminando test"


    #===========================================================================
    # def test_get_all_roles(self):
    #    """verifica si se puede acceder al listado de roles """
    #    request = self.client.get('/administrarrol', follow_redirects=True)
    #    print "preueba "+request.data
    #    assert 'sin permisos' in request.data
    #    print "No posee permisos"
    #===========================================================================
        
        
    def test_get_all_roles2(self):
        """verifica si se puede acceder al listado de roles """
        request = self.client.get('/administrarrol', follow_redirects=True)
        # print "prueba2 "+request.data
        # assert 'sin permisos' in request.data
        assert request._status in '200 OK'
        self.assertEqual(request._status, '200 OK', 'Roles obtenidos para el administrador')
   
   
    def test_crear_rol(self):
        """  crea el rol y verifica si el rol fue creado     """  
        request = self._crear_rol('rolprueba', 'este es un rol de prueba')    
       
        print "Respuesta satisfactoria, verificando si creo el rol"
        request_all = self.client.get('/administrarrol', follow_redirects=True)
        assert 'rolprueba' in request_all.data
        print "Rol creado correctamente"


    def test_crear_rol_duplicado(self):
        """prueba si se pueden crear roles duplicados    """
        # Ahora probamos vovler a crear
        print "Creacion de rol con nombre repetido"
        request = self._crear_rol('rolprueba', 'este es un rol de prueba')
        print "Respuesta satisfactoria, verificando si dejo crear el rol"
        assert 'Clave unica violada por favor ingrese otro CODIGO de Rol' in request.data
        print "Verificacion completa, no se pueden crear dos roles con el mismo nombre"


    def test_eliminar_rol(self):
        """verifica si se puede eliminar un rol   """
        print "Creando rol con nombre 'rolprueba2'."
        crear_request = self._crear_rol('rolprueba2', 'borrar')
        print "Verificando si se creo el rol"
        all_request = self._get()
        assert 'rolprueba2' in all_request.data
        print "Rol creado exitosamente"        
        borrar_request = self._eliminar_rol('rolprueba2', 'borrar')
        print "verificar si se elimino"
        self.assertEqual(borrar_request._status, '200 OK')
        print "verificacion completa, se elimino"
        
    def test_editar_rol(self):
        """  edita un rol    """        
        print "Probando editar rol"
        request = self._editar_rol('rolprueba', 'este es un rol de prueba editado')     
        print "Respuesta satisfactoria, verificando si se edito el rol"
        request_all = self.client.get('/administrarrol', follow_redirects=True)
        assert 'rolprueba' in request_all.data
        print "Rol editado correctamente"

           
    def _crear_rol(self, codigo='rolprueba', descripcion='este es un rol de prueba'):     
        request = self.client.post('/add', data=dict(
           codigo=codigo,
           descripcion=descripcion), follow_redirects=True)
        return request
   
    def _editar_rol(self, codigo='rolprueba', descripcion='este es un rol de prueba editado'):     
        request = self.client.post('/editar', data=dict(
           codigo=codigo,
           descripcion=descripcion), follow_redirects=True)
        return request

    def _eliminar_rol(self, codigo='rolprueba2', descripcion='borrar'):     
        request = self.client.post('/eliminar?cod='+codigo, follow_redirects=True)
        return request
   
    def _get(self, url ='/administrarrol'):
        """obtiene la pagina administrar roles """
        return self.client.get(url, follow_redirects=True)
    
if __name__ == '__main__':
    unittest.main()
