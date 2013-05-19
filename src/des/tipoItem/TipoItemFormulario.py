from wtforms import Form, TextField, validators, SelectField, SelectMultipleField
from des.mod.Fase import Fase
from des.mod.Atributo import Atributo
from util.database import engine
from sqlalchemy.orm import scoped_session, sessionmaker
from wtforms import widgets

db_session = scoped_session(sessionmaker(autocommit=False,
                                       autoflush=False,
                                       bind=engine))

class TipoItemFormulario(Form):
    codigo = TextField('Codigo', [validators.Length(min=1, max=50), validators.Required()])
    nombre = TextField('Nombre', [validators.Length(min=2, max=50), validators.Required()])
    descripcion = TextField('Descripcion', [validators.Length(min=2, max=100), validators.Required()])
    id_fase = SelectField('Fase',choices= [(f.id, f.nombre) for f in db_session.query(Fase)],coerce=int)                      
    lista_atributo = SelectMultipleField( 'Atributos', choices = [(f.id, f.nombre) for f in db_session.query(Atributo)],coerce=int)
    #,choices=[(f.id, f.nombre) for f in db_session.query(Atributo).order_by(Atributo.nombre).all()],
    #                                       option_widget= widgets.CheckboxInput())