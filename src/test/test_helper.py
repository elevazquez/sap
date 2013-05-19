import re
import xml.etree.ElementTree as ET
#from BeautifulSoup import BeautifulSoup


TEST_USER = 'raquel'
TEST_PASS = 'raquel'


def login(app, usuario=TEST_USER, password=TEST_PASS):
    """
    Este metodo realiza el test de ingreso a la pagina login de la aplicacion
    @param app: la aplicacion
    @param nombre: nombre de usuario
    @param contrasenha: contrasenha del usuario
    """
    access = app.post('/', data=dict(
        usuario=usuario,
        password=password
        ), follow_redirects=True)

    return access

