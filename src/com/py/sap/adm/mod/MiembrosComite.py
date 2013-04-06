from sqlalchemy import *
from sqlalchemy.orm import *
from com.py.sap.util.database import Base

class MiembrosComite (Base):
    __tablename__ = 'miembros_comite'
    id = Column('id', Integer, Sequence('miembros_comite_id_seq'), primary_key=True)
    id_proyecto = Column(Integer, ForeignKey('proyecto.id'))
    proyecto = relationship('Proyecto', backref=backref('proyectos', lazy='dynamic'))
    id_usuario = Column(Integer, ForeignKey('usuario.id'))
    usuario = relationship('Usuario', backref=backref('usuarios', lazy='dynamic'))
    
    def __init__(self, proyecto=None, usuario=None):
        self.proyecto = proyecto
        self.usuario = usuario
        
    def __repr__(self):
        return '<MiembrosComite %s %s>' % (self.proyecto, self.usuario)
    