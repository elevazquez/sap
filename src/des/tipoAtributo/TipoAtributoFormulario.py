from wtforms import Form, TextField, validators, IntegerField, SelectField, DateField
from des.mod.TipoAtributo import TipoAtributo
from util.database import engine
from sqlalchemy.orm import scoped_session, sessionmaker

db_session = scoped_session(sessionmaker(autocommit=False,
                                       autoflush=False,
                                       bind=engine))
class TipoAtributoFormulario(Form):
    codigo = TextField('Codigo', [validators.Length(min=1, max=50), validators.Required()])
    nombre = TextField('Nombre', [validators.Length(min=2, max=50), validators.Required()])
    descripcion = TextField('Descripcion', [validators.Length(min=2, max=100), validators.Required()])