from sqlalchemy import Integer, Sequence, String, Column, ForeignKey
from sqlalchemy.orm import relationship, backref
from util.database import Base
from adm.mod.Proyecto import Proyecto
from des.mod.Fase import Fase

class Recurso (Base):
    __tablename__ = 'recurso'
    id = Column('id', Integer, Sequence('recurso_id_seq'), primary_key=True)
    nombre = Column('nombre', String(100))
    id_proyecto = Column(Integer, ForeignKey('proyecto.id'))
    proyecto = relationship('Proyecto', backref=backref('proyectos', lazy='dynamic'))
    id_fase = Column(Integer, ForeignKey('fase.id'))
    fase = relationship('Fase', backref=backref('fases', lazy='dynamic'))
    
    def __init__(self, nombre=None, id_proyecto=None, id_fase=None):
        self.nombre = nombre
        self.id_proyecto = id_proyecto 
        self.id_fase = id_fase
 
    def __repr__(self):
        return '<Recurso %s %s %s>' % (self.nombre, self.proyecto, self.fase)
    