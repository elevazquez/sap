""" Modelo de la tabla Rol """
from sqlalchemy import Column, Integer, String, Sequence
from util.database import Base

class Rol (Base):
    __tablename__ = 'rol'
    __table_args__ = {'extend_existing': True}
    id = Column('id', Integer, Sequence('rol_id_seq'), primary_key=True)
    codigo = Column('codigo', String(50), unique=True)
    descripcion = Column('descripcion', String(100))
 
    def __init__(self, codigo=None, descripcion=None):
        self.codigo = codigo
        self.descripcion = descripcion 
 
    def __repr__(self):
        return '<Rol %s %s>' % (self.codigo, self.descripcion)