from loginC import app
from flask_principal import Permission, ItemNeed
from util.database import engine
from sqlalchemy.orm import scoped_session, sessionmaker

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

class UserPermission(Permission):
    def __init__(self, action, idr):
        need = ItemNeed(action, idr, 'manage')
        super(UserPermission, self).__init__(need)