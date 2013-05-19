from loginC import app
from collections import namedtuple
from flask_principal import Permission, ItemNeed
from util.database import engine
from sqlalchemy.orm import scoped_session, sessionmaker

#crea un subtipo de tupla llamado permiso_edit,cuyo nombre de campos son method y value
RecursoNeed = namedtuple('permiso_edit', ['method', 'value'])
#crea un objeto partial, que cuando se llama va a comportarse como "PermisoNeed" llamada con los argumentos posicionales 'edit'
#ManageRecursoNeed = partial(PermisoNeed, 'edit')

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

class UserPermission(Permission):
    def __init__(self, action, idr):
        need = ItemNeed(action, idr, 'manage')
        super(UserPermission, self).__init__(need)

    # Assuming the User model has a list of posts the user
    # has authored, add the needs to the identity
    #===========================================================================
    # for post in current_user.posts:
    #    identity.provides.add(EditPermisoNeed(unicode(post.id)))
    #===========================================================================