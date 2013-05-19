""" Modelo de la tabla Resolucion Miembros """
from sqlalchemy import *
from sqlalchemy.orm import *
from util.database import Base
from ges.mod.SolicitudCambio import SolicitudCambio 
from adm.mod.Usuario import Usuario 

class ResolucionMiembros (Base):
    __tablename__ = 'resolucion_miembros'
    __table_args__ = {'extend_existing': True}
    id = Column('id', Integer, Sequence('resolucion_miembros_id_seq'), primary_key=True)
    voto = Column('voto', Boolean)
    id_solicitud_cambio = Column(Integer, ForeignKey('solicitud_cambio.id'))
    resmiesolicitud_cambio = relationship(SolicitudCambio, backref=backref('resmiesolicitud_cambios', lazy='dynamic'))
    id_usuario = Column(Integer, ForeignKey('usuario.id'))
    resmieusuario = relationship(Usuario, backref=backref('resmieusuarios', lazy='dynamic'))
    
    def __init__(self, voto=None, id_solicitud_cambio=None, id_usuario=None):
        self.voto = voto
        self.id_solicitud_cambio = id_solicitud_cambio
        self.id_usuario = id_usuario
        
    def __repr__(self):
        return '<ResolucionMiembros %s %s %s>' % (self.voto, self.id_solicitud_cambio, self.id_usuario)
    