from loginC import app

from util.database import init_db, engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import DatabaseError
from sqlalchemy import func, Integer
from flask import Flask, render_template, request, redirect, url_for, flash, session 
from adm.mod.Proyecto import Proyecto
from des.mod.TipoAtributo import TipoAtributo
from des.mod.Atributo import Atributo
from des.tipoAtributo.TipoAtributoFormulario import TipoAtributoFormulario
import flask, flask.views
import os
import datetime

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
class TipoAtributoControlador(flask.views.MethodView):
    def get(self):
        return flask.render_template('tipoAtributo.html')
    
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ),'error')


@app.route('/tipoAtributo/nuevotipoAtributo', methods=['GET', 'POST'])
def nuevotipoAtributo():
    """ Funcion para agregar registros a la tabla TipoAtributo""" 
    
    form = TipoAtributoFormulario(request.form)
    ##init_db(db_session)
    if request.method == 'POST' and form.validate():
        ##init_db(db_session)
        try:
            tipoAtributo = TipoAtributo( form.nombre.data, form.descripcion.data)
            db_session.add(tipoAtributo)
            db_session.commit()
            flash('El Tipo Atributo ha sido registrado con exito','info')
            return redirect('/tipoAtributo/administrartipoAtributo')
        except DatabaseError, e:
            if e.args[0].find('duplicate key value violates unique')!=-1:
                flash('Clave unica violada por favor ingrese otro CODIGO para el Tipo de Atributo' ,'error')
            else:
                flash('Error en la Base de Datos' + e.args[0],'error')
            return render_template('tipoAtributo/nuevotipoAtributo.html', form=form)
    else:
        flash_errors(form)  
    return render_template('tipoAtributo/nuevotipoAtributo.html', form=form)

@app.route('/tipoAtributo/editartipoAtributo', methods=['GET', 'POST'])
def editartipoAtributo():
    """funcion que permite editar un Tipo de Atributo"""
    ##init_db(db_session)
    f = db_session.query(TipoAtributo).filter_by(nombre=request.args.get('nombre')).first()  
    form = TipoAtributoFormulario(request.form,f)
    tipoAtributo = db_session.query(TipoAtributo).filter_by(nombre=form.nombre.data).first()  
    if request.method == 'POST' and form.validate():
        try:
            form.populate_obj(tipoAtributo)
            db_session.merge(tipoAtributo)
            db_session.commit()
            return redirect('/tipoAtributo/administrartipoAtributo')
        except DatabaseError, e:
            flash('Error en la Base de Datos' + e.args[0],'error')
            return render_template('tipoAtributo/editartipoAtributo.html', form=form)
    else:
        flash_errors(form) 
    return render_template('tipoAtributo/editartipoAtributo.html', form=form)

@app.route('/tipoAtributo/eliminartipoAtributo', methods=['GET', 'POST'])
def eliminartipoAtributo():
    """funcion que permite eliminar un tipo atributo"""
    ##init_db(db_session)
    ta = db_session.query(TipoAtributo).filter_by(nombre=request.args.get('nombre')).first()  
    a = db_session.query(Atributo).filter_by(id_tipo_atributo=ta.id).first()
    if a != None :
        flash('No se puede eliminar el Tipo Atributo, esta asociado al Atributo ' + a.nombre,'info')
        return render_template('tipoAtributo/administrartipoAtributo.html')  
    try:
        cod = request.args.get('nombre')
        ##init_db(db_session)
        tipoAtributo = db_session.query(TipoAtributo).filter_by(nombre=cod).first()  
        ##init_db(db_session)
        db_session.delete(tipoAtributo)
        db_session.commit()
        return redirect('/tipoAtributo/administrartipoAtributo')
    except DatabaseError, e:
            flash('Error en la Base de Datos' + e.args[0],'info')
            return render_template('/tipoAtributo/administrartipoAtributo.html')
    
@app.route('/tipoAtributo/buscartipoAtributo', methods=['GET', 'POST'])
def buscartipoAtributo():
    """funcion que permite buscar tipo de atributos"""
    valor = request.args['patron']
    parametro = request.args['parametro']
    ##init_db(db_session)
    if valor == "" : 
        p = db_session.query(TipoAtributo).order_by(TipoAtributo.nombre)
    else:
        p = db_session.query(TipoAtributo).from_statement("SELECT * FROM tipo_atributo where "+parametro+" ilike '%"+valor+"%' ").all()
    return render_template('tipoAtributo/administrartipoAtributo.html', tipoAtributos = p)

@app.route('/tipoAtributo/administrartipoAtributo')
def administrartipoAtributo():
    ##init_db(db_session)
    tipoAtributos = db_session.query(TipoAtributo).order_by(TipoAtributo.nombre)
    return render_template('tipoAtributo/administrartipoAtributo.html', tipoAtributos = tipoAtributos)


@app.errorhandler(404)
def page_not_found(error):
    """Lanza un mensaje de error en caso de que la pagina solicitada no exista"""
    return 'Esta Pagina no existe', 404


@app.after_request
def shutdown_session(response):
    """Cierra la sesion de la conexion con la base de datos"""
    db_session.remove()
    return response