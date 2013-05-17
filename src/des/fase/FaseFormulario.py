from wtforms import Form, TextField, validators, IntegerField, SelectField, DateField
from des.mod.Fase import Fase
from util.database import engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import func, Integer
from flask import session 

db_session = scoped_session(sessionmaker(autocommit=False,
                                       autoflush=False,
                                       bind=engine))
#db_session.query(func.max(Fase.nro_orden, type_=Integer)).filter_by(id_proyecto=session['pry']).scalar()+1
#, default=1
class FaseFormulario(Form):
    nro_orden = IntegerField('Numero Orden', [validators.Required()]) 
    nombre = TextField('Nombre', [validators.Length(min=2, max=50), validators.Required()])
    descripcion = TextField('Descripcion', [validators.Length(min=2, max=100), validators.Required()])
    estado = TextField('Estado')
    #estado = SelectField('Estado', choices=[('I', 'Inicial'), ('P', 'En Progreso'), ('L', 'En Linea Base'), ('A', 'Aprobado')])
    fecha_inicio = DateField('Fecha Inicio', format='%Y-%m-%d')
    fecha_fin = DateField('Fecha Fin', format='%Y-%m-%d' )
    id_proyecto = TextField('Proyecto')
#,coerce=int