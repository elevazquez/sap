from wtforms import Form, TextField, validators, DateField, IntegerField
from sqlalchemy.orm import scoped_session, sessionmaker
from util.database import engine
db_session = scoped_session(sessionmaker(autocommit=False,
                                       autoflush=False,
                                       bind=engine))

class LineaBaseModifFormulario(Form):  
    id = IntegerField('Id', [validators.Required()])     
    descripcion = TextField('Descripcion', [validators.Length(min=2, max=100), validators.Required()])
    estado= TextField('Estado',[validators.Required()])     
    fecha_creacion = DateField('Fecha', format='%Y-%m-%d' )
    fecha_ruptura= DateField('Fecha Ruptura', format='%Y-%m-%d' )
    