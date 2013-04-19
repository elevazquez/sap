from sqlalchemy import *
from sqlalchemy.orm import *
from com.py.sap.util.database import Base

class Proyecto (Base):
    __tablename__ = 'proyecto'
    id = Column('id', Integer, Sequence('proyecto_id_seq'), primary_key=True)
    nombre = Column('nombre', String(50), unique=True)
    descripcion = Column('descripcion', String(100))
    estado = Column('estado', String(1))
    cant_miembros = Column('cant_miembros', Integer)
    fecha_inicio = Column('fecha_inicio', Date)
    fecha_fin = Column('fecha_fin', Date)
    fecha_ultima_mod = Column('fecha_ultima_mod', Date)
    id_usuario_lider = Column(Integer, ForeignKey('usuario.id'))
    usuario_lider = relationship('Usuario', backref=backref('usuarios', lazy='dynamic'))
    
    def __init__(self, nombre=None, descripcion=None, estado=None, cant_miembros=None, fecha_inicio=None,
    fecha_fin=None, fecha_ultima_mod=None, id_usuario_lider=None):
        self.nombre = nombre
        self.descripcion = descripcion
        self.estado = estado
        self.cant_miembros = cant_miembros
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.fecha_ultima_mod = fecha_ultima_mod
        self.id_usuario_lider = id_usuario_lider
    
    def __repr__(self):
        return '<Proyecto %s %s %s %d %d %d %d %s>' % (self.nombre, self.descripcion, self.estado,
        self.cant_miembros, self.fecha_inicio, self.fecha_fin, self.fecha_ultima_mod,
        self.usuario_lider)
    