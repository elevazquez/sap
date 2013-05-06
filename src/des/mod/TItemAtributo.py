from sqlalchemy import *
from sqlalchemy.orm import *
from util.database import Base

class TItemAtributo (Base):
    __tablename__ = 'titem_atributo'
    id = Column('id', Integer, Sequence('titem_atributo_id_seq'), primary_key=True)
    id_tipo_item = Column(Integer, ForeignKey('tipo_item.id'))
    tipo_item = relationship('TipoItem', backref=backref('tipo_items', lazy='dynamic'))
    id_atributo = Column(Integer, ForeignKey('atributo.id'))
    atributo = relationship('Atributo', backref=backref('atributostipoItem', lazy='dynamic'))
    
    def __init__(self, id_tipo_item=None, id_atributo=None):
        self.id_tipo_item = id_tipo_item
        self.id_atributo = id_atributo
        
    def __repr__(self):
        return '<Tipo Tipo Item Atributo %s %s %s %s>' % (self.tipo_item, self.atributo)
    