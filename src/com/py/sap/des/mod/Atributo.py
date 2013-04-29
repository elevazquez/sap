from sqlalchemy import *
from sqlalchemy.orm import *
from com.py.sap.util.database import Base

class Atributo (Base):
    __tablename__ = 'atributo'
    id = Column('id', Integer, Sequence('atributo_id_seq'), primary_key=True)
    codigo = Column('codigo', String(50), unique=True)
    nombre = Column('nombre', String(50))
    descripcion = Column('descripcion', String(100))
    id_tipo_atributo = Column(Integer, ForeignKey('tipo_atributo.id'))
    tipo_atributo = relationship('TipoAtributo', backref=backref('tipo_atributos', lazy='dynamic'))
    
    def __init__(self, codigo=None, nombre=None, descripcion=None, id_tipo_atributo=None):
        self.codigo = codigo
        self.nombre = nombre
        self.descripcion = descripcion
        self.id_tipo_atributo = id_tipo_atributo
        
    def __repr__(self):
        return '<Atributo %s %s %s %s>' % (self.codigo, self.nombre, self.descripcion, self.tipo_atributo)
    