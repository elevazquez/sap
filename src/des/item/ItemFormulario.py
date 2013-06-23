from wtforms import Form, TextField, validators, IntegerField, SelectField, DateField, FileField
from sqlalchemy.orm import scoped_session, sessionmaker
from util.database import engine
db_session = scoped_session(sessionmaker(autocommit=False,
                                       autoflush=False,
                                       bind=engine))

class ItemFormulario(Form):
    codigo = TextField('Codigo', [validators.Length(min=2, max=50), validators.Required()])    
    nombre = TextField('Nombre', [validators.Length(min=2, max=50), validators.Required()])
    descripcion = TextField('Descripcion', [validators.Length(min=2, max=100), validators.Required()])
    estado = SelectField('Estado', choices=[('I', 'Abierto')])
                                    #        , ('P', 'En Progreso'), ('R', 'Resuelto'), ('A', 'Aprobado'), 
                                    #      ('Z', 'Rechazado'), ('E', 'Eliminado'), ('V', 'Revision'),  ('B', 'Bloqueado')   ])
    complejidad = IntegerField('Complejidad', [validators.Required()]) 
    fecha = DateField('Fecha', format='%Y-%m-%d' )
    costo = IntegerField('Costo', [validators.Required()]) 
    version = IntegerField('Version', [validators.Required()]) 
    usuario = IntegerField('Usuario', [validators.Required()]) 
    archivo=  FileField('Adjuntar Archivo')
    id_tipo_f = IntegerField('Id_tipo', [validators.Required()]) 
    id_fase_f = IntegerField('Id_fase', [validators.Required()])
   
    