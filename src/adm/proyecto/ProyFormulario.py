from wtforms import Form, TextField, validators, IntegerField, SelectField, DateField
from adm.mod.Usuario import Usuario
from util.database import engine
from sqlalchemy.orm import scoped_session, sessionmaker

db_session = scoped_session(sessionmaker(autocommit=False,
                                       autoflush=False,
                                       bind=engine))

class ProyFormulario(Form):
    nombre = TextField('Nombre', [validators.Length(min=2, max=50), validators.Required()])
    descripcion = TextField('Descripcion', [validators.Length(min=2, max=100), validators.Required()])
    estado = TextField('Estado', default='Nuevo')
    #estado = SelectField('Estado', choices=[('N', 'Nuevo'), ('P', 'En Progreso'), ('A', 'Anulado'), ('F', 'Finalizado')])
    cant_miembros = IntegerField('Cantidad Miembros', [validators.Required()]) 
    fecha_inicio = DateField('Fecha Inicio', format='%Y-%m-%d' )
    fecha_fin = DateField('Fecha Fin', format='%Y-%m-%d' )
    fecha_ultima_mod = DateField('Fecha Ultima Modificacion', format='%Y-%m-%d' )
    id_usuario_lider = SelectField('Lider de Proyecto', choices=[(u.id, u.nombre + " " + u.apellido) for u in db_session.query(Usuario).order_by(Usuario.nombre)], coerce=int)