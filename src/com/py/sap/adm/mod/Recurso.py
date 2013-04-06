from sqlalchemy import *
from sqlalchemy.orm import *
from com.py.sap.util.database import Base

class Recurso (Base):
    __tablename__ = 'recurso'
    id = Column('id', Integer, Sequence('recurso_id_seq'), primary_key=True)
    nombre = Column('nombre', String(100))
    id_proyecto = Column(Integer, ForeignKey('proyecto.id'))
    proyecto = relationship('Proyecto', backref=backref('proyectos', lazy='dynamic'))
    id_fase = Column(Integer, ForeignKey('fase.id'))
    fase = relationship('Fase', backref=backref('fases', lazy='dynamic'))
    
    def __init__(self, nombre=None, proyecto=None, fase=None):
        self.nombre = nombre
        self.proyecto = proyecto 
        self.fase = fase
 
    def __repr__(self):
        return '<Recurso %s %s %s>' % (self.nombre, self.proyecto, self.fase)
    