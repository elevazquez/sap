from sqlalchemy import *
from sqlalchemy.orm import *
from com.py.sap.util.database import Base

class Permiso (Base):
    __tablename__ = 'permiso'
    id = Column('id', Integer, Sequence('permiso_id_seq'), primary_key=True)
    codigo = Column('codigo', String(50), unique=True)
    descripcion = Column('descripcion', String(100))
    id_recurso = Column(Integer, ForeignKey('recurso.id'))
    recurso = relationship('Recurso', backref=backref('recursos', lazy='dynamic'))
    
    def __init__(self, codigo=None, descripcion=None, recurso=None):
        self.codigo = codigo
        self.descripcion = descripcion 
        self.recurso = recurso
 
    def __repr__(self):
        return '<Permiso %s %s %s>' % (self.codigo, self.descripcion, self.recurso)
    