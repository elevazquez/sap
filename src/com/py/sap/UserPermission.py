from com.py.sap.loginC import app
from collections import namedtuple
from functools import partial

from flask_login import current_user
from flask_principal import identity_loaded, Permission, RoleNeed, UserNeed
from com.py.sap.util.database import engine
from sqlalchemy.orm import scoped_session, sessionmaker
from com.py.sap.adm.mod.UsuarioRol import *

PermisoNeed = namedtuple('permiso_edit', ['method', 'value'])
EditPermisoNeed = partial(PermisoNeed, 'edit')

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

class UserPermission(Permission):
    def __init__(self, post_id):
        need = EditPermisoNeed(unicode(post_id))
        super(UserPermission, self).__init__(need)

@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    # Set the identity user object
    identity.user = current_user

    # Add the UserNeed to the identity
    if hasattr(current_user, 'id'):
        identity.provides.add(UserNeed(current_user.id))

    # Assuming the User model has a list of roles, update the
    # identity with the roles that the user provides
    roles = db_session.query(UsuarioRol).filter_by(codigo=current_user.id).all()
    for role in roles:
        identity.provides.add(RoleNeed(role.usuario.rol.codigo))

    # Assuming the User model has a list of posts the user
    # has authored, add the needs to the identity
    for post in current_user.posts:
        identity.provides.add(EditPermisoNeed(unicode(post.id)))