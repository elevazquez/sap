from loginC import app
from collections import namedtuple
from functools import partial

from flask_login import current_user
from flask_principal import Permission, RoleNeed
from util.database import engine
from sqlalchemy.orm import scoped_session, sessionmaker

#crea un subtipo de tupla llamado permiso_edit,cuyo nombre de campos son method y value
PermisoNeed = namedtuple('permiso_edit', ['method', 'value'])
#crea un objeto partial, que cuando se llama va a comportarse como "PermisoNeed" llamada con los argumentos posicionales 'edit'
EditPermisoNeed = partial(PermisoNeed, 'edit')

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

class UserPermission(Permission):
    def __init__(self, rol):
        need = RoleNeed(unicode(rol))
        super(UserPermission, self).__init__(need)

    # Assuming the User model has a list of posts the user
    # has authored, add the needs to the identity
    #===========================================================================
    # for post in current_user.posts:
    #    identity.provides.add(EditPermisoNeed(unicode(post.id)))
    #===========================================================================