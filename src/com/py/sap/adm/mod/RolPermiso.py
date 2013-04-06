from sqlalchemy import *
from sqlalchemy.orm import *
from com.py.sap.util.database import Base

class RolPermiso (Base):
    __tablename__ = 'rol_permiso'
    id = Column('id', Integer, Sequence('rol_permiso_id_seq'), primary_key=True)
    id_rol = Column(Integer, ForeignKey('rol.id'))
    rol = relationship('Rol', backref=backref('roles', lazy='dynamic'))
    id_permiso = Column(Integer, ForeignKey('permiso.id'))
    permiso = relationship('Permiso', backref=backref('permisos', lazy='dynamic'))
    
    def __init__(self, rol=None, permiso=None):
        self.rol = rol
        self.permiso = permiso
        
    def __repr__(self):
        return '<RolPermiso %s %s>' % (self.rol, self.permiso)
