from sqlalchemy import *
from sqlalchemy.orm import *
from com.py.sap.util.database import Base

class ItemAtributo (Base):
    __tablename__ = 'itemAtributo'
    id = Column('id', Integer, Sequence('item_atributo_id_seq'), primary_key=True)
    valor = Column('nombre', String(50))
    id_item = Column(Integer, ForeignKey('item.id'))
    item = relationship('Item', backref=backref('items', lazy='dynamic'))
    id_atributo = Column(Integer, ForeignKey('atributo.id'))
    atributo = relationship('Atributo', backref=backref('atributos', lazy='dynamic'))
    
    def __init__(self, valor=None, item=None, atributo=None):
        self.valor = valor
        self.item = item
        self.atributo = atributo
        
    def __repr__(self):
        return '<ItemAtributo %s %s %s>' % (self.valor, self.item, self.atributo)
    