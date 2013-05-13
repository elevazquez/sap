from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from util import configDB

engine = create_engine(configDB.DB_URI)

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()                                        

def init_db(db_session):
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    Base.query = db_session.query_property()
    #===========================================================================
    # from adm.mod.Rol import Rol
    # from adm.mod.Usuario import Usuario
    # from adm.mod.Permiso import Permiso
    # from adm.mod.Recurso import Recurso
    # from ges.mod.Relacion import Relacion
    # from des.mod.Item import Item
    #===========================================================================
    Base.metadata.create_all(bind=engine)
    
