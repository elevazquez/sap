from com.py.sap.loginC import app

from com.py.sap.util.database import init_db, engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import DatabaseError
from flask import Flask, render_template, request, redirect, url_for, flash 
from com.py.sap.adm.mod.Usuario import Usuario
from com.py.sap.adm.usuario.UsuarioFormulario import UsuarioFormulario
import flask, flask.views
import os
import datetime

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
class UsuarioControlador(flask.views.MethodView):
    def get(self):
        return flask.render_template('usuario.html')
    
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ),'error')
                
""" Funcion para agregar registros a la tabla Usuario""" 
@app.route('/usuario/nuevousuario', methods=['GET', 'POST'])
def nuevousuario():
    form = UsuarioFormulario(request.form)
    if request.method == 'POST' and form.validate():
        init_db(db_session)
        try:
            usu = Usuario(form.usuario.data, form.nombre.data, form.apellido.data, 
                    form.password.data, form.correo.data, form.domicilio.data,
                    form.telefono.data, form.fecha_nac.data)
            db_session.add(usu)
            db_session.commit()
            flash('El Usuario ha sido registrado con exito','info')
            return redirect('/usuario/administrarusuario')
        except DatabaseError, e:
            flash('Error en la Base de Datos' + e.args[0],'error')
            return render_template('usuario/nuevousuario.html', form=form)
    else:
        flash_errors(form) 
    return render_template('usuario/nuevousuario.html', form=form)

@app.route('/usuario/editarusuario', methods=['GET', 'POST'])
def editarusuario():
    init_db(db_session)
    usu = request.args.get('usu')
    form = UsuarioFormulario(request.form)
    usuario = db_session.query(Usuario).filter_by(usuario=usu).first()  
    if request.method == 'POST' and form.validate():
        try:
            form.populate_obj(usuario)
            db_session.merge(usuario)
            db_session.commit()
            return redirect('/usuario/administrarusuario')
        except DatabaseError, e:
            flash('Error en la Base de Datos' + e.args[0],'error')
            return render_template('usuario/editarusuario.html', form=form)
    else:
        flash_errors(form)
    return render_template('usuario/editarusuario.html', form=form)

@app.route('/usuario/eliminarusuario', methods=['GET', 'POST'])
def eliminarusuario():
    try:
        usu = request.args.get('usu')
        init_db(db_session)
        usuario = db_session.query(Usuario).filter_by(usuario=usu).first()  
        init_db(db_session)
        db_session.delete(usuario)
        db_session.commit()
        return redirect('/usuario/administrarusuario')
    except DatabaseError, e:
            flash('Error en la Base de Datos' + e.args[0],'error')
            return render_template('usuario/administrarusuario.html')
    
@app.route('/usuario/buscarusuario', methods=['GET', 'POST'])
def buscarusuario():
    valor = request.args['patron']
    parametro = request.args['parametro']
    init_db(db_session)
    if valor == "" : 
        administrarusuario()
    if parametro == 'fecha_nac' :
        p = db_session.query(Usuario).from_statement("SELECT * FROM usuario where to_char("+parametro+", 'YYYY-mm-dd') ilike '%"+valor+"%'").all()
    else:
        p = db_session.query(Usuario).from_statement("SELECT * FROM usuario where "+parametro+" ilike '%"+valor+"%'").all()
    return render_template('usuario/administrarusuario.html', usuarios = p)   
    valor = request.args['patron']
    init_db(db_session)
    r = db_session.query(Usuario).filter_by(usuario=valor)
    if r == None:
        return 'no existe concordancia'
    return render_template('usuario/administrarusuario.html', usuarios = r)

@app.route('/usuario/administrarusuario')
def administrarusuario():
    init_db(db_session)
    usuarios = db_session.query(Usuario).order_by(Usuario.usuario)
    return render_template('usuario/administrarusuario.html', usuarios = usuarios)

"""Lanza un mensaje de error en caso de que la pagina solicitada no exista"""
@app.errorhandler(404)
def page_not_found(error):
    return 'Esta Pagina no existe', 404

"""Cierra la sesion de la conexion con la base de datos"""
@app.after_request
def shutdown_session(response):
    db_session.remove()
    return response