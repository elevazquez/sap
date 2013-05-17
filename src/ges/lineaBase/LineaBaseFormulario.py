from wtforms import Form, TextField, validators, IntegerField, SelectField, DateField, FileField
from adm.mod.Usuario import  Usuario
from des.mod.Fase import Fase
from des.mod.TipoItem import TipoItem
from sqlalchemy.orm import scoped_session, sessionmaker
from util.database import engine
db_session = scoped_session(sessionmaker(autocommit=False,
                                       autoflush=False,
                                       bind=engine))

class LineaBaseFormulario(Form):  
    descripcion = TextField('Descripcion', [validators.Length(min=2, max=100), validators.Required()])
    estado = SelectField('Estado', choices=[('V', 'Valido')])
                                    #        , ('N', 'No Valido'), ('L', 'Liberado')  ])
     
    fechaCreacion = DateField('Fecha', format='%Y-%m-%d' )
   
    