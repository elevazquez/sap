from com.py.sap.loginC import app
from flask import render_template, session

from com.py.sap.util.database import init_db, engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import DatabaseError
from flask import Flask, render_template, request, redirect, url_for, flash 
from com.py.sap.des.mod.Fase import Fase
from com.py.sap.adm.mod.Proyecto import Proyecto
from com.py.sap.des.fase.FaseFormulario import FaseFormulario
import flask, flask.views
import os

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
class FaseControlador(flask.views.MethodView):
    def get(self):
        return flask.render_template('fase.html')
    
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ),'error')

""" Funcion para agregar registros a la tabla Fase""" 
@app.route('/fase/nuevafase', methods=['GET', 'POST'])
def nuevafase():
    form = FaseFormulario(request.form)
    init_db(db_session)
    pro = db_session.query(Proyecto).filter_by(id=session['pry']).first()
    form.proyecto.data = pro.nombre
    if request.method == 'POST' and form.validate():
        init_db(db_session)
        if form.fecha_inicio.data > form.fecha_fin.data :
            flash('La fecha de inicio no puede ser mayor que la fecha de finalizacion','error')
            return render_template('fase/nuevafase.html', form=form) 
        try:
            fase = Fase(form.nro_orden.data, form.nombre.data, form.descripcion.data, 
                    form.estado.data, form.fecha_inicio.data, 
                    form.fecha_fin.data, pro.id)
            db_session.add(fase)
            db_session.commit()
            flash('La fase ha sido registrada con exito','info')
            return redirect('/fase/administrarfase')
        except DatabaseError, e:
            flash('Error en la Base de Datos' + e.args[0],'error')
            return render_template('fase/nuevafase.html', form=form)
    else:
        flash_errors(form)  
    return render_template('fase/nuevafase.html', form=form)

@app.route('/fase/editarfase', methods=['GET', 'POST'])
def editarfase():
    form = FaseFormulario(request.form)
    nro = request.args.get('nro')
    init_db(db_session)
    pro = db_session.query(Proyecto).filter_by(id=session['pry']).first()
    fase = db_session.query(Fase).filter_by(nro_orden=nro).filter_by(id_proyecto=pro.id).first()  
    form.proyecto.data = pro.nombre
    flash(fase,'error')
    if request.method == 'POST' and form.validate():
        if form.fecha_inicio.data > form.fecha_fin.data :
            flash('La fecha de inicio no puede ser mayor que la fecha de finalizacion','error')
            return render_template('fase/editarfase.html', form=form) 
        try:
            form.populate_obj(fase)
            db_session.merge(fase)
            db_session.commit()
            return redirect('/fase/administrarfase')
        except DatabaseError, e:
            flash('Error en la Base de Datos' + e.args[0],'error')
            return render_template('fase/editarfase.html', form=form)
    else:
        flash_errors(form) 
    return render_template('fase/editarfase.html', form=form)

@app.route('/fase/eliminarfase', methods=['GET', 'POST'])
def eliminarfase():
    try:
        nro = request.args.get('nro')
        init_db(db_session)
        fase = db_session.query(Fase).filter_by(nro_orden=nro).filter_by(id_proyecto=session['pry']).first()  
        init_db(db_session)
        db_session.delete(fase)
        db_session.commit()
        return redirect('/fase/administrarfase')
    except DatabaseError, e:
            flash('Error en la Base de Datos' + e.args[0],'error')
            return render_template('/fase/administrarfase.html')
    
@app.route('/fase/buscarfase', methods=['GET', 'POST'])
def buscarfase():
    valor = request.args['patron']
    parametro = request.args['parametro']
    init_db(db_session)
    if valor == "" : 
        p = db_session.query(Fase).filter_by(id_proyecto=session['pry']).order_by(Fase.nro_orden)
    elif parametro == 'nro_orden' or parametro == 'id_proyecto':
        p = db_session.query(Fase).from_statement("SELECT * FROM fase where to_char("+parametro+", '99999') ilike '%"+valor+"%' and id_proyecto='"+session['pry'].__repr__()+"'").all()
    elif parametro == 'fecha_inicio' or parametro == 'fecha_fin':
        p = db_session.query(Fase).from_statement("SELECT * FROM fase where to_char("+parametro+", 'YYYY-mm-dd') ilike '%"+valor+"%' and id_proyecto='"+session['pry'].__repr__()+"'").all()
    else:
        p = db_session.query(Fase).from_statement("SELECT * FROM fase where "+parametro+" ilike '%"+valor+"%' and id_proyecto='"+session['pry'].__repr__()+"'").all()
    return render_template('fase/administrarfase.html', fases = p)

@app.route('/fase/administrarfase')
def administrarfase():
    init_db(db_session)
    fases = db_session.query(Fase).filter_by(id_proyecto=session['pry']).order_by(Fase.nro_orden)
    return render_template('fase/administrarfase.html', fases = fases)

"""Lanza un mensaje de error en caso de que la pagina solicitada no exista"""
@app.errorhandler(404)
def page_not_found(error):
    return 'Esta Pagina no existe', 404

"""Cierra la sesion de la conexion con la base de datos"""
@app.after_request
def shutdown_session(response):
    db_session.remove()
    return response


