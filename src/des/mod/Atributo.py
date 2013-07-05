""" Modelo de la tabla Atributo"""
from sqlalchemy import Integer, Sequence, String, Column, ForeignKey
from sqlalchemy.orm import relationship, backref
from util.database import Base
from des.mod.TipoAtributo import TipoAtributo

class Atributo (Base):
    __tablename__ = 'atributo'
    __table_args__ = {'extend_existing': True}
    id = Column('id', Integer, Sequence('atributo_id_seq'), primary_key=True)
    nombre = Column('nombre', String(50),unique=True)
    descripcion = Column('descripcion', String(100))
    id_tipo_atributo = Column(Integer, ForeignKey('tipo_atributo.id'))
    atributotipo_atributo = relationship(TipoAtributo, backref=backref('atributotipo_atributos', lazy='dynamic'))
    
    def __init__(self, nombre=None, descripcion=None, id_tipo_atributo=None):
        self.nombre = nombre
        self.descripcion = descripcion
        self.id_tipo_atributo = id_tipo_atributo
        
    def __repr__(self):
        return '<Atributo %s %s %s %d>' % ( self.nombre, self.descripcion, self.id_tipo_atributo)