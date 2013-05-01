from wtforms import Form, TextField, validators, IntegerField, SelectField, DateField
from com.py.sap.adm.mod.Usuario import  Usuario
from com.py.sap.des.mod.Fase import Fase
from com.py.sap.des.mod.TipoItem import TipoItem
from sqlalchemy.orm import scoped_session, sessionmaker
from com.py.sap.util.database import engine

db_session = scoped_session(sessionmaker(autocommit=False,
                                       autoflush=False,
                                       bind=engine))

class ItemFormulario(Form):
    codigo = TextField('Codigo', [validators.Length(min=2, max=50), validators.Required()])    
    nombre = TextField('Nombre', [validators.Length(min=2, max=50), validators.Required()])
    descripcion = TextField('Descripcion', [validators.Length(min=2, max=100), validators.Required()])
    estado = SelectField('Estado', choices=[('I', 'Abierto'), ('P', 'En Progreso'), ('R', 'Resuelto'), ('A', 'Aprobado'), 
                                          ('Z', 'Rechazado'), ('E', 'Eliminado'), ('V', 'Revision'),  ('B', 'Bloqueado')   ])
    complejidad = IntegerField('Complejidad', [validators.Required()]) 
    fecha = DateField('Fecha', format='%Y-%m-%d' )
    costo = IntegerField('Costo', [validators.Required()]) 
    version = IntegerField('Version', [validators.Required()]) 
    id_usuario = IntegerField('Usuario', [validators.Required()]) 
    id_fase = SelectField('Fase', choices=[(f.id, f.nombre) for f in db_session.query(Fase).order_by(Fase.nombre).all()], coerce=int)  
  #  id_tipo_item = SelectField('Tipo Item', choices=[(f.id, f.nombre) for f in db_session.query(TipoItem).filter_by(id_fase= id_fase.id).all()], coerce=int)
                                                     #from_statement("select i.* from tipo_item i, fase fa where i.id_fase = fa.id and fa.id= "+id_fase+" order by i.nombre").all()], coerce=int)
    
    
    #id_tipo_item = SelectField('Tipo Item', choices=[(f.id, f.nombre) for f in db_session.query(TipoItem).order_by(TipoItem.nombre).all()], coerce=int)
    
   # archivo= bytearray('Archivo',[validators.Required()] )
   # mime= TextField('Mime',[validators.Length(min=2, max=15), validators.Required()])
    
    
    