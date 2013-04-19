from wtforms import Form, TextField, validators, IntegerField, SelectField, DateField
from com.py.sap.adm.mod.Proyecto import Proyecto
from com.py.sap.adm.mod.Usuario import Usuario

class ProyFormulario(Form):
    nombre = TextField('Nombre', [validators.Length(min=2, max=50), validators.Required()])
    descripcion = TextField('Descripcion', [validators.Length(min=2, max=100), validators.Required()])
    estado = SelectField('Estado', choices=[('N', 'Nuevo'), ('P', 'En Progreso'), ('A', 'Anulado'), ('F', 'Finalizado')])
    cant_miembros = IntegerField('Cantidad Miembros', [validators.Required()]) 
    fecha_inicio = DateField('Fecha Inicio', format='%Y-%m-%d' )
    fecha_fin = DateField('Fecha Fin', format='%Y-%m-%d' )
    fecha_ultima_mod = DateField('Fecha Ultima Modificacion', format='%Y-%m-%d' )
    id_usuario_lider = IntegerField('Usuario Lider', [validators.Required()]) 
