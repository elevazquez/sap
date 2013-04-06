from sqlalchemy import *
from sqlalchemy.orm import *
from com.py.sap.util.database import Base

class TItemAtributo (Base):
    __tablename__ = 'titem_atributo'
    id = Column('id', Integer, Sequence('titem_atributo_id_seq'), primary_key=True)
    id_tipo_item = Column(Integer, ForeignKey('tipo_item.id'))
    tipo_item = relationship('TipoItem', backref=backref('tipo_items', lazy='dynamic'))
    id_atributo = Column(Integer, ForeignKey('atributo.id'))
    atributo = relationship('Atributo', backref=backref('atributos', lazy='dynamic'))
    
    def __init__(self, tipo_item=None, atributo=None):
        self.tipo_item = tipo_item
        self.atributo = atributo
        
    def __repr__(self):
        return '<Tipo Tipo Item Atributo %s %s %s %s>' % (self.tipo_item, self.atributo)
    