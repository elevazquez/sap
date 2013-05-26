""" Modelo de la tabla Solicitud Item"""
from sqlalchemy import *
from sqlalchemy.orm import *
from util.database import Base
from des.mod.Item import Item 
from ges.mod.SolicitudCambio import SolicitudCambio 

class SolicitudItem (Base):
    __tablename__ = 'solicitud_item'
    __table_args__ = {'extend_existing': True}
    id = Column('id', Integer, Sequence('solicitud_item_id_seq'), primary_key=True)
    id_solicitud = Column(Integer, ForeignKey('solicitud_cambio.id'))
    solitemsolicitud = relationship(SolicitudCambio, backref=backref('solitemsolicituds', lazy='dynamic'))
    id_item = Column(Integer, ForeignKey('item.id'))
    solitemitem = relationship(Item, backref=backref('solitemitems', lazy='dynamic'))
    
    def __init__(self, id_solicitud=None, id_item=None):
        self.id_solicitud = id_solicitud
        self.id_item = id_item
        
    def __repr__(self):
        return '<Solicitud Item %d %d>' % (self.id_solicitud, self.id_item)