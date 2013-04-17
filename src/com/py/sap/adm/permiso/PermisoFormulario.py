from wtforms import Form, TextField, validators, SelectField
from com.py.sap.adm.mod.Recurso import Recurso
from com.py.sap.util.database import init_db, engine
from sqlalchemy.orm import scoped_session, sessionmaker

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

class PermisoFormulario(Form):
    codigo = TextField('Codigo', [validators.Length(min=1, max=50), validators.Required()])
    descripcion = TextField('Descripcion', [validators.Length(min=2, max=100)])
    recurso = SelectField('Recurso', choices=[(r.id,r.nombre) for r in db_session.query(Recurso).order_by(Recurso.nombre)])