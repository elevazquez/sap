""" Modelo de la tabla Archivo"""
from sqlalchemy import *
from sqlalchemy.orm import *
from util.database import Base
from des.mod.Item import Item
from sqlalchemy.types import Binary
from docutils.io import BinaryFileOutput

  
class Archivo(Base):
    __tablename__ = 'archivo'
    __table_args__ = {'extend_existing': True}
    id = Column('id', Integer, Sequence('archivo_id_seq'), primary_key=True)
    id_item = Column(Integer, ForeignKey('item.id'))
    archivoitem = relationship(Item, backref=backref('archivoitems', lazy='dynamic'))
    nombre = Column('nombre', String(50))
    archivo = Column('archivo',  Binary)
    mime = Column('mime', String(15))
    
    
    def __init__(self, id_item ,nombre,archivo,mime):
        self.id_item = id_item
        self.nombre = nombre
        self.archivo = archivo
        self.mime = mime
        
    
        
