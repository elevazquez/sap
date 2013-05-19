""" Modelo de la tabla Permiso """
from sqlalchemy import Integer, Sequence, String, Column, ForeignKey
from sqlalchemy.orm import backref, relationship
from util.database import Base
from des.mod.Fase import Fase

class Permiso (Base):
    __tablename__ = 'permiso'
    __table_args__ = {'extend_existing': True}
    id = Column('id', Integer, Sequence('permiso_id_seq'), primary_key=True)
    codigo = Column('codigo', String(50), unique=True)
    descripcion = Column('descripcion', String(100))
    id_fase = Column(Integer, ForeignKey('fase.id'))
    permisofase = relationship(Fase, backref=backref('permisosfases', lazy='dynamic'))
    
    def __init__(self, codigo=None, descripcion=None, id_fase=None):
        self.codigo = codigo
        self.descripcion = descripcion 
        self.id_fase = id_fase
 
    def __repr__(self):
        return '<Permiso %s %s %s>' % (self.codigo, self.descripcion, self.id_fase)
    