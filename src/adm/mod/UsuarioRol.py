from sqlalchemy import Column, Sequence, ForeignKey, Integer, String
from sqlalchemy.orm import backref, relationship
from util.database import Base
from adm.mod.Rol import Rol
from adm.mod.Usuario import Usuario

class UsuarioRol (Base):
    __tablename__ = 'usuario_rol'
    id = Column('id', Integer, Sequence('usuario_rol_id_seq'), primary_key=True)
    id_rol = Column(Integer, ForeignKey('rol.id'))
    rol = relationship('Rol', backref=backref('rolesusuarios', lazy='dynamic'))
    id_usuario = Column(Integer, ForeignKey('usuario.id'))
    usuario = relationship('Usuario', backref=backref('usuariosroles', lazy='dynamic'))
    id_proyecto = Column(Integer, ForeignKey('proyecto.id'))
    proyecto = relationship('Proyecto', backref=backref('proyectosroles', lazy='dynamic'))
    
    def __init__(self, id_rol=None, id_usuario=None, id_proyecto=None):
        self.id_rol = id_rol
        self.id_usuario = id_usuario
        self.id_proyecto = id_proyecto
    
    def __repr__(self):
        return '<Usuario Rol %s %s %s %s>' % (self.id_rol, self.id_usuario, self.id_proyecto)
    