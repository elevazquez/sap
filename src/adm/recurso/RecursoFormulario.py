from wtforms import Form, TextField, validators, SelectField, IntegerField
from des.mod.Fase import Fase
from adm.mod.Proyecto import Proyecto
from util.database import engine
from sqlalchemy.orm import scoped_session, sessionmaker

db_session = scoped_session(sessionmaker(autocommit=False,
                                       autoflush=False,
                                       bind=engine))

class RecursoFormulario(Form):
    nombre = TextField('Nombre', [validators.Length(min=2, max=100), validators.Required()])
    id_proyecto = TextField('Proyecto')
    id_fase = TextField('Fase')
    recurso = TextField('Recurso')
    param = TextField('Param')
    id = TextField('id Recurso')