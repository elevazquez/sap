from wtforms import Form, TextField, validators, IntegerField, DateField,DecimalField
from adm.mod.Usuario import  Usuario
from des.mod.Fase import Fase
from des.mod.TipoItem import TipoItem
from sqlalchemy.orm import scoped_session, sessionmaker
from util.database import engine

db_session = scoped_session(sessionmaker(autocommit=False,
                                       autoflush=False,
                                       bind=engine))

class ItemEditarFormulario(Form): 
    id = IntegerField('Id', [validators.Required()])  
    codigo = TextField('Codigo', [validators.Length(min=2, max=50), validators.Required()])    
    nombre = TextField('Nombre', [validators.Length(min=2, max=50), validators.Required()])
    descripcion = TextField('Descripcion', [validators.Length(min=2, max=100), validators.Required()])
    estado= TextField('Estado',[validators.Required()])
    complejidad = IntegerField('Complejidad', [validators.Required()]) 
    fecha = DateField('Fecha', format='%Y-%m-%d' )
    costo = DecimalField('Costo', [validators.Required()]) 
    version = IntegerField('Version', [validators.Required()]) 
    usuario = IntegerField('Usuario', [validators.Required()]) 
    fase = TextField('Fase',[validators.Required()])   
    id_fase_f = IntegerField('Id_fase', [validators.Required()]) 
    tipo_item = TextField('Tipo Item',[validators.Required()]) 
    id_tipo_f = IntegerField('Id_tipo', [validators.Required()])
    