from sqlalchemy import *
from sqlalchemy.orm import *
from com.py.sap.util.database import Base

class SolicitudItem (Base):
    __tablename__ = 'solicitud_item'
    id = Column('id', Integer, Sequence('solicitud_item_id_seq'), primary_key=True)
    id_solicitud = Column(Integer, ForeignKey('solicitud_cambio.id'))
    solicitud = relationship('Solicitud', backref=backref('solicitudes', lazy='dynamic'))
    id_item = Column(Integer, ForeignKey('item.id'))
    item = relationship('Item', backref=backref('item', lazy='dynamic'))
    
    def __init__(self, solicitud=None, item=None):
        self.solicitud = solicitud
        self.item = item
        
    def __repr__(self):
        return '<Solicitud Item %s %s>' % (self.solicitud, self.item)
    