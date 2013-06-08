from wtforms import Form, TextField, validators, SelectField
from des.mod.Fase import Fase
from adm.mod.Proyecto import Proyecto
from util.database import engine
from sqlalchemy.orm import scoped_session, sessionmaker

db_session = scoped_session(sessionmaker(autocommit=False,
                                       autoflush=False,
                                       bind=engine))

class RecursoFormulario(Form):
    nombre = TextField('Nombre', [validators.Length(min=2, max=100), validators.Required()])
    #id_fase = SelectField('Fase', choices=[(r.id, r.nombre) for r in db_session.query(Fase).order_by(Fase.nombre)], coerce=int)
    id_proyecto = TextField('Proyecto')
    id_fase = TextField('Proyecto')
    