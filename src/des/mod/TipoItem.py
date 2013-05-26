""" Modelo de la tabla Tipo Item """
from sqlalchemy import *
from sqlalchemy.orm import *
from util.database import Base
from des.mod.Fase import Fase

class TipoItem (Base):
    __tablename__ = 'tipo_item'
    __table_args__ = {'extend_existing': True}
    id = Column('id', Integer, Sequence('tipo_item_id_seq'), primary_key=True)
    codigo = Column('codigo', String(50), unique=True)
    nombre = Column('nombre', String(50))
    descripcion = Column('descripcion', String(100))
    id_fase = Column(Integer, ForeignKey('fase.id'))
    tipoitemfase = relationship(Fase, backref=backref('tipoitemfases', lazy='dynamic'))
    
    def __init__(self, codigo=None, nombre=None, descripcion=None, id_fase=None):
        self.codigo = codigo
        self.nombre = nombre
        self.descripcion = descripcion
        self.id_fase = id_fase
    
    def __repr__(self):
        return '<Tipo Item %s %s %s %d>' % (self.codigo, self.nombre, self.descripcion, self.id_fase)