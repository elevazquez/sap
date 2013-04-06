from sqlalchemy import *
from sqlalchemy.orm import *
from com.py.sap.util.database import Base

class LbItem (Base):
    __tablename__ = 'lb_item'
    id = Column('id', Integer, Sequence('lb_item_id_seq'), primary_key=True)
    id_linea_base = Column(Integer, ForeignKey('linea_base.id'))
    linea_base = relationship('LineaBase', backref=backref('linea_bases', lazy='dynamic'))
    id_item = Column(Integer, ForeignKey('item.id'))
    item = relationship('Item', backref=backref('items', lazy='dynamic'))
    
    def __init__(self, linea_base=None, item=None):
        self.linea_base = linea_base
        self.item = item
        
    def __repr__(self):
        return '<LbItem %s %s>' % (self.linea_base, self.item)
    