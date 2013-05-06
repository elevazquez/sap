from sqlalchemy import *
from sqlalchemy.orm import *
from com.py.sap.util.database import Base

class Proyecto (Base):
    __tablename__ = 'proyecto'
    id = Column('id', Integer, Sequence('proyecto_id_seq'), primary_key=True)
    descripcion = Column('descripcion', String(100))
    estado = Column('estado', String(1))
    fecha = Column('fecha', Date)
    cant_votos = Column('cant_votos', Integer)
    id_usuario = Column(Integer, ForeignKey('usuario.id'))
    usuario = relationship('Usuario', backref=backref('usuarios', lazy='dynamic'))
    
    def __init__(self, descripcion=None, estado=None, fecha=None, cant_votos=None, usuario=None):
        self.descripcion = descripcion
        self.estado = estado
        self.fecha = fecha
        self.cant_votos = cant_votos
        self.usuario = usuario
            
    def __repr__(self):
        return '<Proyecto %s %s %d %i %s>' % (self.descripcion, self.estado,
        self.fecha, self.cant_votos, self.usuario)
    