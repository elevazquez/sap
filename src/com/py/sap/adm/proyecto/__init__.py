from com.py.sap.loginC import app

from com.py.sap.util.database import init_db, engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import Flask, render_template, request, redirect, url_for, flash 
from com.py.sap.adm.mod.Proyecto import Proyecto
from com.py.sap.adm.proyecto.ProyFormulario import ProyFormulario
import flask, flask.views
import os

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
class ProyControlador(flask.views.MethodView):
    def get(self):
        return flask.render_template('proyecto.html')
    
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ),'error')
                
""" Funcion para agregar registros a la tabla Proyecto""" 
@app.route('/proyecto/nuevoproyecto', methods=['GET', 'POST'])
def nuevoproyecto():
    form = ProyFormulario(request.form)
    if request.method == 'POST' and form.validate():
        init_db(db_session)
        pry = Proyecto(form.nombre.data, form.descripcion.data, 
                    form.estado.data, form.cant_miembros.data, 
                    form.fecha_inicio.data, form.fecha_fin.data, 
                    form.fecha_ultima_mod.data, form.usuario_lider.data)
        db_session.add(pry)
        db_session.commit()
        flash('El Proyecto ha sido registrado con exito','info')
        return redirect('/proyecto/administrarproyecto') 
    return render_template('proyecto/nuevoproyecto.html', form=form)

@app.route('/proyecto/editarproyecto', methods=['GET', 'POST'])
def editarproyecto():
    init_db(db_session)
    p = db_session.query(Proyecto).filter_by(nombre=request.args.get('nom')).first()  
    form = ProyFormulario(request.form,p)
    proyecto = db_session.query(Proyecto).filter_by(nombre=form.nombre.data).first()  
    if request.method == 'POST' and form.validate():
        form.populate_obj(proyecto)
        db_session.merge(proyecto)
        db_session.commit()
        return redirect('/proyecto/administrarproyecto')
    else:
        flash_errors(form)
    return render_template('proyecto/editarproyecto.html', form=form)

@app.route('/proyecto/eliminarproyecto', methods=['GET', 'POST'])
def eliminarproyecto():
    nom = request.args.get('nom')
    init_db(db_session)
    proyecto = db_session.query(Proyecto).filter_by(nombre=nom).first()  
    init_db(db_session)
    db_session.delete(proyecto)
    db_session.commit()
    return redirect('/proyecto/administrarproyecto')
    
@app.route('/proyecto/buscarproyecto', methods=['GET', 'POST'])
def buscarproyecto():
    valor = request.args['patron']
    parametro = request.args['parametro']
    init_db(db_session)
    if valor == "" : 
        administrarproyecto()
    if parametro == 'cant_miembros' or parametro == 'id_usuario_lider':
        p = db_session.query(Proyecto).from_statement("SELECT * FROM proyecto where "+parametro+" = CAST("+valor+" AS Int)").all()
    else:
        p = db_session.query(Proyecto).from_statement("SELECT * FROM proyecto where "+parametro+" ilike '%"+valor+"%'").all()
    return render_template('proyecto/administrarproyecto.html', proyectos = p)
    
    
    valor = request.args['patron']
    init_db(db_session)
    r = db_session.query(Proyecto).filter_by(nombre=valor)
    if r == None:
        return 'no existe concordancia'
    return render_template('proyecto/administrarproyecto.html', proyectos = r)

@app.route('/proyecto/administrarproyecto')
def administrarproyecto():
    init_db(db_session)
    proyectos = db_session.query(Proyecto).order_by(Proyecto.nombre)
    return render_template('proyecto/administrarproyecto.html', proyectos = proyectos)

"""Lanza un mensaje de error en caso de que la pagina solicitada no exista"""
@app.errorhandler(404)
def page_not_found(error):
    return 'Esta Pagina no existe', 404

"""Cierra la sesion de la conexion con la base de datos"""
@app.after_request
def shutdown_session(response):
    db_session.remove()
    return response