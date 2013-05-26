""" Modelo de la tabla LbItem"""
from sqlalchemy import *
from sqlalchemy.orm import *
from util.database import Base
from des.mod.Item import Item
from ges.mod.LineaBase import LineaBase

class LbItem (Base):
    __tablename__ = 'lb_item'
    __table_args__ = {'extend_existing': True}
    id = Column('id', Integer, Sequence('lb_item_id_seq'), primary_key=True)
    id_linea_base = Column(Integer, ForeignKey('linea_base.id'))
    lbitemlinea_base = relationship(LineaBase, backref=backref('lbitemlinea_bases', lazy='dynamic'))
    id_item = Column(Integer, ForeignKey('item.id'))
    lbitemitem = relationship(Item, backref=backref('lbitemitems', lazy='dynamic'))
    
    def __init__(self, id_linea_base=None, id_item=None):
        self.id_linea_base = id_linea_base
        self.id_item = id_item
        
    def __repr__(self):
        return '<LbItem %d %d>' % (self.id_linea_base, self.id_item)
    