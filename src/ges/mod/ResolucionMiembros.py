from sqlalchemy import *
from sqlalchemy.orm import *
from util.database import Base

class ResolucionMiembros (Base):
    __tablename__ = 'resolucion_miembros'
    id = Column('id', Integer, Sequence('resolucion_miembros_id_seq'), primary_key=True)
    voto = Column('voto', Boolean)
    id_solicitud_cambio = Column(Integer, ForeignKey('solicitud_cambio.id'))
    solicitud_cambio = relationship('SolicitudCambio', backref=backref('solicitud_cambio', lazy='dynamic'))
    id_usuario = Column(Integer, ForeignKey('usuario.id'))
    usuario = relationship('Usuario', backref=backref('usuarios', lazy='dynamic'))
    
    def __init__(self, voto=None, solicitud_cambio=None, usuario=None):
        self.voto = voto
        self.solicitud_cambio = solicitud_cambio
        self.usuario = usuario
        
    def __repr__(self):
        return '<ResolucionMiembros %s %s %s>' % (self.voto, self.solicitud_cambio, self.usuario)
    