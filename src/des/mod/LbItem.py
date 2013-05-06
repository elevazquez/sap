from sqlalchemy import *
from sqlalchemy.orm import *
from util.database import Base

class LbItem (Base):
    __tablename__ = 'lb_item'
    id = Column('id', Integer, Sequence('lb_item_id_seq'), primary_key=True)
    id_linea_base = Column(Integer, ForeignKey('linea_base.id'))
    linea_base = relationship('LineaBase', backref=backref('linea_bases_item', lazy='dynamic'))
    id_item = Column(Integer, ForeignKey('item.id'))
    item = relationship('Item', backref=backref('items_lb', lazy='dynamic'))
    
    def __init__(self, id_linea_base=None, id_item=None):
        self.id_linea_base = id_linea_base
        self.id_item = id_item
        
    def __repr__(self):
        return '<LbItem %s %s>' % (self.linea_base, self.item)
    