from wtforms import Form, TextField, validators, IntegerField, SelectField, DateField, PasswordField
from adm.mod.Usuario import Usuario
from util.database import engine
from sqlalchemy.orm import scoped_session, sessionmaker

db_session = scoped_session(sessionmaker(autocommit=False,
                                       autoflush=False,
                                       bind=engine))

class MiembrosComiteFormulario(Form):
    usuario = TextField('Usuario', [validators.Length(min=2, max=50), validators.Required()])
    nombre = TextField('Nombre', [validators.Length(min=2, max=100), validators.Required()])
    apellido = TextField('Apellido', [validators.Length(min=2, max=100), validators.Required()])
    correo = TextField('Correo', [validators.Length(min=2, max=100), validators.Required(), validators.Email()])
    domicilio = TextField('Domicilio', [validators.Length(min=2, max=150), validators.Required()])
    telefono = TextField('Telefono', [validators.Length(min=2, max=50), validators.Required()])
    fecha_nac = DateField('Fecha Nacimiento', format='%Y-%m-%d' )