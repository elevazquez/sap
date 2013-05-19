""" Modelo de la tabla Tipo Atributo """
from sqlalchemy import *
from util.database import Base

class TipoAtributo (Base):
    __tablename__ = 'tipo_atributo'
    __table_args__ = {'extend_existing': True}
    id = Column('id', Integer, Sequence('tipo_atributo_id_seq'), primary_key=True)
    nombre = Column('nombre', String(50),unique=True)
    descripcion = Column('descripcion', String(100))
    
    def __init__(self,  nombre=None, descripcion=None):
        self.nombre = nombre
        self.descripcion = descripcion
        
    def __repr__(self):
        return '<TipoAtributo %s %s %s>' % (self.nombre, self.descripcion)
    