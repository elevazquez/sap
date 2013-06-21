from wtforms import Form, TextField, validators, IntegerField, SelectField, DateField, TextAreaField
from adm.mod.Usuario import Usuario
from util.database import engine
from sqlalchemy.orm import scoped_session, sessionmaker

db_session = scoped_session(sessionmaker(autocommit=False,
                                       autoflush=False,
                                       bind=engine))

class ListaItemFormulario(Form):
    fecha = DateField('Fecha' )
    