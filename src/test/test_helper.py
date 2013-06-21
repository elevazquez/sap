#import re
#import xml.etree.ElementTree as ET
#from flask import  session
#from UserPermission import UserRol

#from BeautifulSoup import BeautifulSoup


TEST_USER = 'admin'
TEST_PASS = 'admin'



def login(app, usuario=TEST_USER, password=TEST_PASS):
    """
    Este metodo realiza el test de ingreso a la pagina login de la aplicacion
    @param app: la aplicacion
    @param nombre: nombre de usuario
    @param contrasenha: contrasenha del usuario
    """
    #permission = UserRol('ADMINISTRADOR')
    #session['permission_admin'] = permission
    
    access = app.post('/', data=dict(
        username=usuario,
        passwd=password
        ), follow_redirects=True)
    return access
