""" Modelo de la tabla UsuarioRol """
from sqlalchemy import Column, Sequence, ForeignKey, Integer, String
from sqlalchemy.orm import backref, relationship
from util.database import Base
from adm.mod.Rol import Rol
from adm.mod.Usuario import Usuario
from adm.mod.Proyecto import Proyecto

class UsuarioRol (Base):
    __tablename__ = 'usuario_rol'
    __table_args__ = {'extend_existing': True}
    id = Column('id', Integer, Sequence('usuario_rol_id_seq'), primary_key=True)
    id_rol = Column(Integer, ForeignKey('rol.id'))
    usuariorolrol = relationship(Rol, backref=backref('usuariorolrols', lazy='dynamic'))
    id_usuario = Column(Integer, ForeignKey('usuario.id'))
    usuariorolusuario = relationship(Usuario, backref=backref('usuariorolusuarios', lazy='dynamic'))
    id_proyecto = Column(Integer, ForeignKey('proyecto.id'))
    usuariorolproyecto = relationship(Proyecto, backref=backref('usuariorolproyectos', lazy='dynamic'))
    
    def __init__(self, id_rol=None, id_usuario=None, id_proyecto=None):
        self.id_rol = id_rol
        self.id_usuario = id_usuario
        self.id_proyecto = id_proyecto
    
    def __repr__(self):
        return '<Usuario Rol %d %d %d>' % (self.id_rol, self.id_usuario, self.id_proyecto)
    