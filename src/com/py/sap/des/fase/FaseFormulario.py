from wtforms import Form, TextField, validators, IntegerField, SelectField, DateField
from com.py.sap.adm.mod.Proyecto import Proyecto

class FaseFormulario(Form):
    nro_orden = IntegerField('Numero Orden', [validators.Required()]) 
    nombre = TextField('Nombre', [validators.Length(min=2, max=50), validators.Required()])
    descripcion = TextField('Descripcion', [validators.Length(min=2, max=100), validators.Required()])
    estado = SelectField('Estado', choices=[('I', 'Inicial'), ('P', 'En Progreso'), ('L', 'En Linea Base'), ('A', 'Aprobado')], default='2')
    fecha_inicio = DateField('Fecha Inicio', format='%Y-%m-%d' )
    fecha_fin = DateField('Fecha Fin', format='%Y-%m-%d' )
    id_proyecto = IntegerField('Proyecto', [validators.Required()]) 
#,coerce=int