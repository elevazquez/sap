from wtforms import Form, TextField, validators, IntegerField, SelectField, DateField, TextAreaField
from adm.mod.Usuario import Usuario
from util.database import engine
from sqlalchemy.orm import scoped_session, sessionmaker

db_session = scoped_session(sessionmaker(autocommit=False,
                                       autoflush=False,
                                       bind=engine))

class SolicitudFormulario(Form):
    id = IntegerField('Id')     
    descripcion = TextAreaField('Descripcion', [validators.Length(min=2, max=2000), validators.Required()])
    fecha = DateField('Fecha', format='%Y-%m-%d' )
    estado = TextField('Estado')
    id_usuario = TextField('Usuario')
    id_proyecto = TextField('Proyecto')
    cant_votos = TextField('Votos')