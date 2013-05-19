from wtforms import Form, TextField, validators, SelectField
from des.mod.Fase import Fase
from util.database import engine
from sqlalchemy.orm import scoped_session, sessionmaker

db_session = scoped_session(sessionmaker(autocommit=False,
                                       autoflush=False,
                                       bind=engine))

class PermisoFormulario(Form):
    codigo = TextField('Codigo', [validators.Length(min=1, max=50), validators.Required()])
    descripcion = TextField('Descripcion', [validators.Length(min=2, max=100)])
    id_fase = SelectField('Fase', choices=[(r.id, r.nombre) for r in db_session.query(Fase).order_by(Fase.nombre)], coerce=int)