""" Modelo de la tabla Tipo Atributo """
from sqlalchemy import *
from util.database import Base

class TipoAtributo (Base):
    __tablename__ = 'tipo_atributo'
    __table_args__ = {'extend_existing': True}
    id = Column('id', Integer, Sequence('tipo_atributo_id_seq'), primary_key=True)
    codigo = Column('codigo', String(50), unique=True)
    nombre = Column('nombre', String(50))
    descripcion = Column('descripcion', String(100))
    
    def __init__(self, codigo=None, nombre=None, descripcion=None):
        self.codigo = codigo
        self.nombre = nombre
        self.descripcion = descripcion
        
    def __repr__(self):
        return '<TipoAtributo %s %s %s>' % (self.codigo, self.nombre, self.descripcion)
    