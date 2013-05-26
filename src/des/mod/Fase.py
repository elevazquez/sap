""" Modelo de la tabla Fase"""
from sqlalchemy import *
from sqlalchemy.orm import *
from util.database import Base
from adm.mod.Proyecto import Proyecto

class Fase (Base):
    __tablename__ = 'fase'
    __table_args__ = {'extend_existing': True}
    id = Column('id', Integer, Sequence('fase_id_seq'), primary_key=True)
    nro_orden = Column('nro_orden', Integer)
    nombre = Column('nombre', String(50))
    descripcion = Column('descripcion', String(100))
    estado = Column('estado', String(1))
    fecha_inicio = Column('fecha_inicio', Date)
    fecha_fin = Column('fecha_fin', Date)
    id_proyecto = Column(Integer, ForeignKey('proyecto.id'))
    faseproyecto = relationship(Proyecto, backref=backref('faseproyectos', lazy='dynamic'))
    
    def __init__(self, nro_orden=None, nombre=None, descripcion=None, estado=None, fecha_inicio=None,
    fecha_fin=None, id_proyecto=None):
        self.nro_orden = nro_orden
        self.nombre = nombre
        self.descripcion = descripcion
        self.estado = estado
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.id_proyecto = id_proyecto
    
    def __repr__(self):
        return '<Fase %d %s %s %s %s %s %d>' % (self.nro_orden, self.nombre, self.descripcion, self.estado,
        self.fecha_inicio, self.fecha_fin, self.id_proyecto)
    