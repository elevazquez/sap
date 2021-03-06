from wtforms import Form, TextField, validators, SelectField
from des.mod.TipoAtributo import TipoAtributo
from util.database import engine
from sqlalchemy.orm import scoped_session, sessionmaker

db_session = scoped_session(sessionmaker(autocommit=False,
                                       autoflush=False,
                                       bind=engine))

class AtributoFormulario(Form):
    nombre = TextField('Nombre', [validators.Length(min=2, max=50), validators.Required()])
    descripcion = TextField('Descripcion', [validators.Length(min=2, max=100), validators.Required()])
    id_tipo_atributo = SelectField('Tipo', choices=[(r.id, r.nombre) for r in db_session.query(TipoAtributo).order_by(TipoAtributo.nombre).all()], coerce=int)