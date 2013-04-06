from sqlalchemy import *
from com.py.sap.util.database import Base

class LineaBase (Base):
    __tablename__ = 'linea_base'
    id = Column('id', Integer, Sequence('linea_base_id_seq'), primary_key=True)
    descripcion = Column('descripcion', String(100))
    estado = Column('estado', String(1))
    fecha_creacion = Column('fecha_creacion', Date)
    fecha_ruptura = Column('fecha_ruptura', Date)
    
    def __init__(self, descripcion=None, estado=None, fecha_creacion=None, fecha_ruptura=None):
        self.descripcion = descripcion
        self.estado = estado
        self.fecha_creacion = fecha_creacion
        self.fecha_ruptura = fecha_ruptura
        
    def __repr__(self):
        return '<LineaBase %s %s %d %d>' % (self.descripcion, self.estado,
        self.fecha_creacion, self.fecha_ruptura)
    