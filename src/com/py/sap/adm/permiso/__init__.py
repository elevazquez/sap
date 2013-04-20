from com.py.sap.loginC import app
from com.py.sap.util.database import init_db, engine
import sqlalchemy
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import Flask, render_template, request, redirect, url_for, flash 
from com.py.sap.adm.mod.Permiso import Permiso
from com.py.sap.adm.mod.Recurso import Recurso
from com.py.sap.adm.permiso.PermisoFormulario import PermisoFormulario
import flask, flask.views
import os

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
class PermisoControlador(flask.views.MethodView):
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
    init_db(db_session)
    p = db_session.query(Permiso).filter_by(codigo=request.args.get('codigo')).first()
    form = PermisoFormulario(request.form,p)
    permiso = db_session.query(Permiso).filter_by(codigo=request.args.get('codigo')).first()
    if request.method == 'POST':
        print(form.id_recurso.data)
        print(form.codigo.data)
        print(form.descripcion.data)
        #form.populate_obj(permiso)
        permiso.id_recurso=form.id_recurso.data
        permiso.descripcion=form.descripcion.data
        db_session.merge(permiso)
        db_session.commit()
        return redirect('/permiso/administrarpermiso')
    return render_template('permiso/editarpermiso.html', form=form)

@app.route('/permiso/eliminarpermiso', methods=['GET', 'POST'])
def eliminarpermiso():
    cod = request.args.get('codigo')
    init_db(db_session)
    rol = db_session.query(Permiso).filter_by(codigo=cod).first()
    db_session.delete(rol)
    db_session.commit()
    return redirect('/permiso/administrarpermiso')

@app.route('/permiso/buscarpermiso', methods=['GET', 'POST'])
def buscarpermiso():
    valor = request.args['patron']
    parametro = request.args['parametro']
    init_db(db_session)
    if valor=='':
        administrarpermiso()
    if parametro == 'id_recurso':
        p = db_session.query(Permiso).from_statement("SELECT * FROM permiso where "+parametro+" = CAST("+valor+" AS Int)").all()
    else:
        p = db_session.query(Permiso).from_statement("SELECT * FROM permiso where "+parametro+" ilike '%"+valor+"%'").all()
    #p = db_session.query(Permiso).filter(Permiso.codigo.like('%'+valor+'%'))
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

