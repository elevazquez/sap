""" Modelo de la tabla Item Atributo """
from sqlalchemy import Integer, Sequence, String, Column, ForeignKey
from sqlalchemy.orm import backref, relationship
from util.database import Base
from des.mod.Item import Item
from des.mod.Atributo import Atributo

class ItemAtributo (Base):
    __tablename__ = 'item_atributo'
    __table_args__ = {'extend_existing': True}
    id = Column('id', Integer, Sequence('item_atributo_id_seq'), primary_key=True)
    valor = Column('valor', String(50))
    id_item = Column(Integer, ForeignKey('item.id'))
    itematributoitem = relationship(Item, backref=backref('itematributoitems', lazy='dynamic'))
    id_atributo = Column(Integer, ForeignKey('atributo.id'))
    itematributoatributo = relationship(Atributo, backref=backref('itematributoatributos', lazy='dynamic'))
    
    def __init__(self, valor=None, id_item=None, id_atributo=None):
        self.valor = valor
        self.id_item = id_item
        self.id_atributo = id_atributo
        
    def __repr__(self):
        return '<ItemAtributo %s %s %s>' % (self.valor, self.id_item, self.id_atributo)