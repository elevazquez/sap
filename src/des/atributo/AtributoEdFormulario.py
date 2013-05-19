from wtforms import Form, TextField, validators
from util.database import engine
from sqlalchemy.orm import scoped_session, sessionmaker

db_session = scoped_session(sessionmaker(autocommit=False,
                                       autoflush=False,
                                       bind=engine))

class AtributoEdFormulario(Form):
    nombre = TextField('Nombre', [validators.Length(min=2, max=50), validators.Required()])
    descripcion = TextField('Descripcion', [validators.Length(min=2, max=100), validators.Required()])
    id_tipo_atributo = TextField('Tipo',[validators.Required()])