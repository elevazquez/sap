from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from com.py.sap.util import configDB

engine = create_engine(configDB.DB_URI)

Base = declarative_base()                                        


def init_db(db_session):
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    Base.query = db_session.query_property()
    from com.py.sap.adm.mod.Rol import Rol
    from com.py.sap.adm.mod.Usuario import Usuario
    from com.py.sap.adm.mod.Recurso import Recurso
    from com.py.sap.adm.mod.Proyecto import Proyecto
    Base.metadata.create_all(bind=engine)
    
