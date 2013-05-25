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
class CalculoImpactoControlador(flask.views.MethodView):
    def get(self):
        return flask.render_template('calculoImpacto.html')

def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ),'error')

""" Funcion para calcular impacto""" 
@app.route('/calculoimpacto', methods=['GET', 'POST'])
def calculoImpacto():
    caminos = []
    item=[1]
    items = getItemsPadres()
    for i in items:
        item.append(i.id)
        
    
def getItemsPadres():
    return db_session.query(Item).join(Relacion, Relacion.id_item == Item.id).filter(Relacion.estado == 'A')
    