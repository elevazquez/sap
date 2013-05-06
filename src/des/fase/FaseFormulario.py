from wtforms import Form, TextField, validators, IntegerField, SelectField, DateField
from adm.mod.Proyecto import Proyecto
from util.database import engine
from sqlalchemy.orm import scoped_session, sessionmaker

db_session = scoped_session(sessionmaker(autocommit=False,
                                       autoflush=False,
                                       bind=engine))

class FaseFormulario(Form):
    nro_orden = IntegerField('Numero Orden', [validators.Required()]) 
    nombre = TextField('Nombre', [validators.Length(min=2, max=50), validators.Required()])
    descripcion = TextField('Descripcion', [validators.Length(min=2, max=100), validators.Required()])
    estado = SelectField('Estado', choices=[('I', 'Inicial'), ('P', 'En Progreso'), ('L', 'En Linea Base'), ('A', 'Aprobado')])
    fecha_inicio = DateField('Fecha Inicio', format='%Y-%m-%d')
    fecha_fin = DateField('Fecha Fin', format='%Y-%m-%d' )
    id_proyecto = TextField('Proyecto')
#,coerce=int