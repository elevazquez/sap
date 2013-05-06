from wtforms import Form, TextField, validators, IntegerField, SelectField, DateField
from adm.mod.Usuario import  Usuario
from des.mod.Fase import Fase
from des.mod.TipoItem import TipoItem
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
    fase = SelectField('Fase', choices=[(f.id,f.nombre) for f in db_session.query(Fase).order_by(Fase.nombre).all()], coerce=int)   
    tipo_item = SelectField('Tipo Item', choices=[(f.id, f.nombre) for f in db_session.query(TipoItem).order_by(TipoItem.nombre).all()],coerce=int) 
   
   # archivo= bytearray('Archivo',[validators.Required()] )
   # mime= TextField('Mime',[validators.Length(min=2, max=15), validators.Required()])
    
    
    