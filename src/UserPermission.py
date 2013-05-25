from loginC import app
from flask_principal import Permission, ItemNeed, RoleNeed
from util.database import engine
from sqlalchemy.orm import scoped_session, sessionmaker

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

class UserPermission(Permission):
    def __init__(self, action, idr):
        needPermiso = ItemNeed(action, idr, 'manage')
        super(UserPermission, self).__init__(needPermiso)
        
class UserRol(Permission):
    def __init__(self, rol):
        need = RoleNeed(rol)
        super(UserRol, self).__init__(need)