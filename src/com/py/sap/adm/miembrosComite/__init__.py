from com.py.sap.loginC import app

from com.py.sap.util.database import init_db, engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import DatabaseError
from flask import Flask, render_template, request, redirect, url_for, flash, session 
from com.py.sap.adm.mod.Proyecto import Proyecto
from com.py.sap.adm.mod.Usuario import Usuario
from com.py.sap.adm.mod.MiembrosComite import MiembrosComite
from com.py.sap.adm.miembrosComite.MiembrosComiteFormulario import MiembrosComiteFormulario
import flask, flask.views
import os
import datetime

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
class MiembrosComiteControlador(flask.views.MethodView):
    def get(self):
        return flask.render_template('miembrosComite.html')
    
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ),'error')

""" Funcion para agregar registros a la tabla MiembrosComite""" 
@app.route('/miembrosComite/nuevomiembrosComite', methods=['GET', 'POST'])
def nuevomiembrosComite():
    init_db(db_session)
    pro = db_session.query(Proyecto).filter_by(id=session['pry']).first()
    u = db_session.query(Usuario).filter_by(usuario=request.args.get('usu')).first()  
    form = MiembrosComiteFormulario(request.form,u)
    usuario = db_session.query(Usuario).filter_by(usuario=form.usuario.data).first()
    cant = db_session.query(MiembrosComite).filter_by(id_proyecto=pro.id).count()
    if pro.estado != 'N' :
        flash('No se pueden asignar Miembros al Comite de Cambios','info')
        return render_template('miembrosComite/administrarmiembrosComite.html')
    if cant == pro.cant_miembros :
        flash('No se pueden asignar Miembros al Comite de Cambios, numero maximo de miembros alcanzado','info')
        return render_template('miembrosComite/administrarmiembrosComite.html')  
    if request.method == 'POST' and form.validate():
        init_db(db_session)
        try:
            miembrosComite = MiembrosComite(pro.id, usuario.id)
            db_session.add(miembrosComite)
            db_session.commit()
            flash('Se ha asignado el usario al Comite de Cambios','info')
            return redirect('/miembrosComite/administrarmiembrosComite')
        except DatabaseError, e:
            flash('Error en la Base de Datos' + e.args[0],'error')
            return render_template('miembrosComite/nuevomiembrosComite.html', form=form)
    else:
        flash_errors(form)  
    return render_template('miembrosComite/nuevomiembrosComite.html', form=form)

@app.route('/miembrosComite/eliminarmiembrosComite', methods=['GET', 'POST'])
def eliminarmiembrosComite():
    init_db(db_session)
    pro = db_session.query(Proyecto).filter_by(id=session['pry']).first()
    if pro.estado != 'N' :
        flash('No se pueden desasignar Miembros al Comites de Cambios','info')
        return render_template('miembrosComite/administrarmiembrosComite.html')
    if pro.id_usuario_lider.__repr__() == request.args.get('usu'):
        flash('No se pueden desasignar al Lider de Proyecto del Comite de Cambios','info')
        return render_template('miembrosComite/administrarmiembrosComite.html')   
    try:
        init_db(db_session)
        miembrosComite = db_session.query(MiembrosComite).filter_by(id=request.args.get('id_mc')).first()  
        init_db(db_session)
        db_session.delete(miembrosComite)
        db_session.commit()
        return redirect('/miembrosComite/administrarmiembrosComite')
    except DatabaseError, e:
            flash('Error en la Base de Datos' + e.args[0],'error')
            return render_template('/miembrosComite/administrarmiembrosComite.html')
    
@app.route('/miembrosComite/buscarmiembrosComite', methods=['GET', 'POST'])
def buscarmiembrosComite():
    valor = request.args['patron']
    parametro = request.args['parametro']
    init_db(db_session)
    if valor == "" : 
        p = db_session.query(MiembrosComite).filter_by(id_proyecto=session['pry'])
    elif parametro == 'id_usuario' :
        p = db_session.query(MiembrosComite).from_statement("SELECT * FROM miembros_comite where to_char("+parametro+", '99999') ilike '%"+valor+"%' and id_proyecto='"+session['pry'].__repr__()+"'").all()
    return render_template('miembrosComite/administrarmiembrosComite.html', miembrosComites = p)

@app.route('/miembrosComite/administrarmiembrosComite')
def administrarmiembrosComite():
    init_db(db_session)
    miembrosComites = db_session.query(MiembrosComite).filter_by(id_proyecto=session['pry']).order_by(MiembrosComite.id_usuario)
    return render_template('miembrosComite/administrarmiembrosComite.html', miembrosComites = miembrosComites)

@app.route('/miembrosComite/listarusuarios')
def listarusuarios():
    init_db(db_session)
    usuarios = db_session.query(Usuario).from_statement("select * from usuario where id not in (select id_usuario from miembros_comite where id_proyecto='"+session['pry']+"')").all()
    return render_template('miembrosComite/listarusuarios.html', usuarios = usuarios)
    
"""Lanza un mensaje de error en caso de que la pagina solicitada no exista"""
@app.errorhandler(404)
def page_not_found(error):
    return 'Esta Pagina no existe', 404

"""Cierra la sesion de la conexion con la base de datos"""
@app.after_request
def shutdown_session(response):
    db_session.remove()
    return response