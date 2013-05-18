from sqlalchemy import Column, Integer, Sequence, String, Date
from util.database import Base
#Para implementar una clase de usuario mas sencilla se hereda de UserMixin
#implement these methods: is_authenticated(), is_active(), is_anonymous(), get_id()
from flask_login import UserMixin

class Usuario (Base, UserMixin):
    __tablename__ = 'usuario'
    __table_args__ = {'extend_existing': True}
    id = Column('id', Integer, Sequence('usuario_id_seq'), primary_key=True)
    usuario = Column('usuario', String(50), unique=True)
    nombre = Column('nombre', String(100))
    apellido = Column('apellido', String(100))
    password = Column('password', String(100))
    correo = Column('correo', String(100))
    domicilio = Column('domicilio', String(150))
    telefono = Column('telefono', String(50))
    fecha_nac = Column('fecha_nac', Date)
    
    def __init__(self, usuario=None, nombre=None, apellido=None, password=None, correo=None, 
                 domicilio=None, telefono=None, fecha_nac=None):
        self.usuario = usuario
        self.nombre = nombre
        self.apellido = apellido
        self.password = password
        self.correo = correo
        self.domicilio = domicilio
        self.telefono = telefono
        self.fecha_nac = fecha_nac
    
    def __repr__(self):
        return '<Usuario %s %s %s %s %s %s %s %d>' % (self.usuario, self.nombre, self.apellido,
        self.password, self.correo, self.domicilio, self.telefono, self.fecha_nac)
    
    def getUserName(self): 
        return self.usuario
    