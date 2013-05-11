from sqlalchemy import *
from sqlalchemy.orm import *
from util.database import Base
from adm.mod.Usuario import Usuario
from des.mod.Fase import Fase
from des.mod.TipoItem import TipoItem

class Item (Base):
    __tablename__ = 'item'
    id = Column('id', Integer, Sequence('item_id_seq'), primary_key=True)
    codigo = Column('codigo', String(50), unique=True)
    nombre = Column('nombre', String(50))  
    descripcion = Column('descripcion', String(100))
    estado = Column('estado', String(1))
    complejidad = Column('complejidad', Integer)  
    fecha = Column('fecha', Date)
    costo = Column('costo', Numeric(10,2))
   # archivo = Column('archivo', bytearray)
   # mime = Column('mime', String(15), unique=True)
    version = Column('version', Integer)
    id_usuario = Column(Integer, ForeignKey('usuario.id'))
    usuario = relationship('Usuario', backref=backref('usuariositem', lazy='dynamic'))
    id_fase = Column(Integer, ForeignKey('fase.id'))
    fase = relationship('Fase', backref=backref('fasesitem', lazy='dynamic'))
    id_tipo_item = Column(Integer, ForeignKey('tipo_item.id'))
    tipo_item = relationship('TipoItem', backref=backref('tipoitem_item', lazy='dynamic'))
    
    def __init__(self, codigo=None, nombre=None, descripcion=None, estado=None, complejidad=None, 
                 fecha=None, costo=None , id_usuario=None, version=None,
                 id_fase=None, id_tipo_item=None):
        self.codigo = codigo
        self.nombre = nombre
        self.descripcion = descripcion
        self.estado = estado
        self.complejidad = complejidad
        self.fecha = fecha
        self.costo = costo
        #self.archivo = archivo
        #self.mime = mime
        self.id_usuario = id_usuario
        self.version = version
        self.id_fase = id_fase
        self.id_tipo_item = id_tipo_item
        
    def __repr__(self):
        return '<Item %s %s %s %s %i %d %f %s %s  %s %s>' % (self.codigo, self.nombre, self.descripcion, 
        self.estado, self.complejidad, self.fecha, self.costo,  self.id_usuario,
        self.version, self.id_fase, self.id_tipo_item)
    