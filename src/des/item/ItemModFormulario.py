from wtforms import Form, TextField, validators, IntegerField, SelectField, DateField,DecimalField
from adm.mod.Usuario import  Usuario
from des.mod.Fase import Fase
from des.mod.TipoItem import TipoItem
from sqlalchemy.orm import scoped_session, sessionmaker
from util.database import engine

db_session = scoped_session(sessionmaker(autocommit=False,
                                       autoflush=False,
                                       bind=engine))

class ItemModFormulario(Form): 
    codigo = TextField('Codigo', [validators.Length(min=2, max=50), validators.Required()])    
    nombre = TextField('Nombre', [validators.Length(min=2, max=50), validators.Required()])
    descripcion = TextField('Descripcion', [validators.Length(min=2, max=100), validators.Required()])
    #estado= TextField('Estado',[validators.Required()])
    estado = SelectField('Estado', choices=[('I', 'Abierto'), ('P', 'En Progreso'), ('R', 'Resuelto'), ('A', 'Aprobado'), 
                                          ('Z', 'Rechazado'), ('V', 'Revision'),  ('B', 'Bloqueado')   ])
    
    complejidad = IntegerField('Complejidad', [validators.Required()]) 
    fecha = DateField('Fecha', format='%Y-%m-%d' )
    costo = DecimalField('Costo', [validators.Required()]) 
    version = IntegerField('Version', [validators.Required()]) 
    usuario = IntegerField('Usuario', [validators.Required()]) 
    fase = TextField('Fase',[validators.Required()])   
    tipo_item = TextField('Tipo Item',[validators.Required()]) 
    