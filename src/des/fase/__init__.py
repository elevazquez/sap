from loginC import app

from util.database import init_db, engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import DatabaseError
from sqlalchemy import func, Integer
from flask import Flask, render_template, request, redirect, url_for, flash, session 
from adm.mod.Proyecto import Proyecto
from des.mod.Fase import Fase
from des.mod.TipoItem import TipoItem
from des.fase.FaseFormulario import FaseFormulario
import flask, flask.views
import os
import datetime

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
    n = db_session.query(func.max(Fase.nro_orden, type_=Integer)).filter_by(id_proyecto=session['pry']).scalar()
    if n != None :
        form.nro_orden.default = n + 1
    else :
        form.nro_orden.default = 1
    pro = db_session.query(Proyecto).filter_by(id=session['pry']).first()
    form.id_proyecto.data = pro.nombre
    if pro.estado != 'N' :
        flash('No se pueden agregar Fases al Proyecto','info')
        return render_template('fase/administrarfase.html') 
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
    init_db(db_session)
    pro = db_session.query(Proyecto).filter_by(id=session['pry']).first()
    f = db_session.query(Fase).filter_by(nro_orden=request.args.get('nro')).filter_by(id_proyecto=pro.id).first()  
    form = FaseFormulario(request.form,f)
    fase = db_session.query(Fase).filter_by(nro_orden=form.nro_orden.data).filter_by(id_proyecto=pro.id).first()  
    form.id_proyecto.data = pro.nombre
    if pro.estado != 'N' :
        flash('No se pueden modificar Fases del Proyecto','info')
        return render_template('fase/administrarfase.html') 
    if request.method == 'POST' and form.validate():
        if form.fecha_inicio.data > form.fecha_fin.data :
            flash('La fecha de inicio no puede ser mayor que la fecha de finalizacion','error')
            return render_template('fase/editarfase.html', form=form) 
        try:
            form.populate_obj(fase)
            fase.id_proyecto = pro.id
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
    init_db(db_session)
    pro = db_session.query(Proyecto).filter_by(id=session['pry']).first()
    if pro.estado != 'N' :
        flash('No se pueden eliminar Fases del Proyecto','info')
        return render_template('fase/administrarfase.html')
    f = db_session.query(Fase).filter_by(nro_orden=request.args.get('nro')).filter_by(id_proyecto=session['pry']).first()  
    ti = db_session.query(TipoItem).filter_by(id_fase=f.id).first()
    if ti != None :
        flash('No se pueden eliminar la Fase esta asociada al Tipo Item ' + ti.nombre,'info')
        return render_template('fase/administrarfase.html')  
    try:
        nro = request.args.get('nro')
        init_db(db_session)
        fase = db_session.query(Fase).filter_by(nro_orden=nro).filter_by(id_proyecto=session['pry']).first()  
        init_db(db_session)
        db_session.delete(fase)
        db_session.commit()
        return redirect('/fase/administrarfase')
    except DatabaseError, e:
            flash('Error en la Base de Datos' + e.args[0],'info')
            return render_template('/fase/administrarfase.html')
    
@app.route('/fase/buscarfase', methods=['GET', 'POST'])
def buscarfase():
    valor = request.args['patron']
    parametro = request.args['parametro']
    init_db(db_session)
    if valor == "" : 
        p = db_session.query(Fase).filter_by(id_proyecto=session['pry']).order_by(Fase.nro_orden)
    elif parametro == 'nro_orden' or parametro == 'id_proyecto':
        p = db_session.query(Fase).from_statement("SELECT * FROM fase where to_char("+parametro+", '99999') ilike '%"+valor+"%' and id_proyecto='"+session['pry']+"'").all()
    elif parametro == 'fecha_inicio' or parametro == 'fecha_fin':
        p = db_session.query(Fase).from_statement("SELECT * FROM fase where to_char("+parametro+", 'YYYY-mm-dd') ilike '%"+valor+"%' and id_proyecto='"+session['pry']+"'").all()
    else:
        p = db_session.query(Fase).from_statement("SELECT * FROM fase where "+parametro+" ilike '%"+valor+"%' and id_proyecto='"+session['pry']+"'").all()
    return render_template('fase/administrarfase.html', fases = p)

@app.route('/fase/administrarfase')
def administrarfase():
    init_db(db_session)
    fases = db_session.query(Fase).filter_by(id_proyecto=session['pry']).order_by(Fase.nro_orden)
    return render_template('fase/administrarfase.html', fases = fases)

@app.route('/fase/listarfase')
def listarfase():
    init_db(db_session)
    fases2 = db_session.query(Fase).order_by(Fase.id_proyecto, Fase.nro_orden)
    return render_template('fase/listarfase.html', fases2 = fases2)

""" Funcion para importar registros a la tabla Fase""" 
@app.route('/fase/importarfase', methods=['GET', 'POST'])
def importarfase():
    init_db(db_session)
    pro = db_session.query(Proyecto).filter_by(id=session['pry']).first()
    f = db_session.query(Fase).filter_by(nro_orden=request.args.get('nro')).filter_by(id_proyecto=request.args.get('py')).first()  
    form = FaseFormulario(request.form,f)
    fase = db_session.query(Fase).filter_by(nro_orden=form.nro_orden.data).filter_by(id_proyecto=request.args.get('py')).first()  
    form.id_proyecto.data = pro.nombre
    n = db_session.query(func.max(Fase.nro_orden, type_=Integer)).filter_by(id_proyecto=session['pry']).scalar()
    form.nro_orden.default = n + 1
    if pro.estado != 'N' :
        flash('No se pueden importar Fases al Proyecto','info')
        return render_template('fase/administrarfase.html') 
    if request.method == 'POST' and form.validate():
        init_db(db_session)
        if form.fecha_inicio.data > form.fecha_fin.data :
            flash('La fecha de inicio no puede ser mayor que la fecha de finalizacion','error')
            return render_template('fase/importarfase.html', form=form) 
        try:
            fase = Fase(form.nro_orden.data, form.nombre.data, form.descripcion.data, 
                    form.estado.data, form.fecha_inicio.data, 
                    form.fecha_fin.data, pro.id)
            db_session.add(fase)
            db_session.commit()
            flash('La fase ha sido importada con exito','info')
            return redirect('/fase/administrarfase')
        except DatabaseError, e:
            flash('Error en la Base de Datos' + e.args[0],'error')
            return render_template('fase/importarfase.html', form=form)
    else:
        flash_errors(form)  
    return render_template('fase/importarfase.html', form=form)

"""Lanza un mensaje de error en caso de que la pagina solicitada no exista"""
@app.errorhandler(404)
def page_not_found(error):
    return 'Esta Pagina no existe', 404

"""Cierra la sesion de la conexion con la base de datos"""
@app.after_request
def shutdown_session(response):
    db_session.remove()
    return response