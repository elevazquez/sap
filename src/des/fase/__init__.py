from loginC import app

from util.database import init_db, engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import DatabaseError
from sqlalchemy import func, Integer
from flask import Flask, render_template, request, redirect, url_for, flash, session 
from adm.mod.Proyecto import Proyecto
from des.mod.Fase import Fase
from des.mod.TipoItem import TipoItem
from des.mod.Item import Item
from ges.mod.Relacion import Relacion
from des.fase.FaseFormulario import FaseFormulario
import flask, flask.views
import os
import datetime
from UserPermission import UserPermission, UserRol

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
class FaseControlador(flask.views.MethodView):
    def get(self):
        return flask.render_template('fase.html')
    
def flash_errors(form):
    """Funcion para capturar errores del Formulario"""
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ),'error')

@app.route('/fase/nuevafase', methods=['GET', 'POST'])
def nuevafase():
    """ Funcion para agregar registros a la tabla Fase"""
    permission =UserPermission('LIDER PROYECTO', int(session['pry']))
    if permission.can()==False:
        flash('No posee los permisos suficientes para realizar la operacion', 'info')
        return render_template('fase/administrarfase.html') 
    form = FaseFormulario(request.form)
    ##init_db(db_session)
    n = db_session.query(func.max(Fase.nro_orden, type_=Integer)).filter_by(id_proyecto=session['pry']).scalar()
    if n != None :
        form.nro_orden.default = n + 1
    else :
        form.nro_orden.default = 1
    pro = db_session.query(Proyecto).filter_by(id=session['pry']).first()
    form.id_proyecto.data = pro.nombre
    form.estado.data = 'Inicial'
    if pro.estado != 'N' :
        flash('No se pueden agregar Fases al Proyecto','info')
        return render_template('fase/administrarfase.html') 
    if request.method == 'POST' and form.validate():
        #init_db(db_session)
        if form.fecha_inicio.data > form.fecha_fin.data :
            flash('La fecha de inicio no puede ser mayor que la fecha de finalizacion','error')
            return render_template('fase/nuevafase.html', form=form) 
        try:
            fase = Fase(form.nro_orden.data, form.nombre.data, form.descripcion.data, 
                    'I', form.fecha_inicio.data, 
                    form.fecha_fin.data, pro.id)
            db_session.add(fase)
            db_session.commit()
            flash('La fase ha sido registrada con exito','info')
            return redirect('/fase/administrarfase')
        except DatabaseError, e:
            if e.args[0].find('duplicate key value violates unique')!=-1:
                flash('Clave unica violada por favor ingrese otro NUMERO de Fase' ,'error')
            else:
                flash('Error en la Base de Datos' + e.args[0],'error')
            return render_template('fase/nuevafase.html', form=form)
    else:
        flash_errors(form)  
    return render_template('fase/nuevafase.html', form=form)

@app.route('/fase/editarfase', methods=['GET', 'POST'])
def editarfase():
    """ Funcion para editar registros de la tabla Fase""" 
    #init_db(db_session)
    permission =UserPermission('LIDER PROYECTO', int(session['pry']))
    if permission.can()==False:
        flash('No posee los permisos suficientes para realizar la operacion', 'info')
        return render_template('fase/administrarfase.html') 
    pro = db_session.query(Proyecto).filter_by(id=session['pry']).first()
    f = db_session.query(Fase).filter_by(nro_orden=request.args.get('nro')).filter_by(id_proyecto=pro.id).first()  
    form = FaseFormulario(request.form,f)
    fase = db_session.query(Fase).filter_by(nro_orden=form.nro_orden.data).filter_by(id_proyecto=pro.id).first()  
    form.id_proyecto.data = pro.nombre
    if fase.estado=='I':
        form.estado.data='Inicial'
    elif fase.estado=='P':
        form.estado.data='En Progreso'
    elif fase.estado=='L':
        form.estado.data='En Linea Base'
    elif fase.estado=='A':
        form.estado.data='Aprobado'
    if pro.estado != 'N' :
        flash('No se pueden modificar Fases del Proyecto','info')
        return render_template('fase/administrarfase.html')
    if fase.estado != 'I' :
        flash('No se pueden modificar Fases que no se encuentren en estado Inicial','info')
        return render_template('fase/administrarfase.html')  
    if request.method == 'POST' and form.validate():
        if form.fecha_inicio.data > form.fecha_fin.data :
            flash('La fecha de inicio no puede ser mayor que la fecha de finalizacion','error')
            return render_template('fase/editarfase.html', form=form)
        try:
            form.populate_obj(fase)
            fase.id_proyecto = pro.id
            if form.estado.data=='Inicial':
                fase.estado='I'
            elif form.estado.data=='En Progreso':
                fase.estado='P'
            elif form.estado.data=='En Linea Base':
                fase.estado='L'
            elif form.estado.data=='Aprobado':
                fase.estado='A' 
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
    """ Funcion para eliminar registros de la tabla Fase""" 
    #init_db(db_session)
    permission =UserPermission('LIDER PROYECTO', int(session['pry']))
    if permission.can()==False:
        flash('No posee los permisos suficientes para realizar la operacion', 'info')
        return render_template('fase/administrarfase.html') 
    pro = db_session.query(Proyecto).filter_by(id=session['pry']).first()
    if pro.estado != 'N' :
        flash('No se pueden eliminar Fases del Proyecto','info')
        return render_template('fase/administrarfase.html')
    f = db_session.query(Fase).filter_by(nro_orden=request.args.get('nro')).filter_by(id_proyecto=session['pry']).first()  
    ti = db_session.query(TipoItem).filter_by(id_fase=f.id).first()
    if ti != None :
        flash('No se pueden eliminar la Fase esta asociada al Tipo Item ' + ti.nombre,'info')
        return render_template('fase/administrarfase.html')  
    if f.estado != 'I' :
        flash('No se pueden eliminar Fases que no se encuentren en estado Inicial','info')
        return render_template('fase/administrarfase.html')  
    try:
        nro = request.args.get('nro')
        #init_db(db_session)
        fase = db_session.query(Fase).filter_by(nro_orden=nro).filter_by(id_proyecto=session['pry']).first()  
        #init_db(db_session)
        db_session.delete(fase)
        db_session.commit()
        return redirect('/fase/administrarfase')
    except DatabaseError, e:
            flash('Error en la Base de Datos' + e.args[0],'info')
            return render_template('/fase/administrarfase.html')
    
@app.route('/fase/buscarfase', methods=['GET', 'POST'])
def buscarfase():
    """ Funcion para buscar registros de la tabla Fase""" 
    valor = request.args['patron']
    parametro = request.args['parametro']
    #init_db(db_session)
    if valor == "" : 
        p = db_session.query(Fase).filter_by(id_proyecto=session['pry']).order_by(Fase.nro_orden)
    elif parametro == 'nro_orden' :
        p = db_session.query(Fase).from_statement("SELECT * FROM fase where to_char("+parametro+", '99999') ilike '%"+valor+"%' and id_proyecto='"+session['pry']+"'").all()
    elif parametro == 'id_proyecto':
        p = db_session.query(Fase).from_statement("SELECT * FROM fase where id_proyecto='"+session['pry']+"' and "+parametro+" in (SELECT id FROM proyecto where nombre ilike '%"+valor+"%')").all()
    elif parametro == 'fecha_inicio' or parametro == 'fecha_fin':
        p = db_session.query(Fase).from_statement("SELECT * FROM fase where to_char("+parametro+", 'YYYY-mm-dd') ilike '%"+valor+"%' and id_proyecto='"+session['pry']+"'").all()
    else:
        p = db_session.query(Fase).from_statement("SELECT * FROM fase where "+parametro+" ilike '%"+valor+"%' and id_proyecto='"+session['pry']+"'").all()
    return render_template('fase/administrarfase.html', fases = p)

@app.route('/fase/buscarfase2', methods=['GET', 'POST'])
def buscarfase2():
    """ Funcion para buscar registros de la tabla Fase""" 
    valor = request.args['patron']
    parametro = request.args['parametro']
    #init_db(db_session)
    if valor == "" : 
        p = db_session.query(Fase).order_by(Fase.nro_orden)
    elif parametro == 'nro_orden' :
        p = db_session.query(Fase).from_statement("SELECT * FROM fase where to_char("+parametro+", '99999') ilike '%"+valor+"%' ").all()
    elif parametro == 'id_proyecto':
        p = db_session.query(Fase).from_statement("SELECT * FROM fase where "+parametro+" in (SELECT id FROM proyecto where nombre ilike '%"+valor+"%')").all()
    elif parametro == 'fecha_inicio' or parametro == 'fecha_fin':
        p = db_session.query(Fase).from_statement("SELECT * FROM fase where to_char("+parametro+", 'YYYY-mm-dd') ilike '%"+valor+"%' ").all()
    else:
        p = db_session.query(Fase).from_statement("SELECT * FROM fase where "+parametro+" ilike '%"+valor+"%' ").all()
    return render_template('fase/listarfase.html', fases2 = p)

@app.route('/fase/administrarfase')
def administrarfase():
    """ Funcion para listar registros de la tabla Fase""" 
    #init_db(db_session)
    fases = db_session.query(Fase).filter_by(id_proyecto=session['pry']).order_by(Fase.nro_orden)
    return render_template('fase/administrarfase.html', fases = fases)

@app.route('/fase/listarfase')
def listarfase():
    """ Funcion para listar registros de la tabla Fase""" 
    #init_db(db_session)
    fases2 = db_session.query(Fase).order_by(Fase.id_proyecto, Fase.nro_orden)
    return render_template('fase/listarfase.html', fases2 = fases2)

@app.route('/fase/importarfase', methods=['GET', 'POST'])
def importarfase():
    """ Funcion para importar registros a la tabla Fase""" 
    #init_db(db_session)
    permission =UserPermission('LIDER PROYECTO', int(session['pry']))
    if permission.can()==False:
        flash('No posee los permisos suficientes para realizar la operacion', 'info')
        return render_template('fase/administrarfase.html') 
    pro = db_session.query(Proyecto).filter_by(id=session['pry']).first()
    f = db_session.query(Fase).filter_by(nro_orden=request.args.get('nro')).filter_by(id_proyecto=request.args.get('py')).first()  
    form = FaseFormulario(request.form,f)
    fase = db_session.query(Fase).filter_by(nro_orden=form.nro_orden.data).filter_by(id_proyecto=request.args.get('py')).first()  
    form.id_proyecto.data = pro.nombre
    n = db_session.query(func.max(Fase.nro_orden, type_=Integer)).filter_by(id_proyecto=session['pry']).scalar()
    if n != None :
        form.nro_orden.default = n + 1
    else :
        form.nro_orden.default = 1
    form.estado.data = 'Inicial'
    if pro.estado != 'N' :
        flash('No se pueden importar Fases al Proyecto','info')
        return render_template('fase/administrarfase.html') 
    if request.method == 'POST' and form.validate():
        #init_db(db_session)
        if form.fecha_inicio.data > form.fecha_fin.data :
            flash('La fecha de inicio no puede ser mayor que la fecha de finalizacion','error')
            return render_template('fase/importarfase.html', form=form) 
        try:
            fase = Fase(form.nro_orden.data, form.nombre.data, form.descripcion.data, 
                    'I', form.fecha_inicio.data, 
                    form.fecha_fin.data, pro.id)
            db_session.add(fase)
            db_session.commit()
            flash('La fase ha sido importada con exito','info')
            return redirect('/fase/administrarfase')
        except DatabaseError, e:
            if e.args[0].find('duplicate key value violates unique')!=-1:
                flash('Clave unica violada por favor ingrese otro NUMERO de Fase' ,'error')
            else:
                flash('Error en la Base de Datos' + e.args[0],'error')
            return render_template('fase/importarfase.html', form=form)
    else:
        flash_errors(form)  
    return render_template('fase/importarfase.html', form=form)

@app.route('/fase/finalizarfase')
def finalizarfase():
    """ Funcion para finalizar registros de la tabla Fase""" 
    #init_db(db_session)
    permission =UserPermission('LIDER PROYECTO', int(session['pry']))
    if permission.can()==False:
        flash('No posee los permisos suficientes para realizar la operacion', 'info')
        return render_template('fase/administrarfase.html') 
    nro = request.args.get('nro')
    fase = db_session.query(Fase).filter_by(nro_orden=nro).filter_by(id_proyecto=session['pry']).first()
    items = db_session.query(Item).from_statement("Select it.*  from item it, "+ 
                        " (Select  i.codigo cod, max(i.version) vermax from item i, fase f  where i.id_fase = f.id "+
                        " and f.id_proyecto = "+str(session['pry'])+ " and f.id ='"+str(fase.id)+"' group by codigo order by 1 ) s "+
                        " where it.codigo = cod and it.version= vermax order by it.codigo ")
    i = db_session.query(Item).from_statement("Select it.*  from item it, "+ 
                        " (Select  i.codigo cod, max(i.version) vermax from item i, fase f  where i.id_fase = f.id "+
                        " and f.id_proyecto = "+str(session['pry'])+ " and f.id ='"+str(fase.id)+"' group by codigo order by 1 ) s "+
                        " where it.codigo = cod and it.version= vermax order by it.codigo ").first()
    rel = db_session.query(Relacion).from_statement("select * from relacion " +
                        " where id_item_duenho in (Select it.id  from item it, " +
                        " (Select  i.codigo cod, max(i.version) vermax from item i, fase f  where i.id_fase = f.id " + 
                        " and f.id_proyecto = "+str(session['pry'])+" and f.id ="+str(fase.id)+" group by codigo order by 1 ) s " +
                        " where it.codigo = cod and it.version= vermax order by it.codigo )")
    f='S'
    if fase.estado!='P' and fase.estado!='L':
        flash('La fase no puede ser finalizada, debe estar en estado En Progreso','info')
        return redirect('/fase/administrarfase')
    if i==None:
        flash('La fase no puede ser finalizada, no posee items relacionados','info')
        return redirect('/fase/administrarfase')
    else :
        for it in items:
            if it.estado != 'B' :
                f='N'
        if f=='N':
            flash('La fase no puede ser finalizada algun item no se encuentra en Linea Base','info')
            return redirect('/fase/administrarfase')
        else :
            if rel != None:
                for r in rel:
                    itt = db_session.query(Item).filter_by(id=r.id_item).first()
                    if itt.id_fase != fase.id :
                        fas = db_session.query(Fase).filter_by(id=itt.id_fase).first()
                        if fas.nro_orden<fase.nro_orden :
                            if fas.estado!='A' :
                                f='N'
            if f=='N':
                flash('La fase no puede ser finalizada algun item tiene una Relacion con una fase anterior que no ha sido Finalizada','info')
                return redirect('/fase/administrarfase')
            try:
                fase.estado = 'A'
                db_session.merge(fase)
                db_session.commit()
            
                flash('La fase ha sido finalizada con exito','info')
                return redirect('/fase/administrarfase')
            except DatabaseError, e:
                flash('Error en la Base de Datos' + e.args[0],'info')
                return redirect('/fase/administrarfase')
        
@app.errorhandler(404)
def page_not_found(error):
    """Lanza un mensaje de error en caso de que la pagina solicitada no exista"""
    return 'Esta Pagina no existe', 404

@app.after_request
def shutdown_session(response):
    """Cierra la sesion de la conexion con la base de datos"""
    db_session.remove()
    return response