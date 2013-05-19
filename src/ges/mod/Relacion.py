""" Modelo de la tabla Relacion"""
from sqlalchemy import Column, Integer, Sequence, Date, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, backref
from util.database import Base
from des.mod.Item import Item
from ges.mod.TipoRelacion import TipoRelacion 

class Relacion (Base):
    __tablename__ = 'relacion'
    __table_args__ = {'extend_existing': True}
    id = Column('id', Integer, Sequence('relacion_id_seq'), primary_key=True)
    fecha_creacion = Column('fecha_creacion', Date)
    fecha_modificacion = Column('fecha_modificacion', Date) 
    id_tipo_relacion = Column(Integer, ForeignKey('tipo_relacion.id'))
    relaciontipo_relacion = relationship(TipoRelacion, backref=backref('relaciontipo_relacions', lazy='dynamic'))
    id_item = Column(Integer, ForeignKey('item.id'))
    relacionitem = relationship(Item, backref=backref('relacionitems', lazy='dynamic'), foreign_keys=[id_item])
    id_item_duenho = Column(Integer, ForeignKey('item.id'))
    relacionitem_duenho = relationship(Item, backref=backref('relacionitem_duenhos', lazy='dynamic'), foreign_keys=[id_item_duenho])
    estado = Column('estado', String(1))
    __table_args__ = (UniqueConstraint('id_item', 'id_item_duenho', name='uq_relacion'),)
    

    def __init__(self, fecha_creacion=None, fecha_modificacion=None, id_tipo_relacion=None,
                 id_item=None, id_item_duenho=None, estado = None):
        self.fecha_creacion = fecha_creacion
        self.fecha_modificacion = fecha_modificacion
        self.id_tipo_relacion = id_tipo_relacion
        self.id_item = id_item
        self.id_item_duenho = id_item_duenho
        self.estado = estado
        
    def __repr__(self):
        return '<Relacion %d %d %s %s %s>' % (self.fecha_creacion, self.fecha_modificacion,
                 self.id_tipo_relacion, self.id_item, self.id_item_duenho, self.estado)
    