from sqlalchemy import Column, Sequence, ForeignKey, Integer, String
from sqlalchemy.orm import backref, relationship
from com.py.sap.util.database import Base
from com.py.sap.adm.mod.Rol import Rol
from com.py.sap.adm.mod.Usuario import Usuario

class UsuarioRol (Base):
    __tablename__ = 'usuario_rol'
    id = Column('id', Integer, Sequence('usuario_rol_id_seq'), primary_key=True)
    nombre = Column('nombre', String(50))
    descripcion = Column('descripcion', String(100))
    id_rol = Column(Integer, ForeignKey('rol.id'))
    rol = relationship('Rol', backref=backref('rolesusuarios', lazy='dynamic'))
    id_usuario = Column(Integer, ForeignKey('usuario.id'))
    usuario = relationship('Usuario', backref=backref('usuariosroles', lazy='dynamic'))
    
    def __init__(self, nombre=None, descripcion=None, rol=None, id_usuario=None):
        self.nombre = nombre
        self.descripcion = descripcion
        self.rol = rol
        self.id_usuario = id_usuario
    
    def __repr__(self):
        return '<Usuario Rol %s %s %s %s>' % (self.nombre, self.descripcion, self.rol, self.id_usuario)
    