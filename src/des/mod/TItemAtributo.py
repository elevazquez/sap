""" Modelo de la tabla TItem Atributo"""
from sqlalchemy import *
from sqlalchemy.orm import *
from util.database import Base
from des.mod.TipoItem import TipoItem
from des.mod.Atributo import Atributo

class TItemAtributo (Base):
    __tablename__ = 'titem_atributo'
    __table_args__ = {'extend_existing': True}
    id = Column('id', Integer, Sequence('titem_atributo_id_seq'), primary_key=True)
    id_tipo_item = Column(Integer, ForeignKey('tipo_item.id'))
    titematttipo_item = relationship(TipoItem, backref=backref('titematttipo_items', lazy='dynamic'))
    id_atributo = Column(Integer, ForeignKey('atributo.id'))
    titemattatributo = relationship(Atributo, backref=backref('titemattatributos', lazy='dynamic'))
    
    def __init__(self, id_tipo_item=None, id_atributo=None):
        self.id_tipo_item = id_tipo_item
        self.id_atributo = id_atributo
        
    def __repr__(self):
        return '<Tipo Tipo Item Atributo %s %s %s %s>' % (self.id_tipo_item, self.id_atributo)
    