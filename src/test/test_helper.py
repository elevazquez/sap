from adm.mod.Permiso import Permiso
from adm.mod.RolPermiso import RolPermiso
from adm.mod.Usuario import Usuario
from adm.mod.UsuarioRol import UsuarioRol
from adm.mod.Recurso import Recurso
from adm.mod.MiembrosComite import MiembrosComite
from flask_principal import RoleNeed, UserNeed, ItemNeed, identity_changed, AnonymousIdentity, current_app
from util.database import engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import session

#cambiar estos usuarios segun la base de datos
TEST_USER = 'testadmin'
TEST_PASS = 'test'

TEST_USER_LIDER = 'testlider'
TEST_PASS_LIDER = 'test'

TEST_USER_DESA = 'testdesa'
TEST_PASS_DESA = 'test'

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

def login(app, usuario=TEST_USER, password=TEST_PASS):
    """
    Este metodo realiza el test de ingreso a la pagina login de la aplicacion
    @param app: la aplicacion
    @param nombre: nombre de usuario
    @param contrasenha: contrasenha del usuario
    """

    access = app.post('/', data=dict(
        username=usuario,
        passwd=password
        ), follow_redirects=True)
    return access

def logout(app):
    """Este metodo se encarga de desloguear
    @param app: la aplicacion """
    out = app.post('/logout', follow_redirects=True)
    return out

def _on_principal_init(sender, identity):
        usuario = db_session.query(Usuario).filter_by(usuario=TEST_USER).first();
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
                
def _on_principal_initL(sender, identity):
        usuario = db_session.query(Usuario).filter_by(usuario=TEST_USER_LIDER).first();
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

def _on_principal_final():
    for key in ('identity.name', 'identity.auth_type'):
        session.pop(key, None)
    #Tell Flask-Principal the user is anonymous
    identity_changed.send(current_app._get_current_object(),
            identity=AnonymousIdentity())

def seleccionar_proyecto(app,idpro):
    request = app.get('/proyectoActual?pyo='+str(idpro), follow_redirects=True)
    return request

def getRecursoByNombre(nombre=None):
    return db_session.query(Recurso).filter_by(nombre=nombre).first()

def getIdUsuario(usua=None):
    usu=db_session.query(Usuario).filter_by(usuario=usua).first()
    print str(usu.id)
    return usu.id

def getMiembroComite(id_proyecto=None, usua=None):
    return db_session.query(MiembrosComite).filter_by(id_proyecto=id_proyecto, id_usuario=usua).first()