from loginC import app
from util.database import init_db, engine
import sqlalchemy
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import Flask, render_template, request, redirect, url_for, flash, session
from ges.mod.Relacion import Relacion
from des.mod.Fase import Fase
from adm.mod.Proyecto import Proyecto
from des.mod.Item import Item
from ges.relacion.RelacionFormulario import RelacionFormulario
import flask, flask.views
from UserPermission import *
import os

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
class RelacionControlador(flask.views.MethodView):
    def get(self):
        return flask.render_template('relacion.html')

def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ),'error')

""" Funcion para agregar registros a la tabla relacion""" 
@app.route('/relacion/nuevarelacion', methods=['GET', 'POST'])
def nuevarelacion():
    #===========================================================================
    # permission = UserPermission('administrador')
    # if permission.can():
    #===========================================================================
    idItem = request.args.get('id_item')
    #===========================================================================
    # Si no hay ningun item seleccionado muestra todos los items que pertenecen a 
    # un proyecto, caso contrario muestra todos los items de la misma fase o fase
    # Siguiente, recordar que el duenho de la relacion es el hijo/sucesor, es decir, en el
    # else se selecciona al hijo o sucesor
    #===========================================================================
    if idItem == None or idItem == '':
        items = getItemByProyecto()
    else:
        items = getItemByProyBefoActFase(idItem)
        if items != None or items != '':
            session['itemduenho'] = idItem
        
    return render_template('relacion/nuevarelacion.html', items = items)
    #===========================================================================
    # else:
    #    return 'sin relacions'
    #===========================================================================

@app.route('/relacion/editarrelacion', methods=['GET', 'POST'])
def editarrelacion():
    init_db(db_session)
    p = db_session.query(Relacion).filter_by(codigo=request.args.get('cod')).first()
    form = RelacionFormulario(request.form,p)
    relacion = db_session.query(Relacion).filter_by(id=form.id.data).first()
    if request.method == 'POST' and form.validate():
        form.populate_obj(relacion)
        db_session.merge(relacion)
        db_session.commit()
        return redirect('/relacion/administrarrelacion')
    else:
        flash_errors(form)
    return render_template('relacion/editarrelacion.html', form=form)

@app.route('/relacion/eliminarrelacion', methods=['GET', 'POST'])
def eliminarrelacion():
    cod = request.args.get('codigo')
    init_db(db_session)
    relacion = db_session.query(Relacion).filter_by(id=cod).first()
    db_session.delete(relacion)
    db_session.commit()
    return redirect('/relacion/administrarrelacion')

@app.route('/relacion/buscarrelacion', methods=['GET', 'POST'])
def buscarrelacion():
    valor = request.args['patron']
    parametro = request.args['parametro']
    init_db(db_session)
    if valor=='' or valor == None:
        return administrarrelacion()
    else:
        if parametro == 'id_recurso':
            p = db_session.query(Relacion).from_statement("SELECT * FROM relacion where to_char("+parametro+", '99999') ilike '%"+valor+"%'").all()
            #p = db_session.query(Relacion).from_statement("SELECT * FROM relacion where "+parametro+" = CAST("+valor+" AS Int)").all()
        else:
            p = db_session.query(Relacion).from_statement("SELECT * FROM relacion where "+parametro+" ilike '%"+valor+"%'").all()
    #p = db_session.query(Relacion).filter(Relacion.codigo.like('%'+valor+'%'))
        return render_template('relacion/administrarrelacion.html', relacions = p)

@app.route('/relacion/administrarrelacion')
def administrarrelacion():
    init_db(db_session)
    relaciones = db_session.query(Relacion).order_by(Relacion.id)
    return render_template('relacion/administrarrelacion.html', relaciones = relaciones)

"""Lanza un mensaje de error en caso de que la pagina solicitada no exista"""
@app.errorhandler(404)
def page_not_found(error):
    return 'Esta Pagina no existe', 404

"""Cierra la sesion de la conexion con la base de datos"""
@app.after_request
def shutdown_session(response):
    db_session.remove()
    return response

""" Obtiene los items de un proyecto, para lo cual obtiene el id del proyecto guardado en la session"""
def getItemByProyecto():
    id_proy =  session['pry']
    items = db_session.query(Item).join(Fase, Fase.id == Item.id_fase).join(Proyecto, Proyecto.id == Fase.id_proyecto).filter(Proyecto.id == id_proy).all()
    return items

def getItemByProyBefoActFase(id_item):
    id_proy = session['pry']
    fase_actual = db_session.query(Item.id_fase).filter_by(id = id_item)
    items = db_session.query(Item).join(Fase, Fase.id == Item.id_fase).join(Proyecto, Proyecto.id == Fase.id_proyecto).filter(Proyecto.id == id_proy).filter(Fase.id >= fase_actual).filter(Item.id != id_item).all()
    return items