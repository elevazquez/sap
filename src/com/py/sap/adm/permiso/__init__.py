from com.py.sap.loginC import app
from com.py.sap.util.database import init_db, engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import Flask, render_template, request, redirect, url_for, flash 
from com.py.sap.adm.mod.Permiso import Permiso
from com.py.sap.adm.permiso.PermisoFormulario import PermisoFormulario
import flask, flask.views
import os

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
class RolControlador(flask.views.MethodView):
    def get(self):
        return flask.render_template('rol.html')

def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ))

""" Funcion para agregar registros a la tabla Permiso""" 
@app.route('/permiso/nuevopermiso', methods=['GET', 'POST'])
def nuevopermiso():
    form = PermisoFormulario(request.form)
    if request.method == 'POST' and form.validate():
        init_db(db_session)
        permiso = Permiso(form.codigo.data, form.descripcion.data, form.recurso.data)
        db_session.add(permiso)
        db_session.commit()
        flash('El permiso ha sido registrado con exito','info')
        return redirect('/permiso/administrarpermiso')
    return render_template('permiso/nuevopermiso.html', form=form)

@app.route('/permiso/editarpermiso', methods=['GET', 'POST'])
def editarpermiso():
    form = PermisoFormulario(request.form)
    init_db(db_session)
    permiso = db_session.query(Permiso).filter_by(codigo=form.nombre.data).first()  
    if request.method == 'POST' and form.validate():
        form.populate_obj(permiso)
        init_db(db_session)
        db_session.merge(permiso)
        db_session.commit()
        return redirect('/permiso/administrarpermiso')
    return render_template('permiso/editarpermiso.html', form=form)

@app.route('/permiso/eliminarpermiso', methods=['GET', 'POST'])
def eliminarpermiso():
    #rol = request.current_user
    form = PermisoFormulario(request.form)
    init_db(db_session)
    permiso = db_session.query(Permiso).filter_by(nombre=form.codigo.data).first()  
    #form = RolFormulario(request.form, rol)
    if request.method == 'POST' :
        form.populate_obj(permiso)
        init_db(db_session)
        db_session.delete(permiso)
        db_session.commit()
        return redirect('/permiso/administrarpermiso')
    return render_template('permiso/eliminarpermiso.html', form=form)

@app.route('/permiso/buscarpermiso', methods=['GET', 'POST'])
def buscarpermiso():
    valor = request.args['patron']
    init_db(db_session)
    p = db_session.query(Permiso).filter_by(codigo=valor)
    return render_template('permiso/administrarpermiso.html', permisos = p)

@app.route('/permiso/administrarpermiso')
def administrarpermiso():
    init_db(db_session)
    permisos = db_session.query(Permiso).order_by(Permiso.id)
    return render_template('permiso/administrarpermiso.html', permisos = permisos)
[]
"""Lanza un mensaje de error en caso de que la pagina solicitada no exista"""
@app.errorhandler(404)
def page_not_found(error):
    return 'Esta Pagina no existe', 404

"""Cierra la sesion de la conexion con la base de datos"""
@app.after_request
def shutdown_session(response):
    db_session.remove()
    return response

