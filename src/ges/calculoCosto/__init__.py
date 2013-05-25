from loginC import app
from util.database import init_db, engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import Flask, render_template, request, redirect, url_for, flash, session
import flask, flask.views
from des.mod.Item import *
from ges.mod.Relacion import *

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
class CalculoCostoControlador(flask.views.MethodView):
    def get(self):
        return flask.render_template('calculoCosto.html')

def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ),'error')

@app.route('/calculocosto', methods=['GET', 'POST'])
def calculoCostoAll():
    caminos = getAllCaminosCosto(1)
    caminoCosto = []
    for camino in caminos :
        costo = 0
        for item in camino :
            costo = costo + item.costo
        caminoCosto.append(costo)
    
    return
        
def getAllCaminosCosto(item):
    """ Funcion para calcular costo"""
    caminos = []
    unicoCamino = [item]
    caminos.append(unicoCamino)
    caminosItem = getCaminos(caminos)
    return caminosItem
    
def getItemsPadres(idItem):
    return db_session.query(Item).join(Relacion, Relacion.id_item == Item.id).filter(Item.id == idItem).filter(Relacion.estado == 'A')
    
def getListas(listaItem, ultimoItem, itemsAAnhadir):
    listaNueva=[]
    for i in itemsAAnhadir:
        auxiliar = listaItem
        auxiliar.append(i)
        listaNueva.append(auxiliar)
    return listaNueva

def getCaminos(listaCamino):
    bandera= True
    unicoCamino = listaCamino[0]
    tamanho = len(unicoCamino) - 1
    ultimoItem = listaCamino[tamanho]
    itemsAAnhadir = getItemsPadres(ultimoItem.id)
    unicoCamino = listaCamino.pop(0)
    while bandera:
        listaNuevoCamino = getListas(unicoCamino, ultimoItem , itemsAAnhadir)
        for camino in listaNuevoCamino :
            listaCamino.append(camino)
        
        tamanho = len(listaCamino) - 1
        unicoCamino = listaCamino.pop(0)
        posicion = len(unicoCamino) - 1
        ultimoItem = unicoCamino[posicion]
        itemsAAnhadir = getItemsPadres(ultimoItem)
        s = 0
        while itemsAAnhadir == None and s < tamanho :
            listaCamino.append(unicoCamino)
            unicoCamino = listaCamino.pop(0)
            posicion = len(unicoCamino) - 1
            ultimoItem = unicoCamino[posicion]
            itemsAAnhadir = getItemsPadres(ultimoItem)
            s = s + 1
        
        if itemsAAnhadir != None :
            bandera =  True
        else:
            if s == tamanho :
                bandera = False
                listaCamino.append(unicoCamino)
    return listaCamino