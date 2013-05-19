""" Modelo de la tabla Miembros Comite """
from sqlalchemy import *
from sqlalchemy.orm import *
from util.database import Base
from adm.mod.Proyecto import Proyecto
from adm.mod.Usuario import Usuario

class MiembrosComite (Base):
    __tablename__ = 'miembros_comite'
    __table_args__ = {'extend_existing': True}
    id = Column('id', Integer, Sequence('miembros_comite_id_seq'), primary_key=True)
    id_proyecto = Column(Integer, ForeignKey('proyecto.id'))
    miembrosproyecto = relationship(Proyecto, backref=backref('miembrosproyectos', lazy='dynamic'))
    id_usuario = Column(Integer, ForeignKey('usuario.id'))
    miembrosusuario = relationship(Usuario, backref=backref('miembrosusuarios', lazy='dynamic'), order_by='Usuario.usuario')
    
    def __init__(self, id_proyecto=None, id_usuario=None):
        self.id_proyecto = id_proyecto
        self.id_usuario = id_usuario
        
    def __repr__(self):
        return '<Miembros Comite %s %s>' % (self.id_proyecto, self.id_usuario)
    