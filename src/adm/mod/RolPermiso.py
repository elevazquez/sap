""" Modelo de la tabla RolPermiso """
from sqlalchemy import Column, Sequence, ForeignKey, Integer
from sqlalchemy.orm import relationship, backref
from util.database import Base
from adm.mod.Rol import Rol
from adm.mod.Permiso import Permiso

class RolPermiso (Base):
    __tablename__ = 'rol_permiso'
    __table_args__ = {'extend_existing': True}
    id = Column('id', Integer, Sequence('rol_permiso_id_seq'), primary_key=True)
    id_rol = Column(Integer, ForeignKey('rol.id'))
    rolpermisorol = relationship(Rol, backref=backref('rolpermisorols', lazy='dynamic'))
    id_permiso = Column(Integer, ForeignKey('permiso.id'))
    rolpermisopermiso = relationship(Permiso, backref=backref('rolpermisopermisos', lazy='dynamic'))
    
    def __init__(self, id_rol=None, id_permiso=None):
        self.id_rol = id_rol
        self.id_permiso = id_permiso
        
    def __repr__(self):
        return '<RolPermiso %s %s>' % (self.id_rol, self.id_permiso)
