from loginC import app

from util.database import init_db, engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import DatabaseError
from flask import Flask, render_template, request, redirect, url_for, flash 
from des.mod.Atributo import Atributo
from des.atributo.AtributoFormulario import AtributoFormulario
import flask, flask.views
import os

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
class AtributoControlador(flask.views.MethodView):
    def get(self):
        return flask.render_template('atributo.html')
    
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ),'error')
                
""" Funcion para agregar registros a la tabla ATributos""" 
@app.route('/atributo/nuevoatributo', methods=['GET', 'POST'])
def nuevoatributo():
        form = AtributoFormulario(request.form)
        if request.method == 'POST' and form.validate():
            init_db(db_session)
            try: 
                att = Atributo( form.codigo.data, form.nombre.data, form.descripcion.data, form.id_tipo_atributo.data)
                db_session.add(att)
                db_session.commit()
                flash('El Atributo ha sido registrado con exito','info')
                return redirect('/atributo/administraratributo') 
            except DatabaseError, e:
                flash('Error en la Base de Datos' + e.args[0],'error')
                return render_template('usuario/nuevousuario.html', form=form)
        else:
            flash_errors(form) 
            return render_template('atributo/nuevoatributo.html', form=form)
 

@app.route('/atributo/editaratributo', methods=['GET', 'POST'])
def editaratributo():
    form = AtributoFormulario(request.form)
    init_db(db_session)
    atributo = db_session.query(Atributo).filter_by(codigo=form.codigo.data).first()  
    if request.method == 'POST' and form.validate():
        try:
            form.populate_obj(atributo)
            db_session.merge(atributo)
            db_session.commit()
            return redirect('/atributo/administraratributo')
        except DatabaseError, e:
            flash('Error en la Base de Datos' + e.args[0],'error')
            return render_template('atributo/editaratributo.html', form=form)
    else:
        flash_errors(form)
        return render_template('atributo/editaratributo.html', form=form)




@app.route('/atributo/eliminaratributo', methods=['GET', 'POST'])
def eliminaratributo():
    try:
        cod = request.args.get('codigo')
        init_db(db_session)
        atributo = db_session.query(Atributo).filter_by(codigo=cod).first()
        init_db(db_session)
        db_session.delete(atributo)
        db_session.commit()
        return redirect('/atributo/administraratributo')
    except DatabaseError, e:
            flash('Error en la Base de Datos' + e.args[0],'error')
            return render_template('atributo/eliminaratributo.html')
    
@app.route('/atributo/buscaratributo', methods=['GET', 'POST'])
def buscaratributo():
    valor = request.args['patron']
    parametro = request.args['parametro']
    init_db(db_session)
    if valor == "" : 
        administraratributo()
    if parametro == 'id_tipo_atributo':
        p = db_session.query(Atributo).from_statement("SELECT a.* FROM atributo a , tipo_atributo ta where ta.nombre  ilike '%"+valor+"%' and a.id_tipo_atributo= ta.id").all()
    else:
        p = db_session.query(Atributo).from_statement("SELECT * FROM atributo where "+parametro+" ilike '%"+valor+"%'").all()
    return render_template('atributo/administraratributo.html', atributos = p)
    
    
    valor = request.args['patron']
    init_db(db_session)
    r = db_session.query(Atributo).filter_by(nombre=valor)
    if r == None:
        return 'No existe concordancia'
    return render_template('atributo/administraratributo.html', atributos = r)

@app.route('/atributo/administraratributo')
def administraratributo():
    init_db(db_session)
    atributos = db_session.query(Atributo).order_by(Atributo.nombre)
    return render_template('atributo/administraratributo.html', atributos = atributos)

"""Lanza un mensaje de error en caso de que la pagina solicitada no exista"""
@app.errorhandler(404)
def page_not_found(error):
    return 'Esta Pagina no existe', 404

"""Cierra la sesion de la conexion con la base de datos"""
@app.after_request
def shutdown_session(response):
    db_session.remove()
    return response