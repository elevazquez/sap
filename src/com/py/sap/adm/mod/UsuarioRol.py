  id serial NOT NULL,
  id_rol integer NOT NULL,
  id_usuario integer NOT NULL,
  nombre character varying(50) NOT NULL,
  descripcion character varying(100) NOT NULL,
  CONSTRAINT pk_usuario_rol PRIMARY KEY (id ),
  CONSTRAINT fk_usuario_rol FOREIGN KEY (id_rol)
      REFERENCES rol (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION,
  CONSTRAINT fk_usurol_usu FOREIGN KEY (id_usuario)
      REFERENCES usuario (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION
from sqlalchemy import *
from sqlalchemy.orm import *
from com.py.sap.util.database import Base

class UsuarioRol (Base):
    __tablename__ = 'usuario_rol'
    id = Column('id', Integer, Sequence('usuario_rol_id_seq'), primary_key=True)
    nombre = Column('nombre', String(50))
    descripcion = Column('descripcion', String(100))
    id_rol = Column(Integer, ForeignKey('rol.id'))
    rol = relationship('Rol', backref=backref('roles', lazy='dynamic'))
    id_usuario = Column(Integer, ForeignKey('usuario.id'))
    usuario = relationship('Usuario', backref=backref('usuarios', lazy='dynamic'))
    
    def __init__(self, nombre=None, descripcion=None, rol=None, usuario=None):
        self.nombre = nombre
        self.descripcion = descripcion
        self.rol = fase
        self.usuario = usuario
    
    def __repr__(self):
        return '<Usuario Rol %s %s %s %s>' % (self.nombre, self.descripcion, self.rol, self.usuario)
    