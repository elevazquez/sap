""" Modelo de la tabla Solicitud Cambio"""
from sqlalchemy import *
from sqlalchemy.orm import *
from util.database import Base
from adm.mod.Usuario import Usuario 
from adm.mod.Proyecto import Proyecto 
from util.database import init_db, engine
from sqlalchemy.orm import scoped_session, sessionmaker
from ges.mod.LineaBase import LineaBase

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

class SolicitudCambio (Base):
    __tablename__ = 'solicitud_cambio'
    __table_args__ = {'extend_existing': True}
    id = Column('id', Integer, Sequence('proyecto_id_seq'), primary_key=True)
    descripcion = Column('descripcion', String(2000))
    estado = Column('estado', String(1))
    fecha = Column('fecha', Date)
    cant_votos = Column('cant_votos', Integer)
    id_usuario = Column(Integer, ForeignKey('usuario.id'))
    solcamusuario = relationship(Usuario, backref=backref('solcamusuarios', lazy='dynamic'))
    id_proyecto = Column(Integer, ForeignKey('proyecto.id'))
    solcamproyecto = relationship(Proyecto, backref=backref('solcamproyectos', lazy='dynamic'))
    
    def __init__(self, descripcion=None, estado=None, fecha=None, cant_votos=None, id_usuario=None, id_proyecto=None):
        self.descripcion = descripcion
        self.estado = estado
        self.fecha = fecha
        self.cant_votos = cant_votos
        self.id_usuario = id_usuario
        self.id_proyecto = id_proyecto
            
    def __repr__(self):
        return '<Proyecto %s %s %s %s %s %s>' % (self.descripcion, self.estado,
        self.fecha, self.cant_votos, self.id_usuario, self.id_proyecto)
    
    def detalle(self, id_solicitud=None):
        return db_session.query(LineaBase).from_statement('select lb.* from solicitud_item si, linea_base lb, lb_item lbi '+ 
        ' where si.id_solicitud='+str(id_solicitud)+' and si.id_item = lbi.id_item and lbi.id_linea_base = lb.id order by lb.descripcion ') 
        