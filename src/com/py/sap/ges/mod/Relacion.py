from sqlalchemy import *
from sqlalchemy.orm import *
from com.py.sap.util.database import Base

class Relacion (Base):
    __tablename__ = 'relacion'
    id = Column('id', Integer, Sequence('relacion_id_seq'), primary_key=True)
    fecha_creacion = Column('fecha_creacion', Date)
    fecha_modificacion = Column('fecha_modificacion', Date) 
    id_tipo_relacion = Column(Integer, ForeignKey('tipo_relacion.id'))
    tipo_relacion = relationship('TipoRelacion', backref=backref('tipo_relaciones', lazy='dynamic'))
    id_item = Column(Integer, ForeignKey('item.id'))
    item = relationship('Item', backref=backref('items', lazy='dynamic'))
    id_item_duenho = Column(Integer, ForeignKey('item.id'))
    item_duenho = relationship('ItemDuenho', backref=backref('item_duenhos', lazy='dynamic'))

    def __init__(self, fecha_creacion=None, fecha_modificacion=None, tipo_relacion=None,
                 item=None, item_duenho=None,):
        self.fecha_creacion = fecha_creacion
        self.fecha_modificacion = fecha_modificacion
        self.tipo_relacion = tipo_relacion
        self.item = item
        self.item_duenho = item_duenho
        
    def __repr__(self):
        return '<Relacion %d %d %s %s %s>' % (self.fecha_creacion, self.fecha_modificacion,
                 self.tipo_relacion, self.item, self.item_duenho)
    