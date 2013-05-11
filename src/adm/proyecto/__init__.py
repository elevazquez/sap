from loginC import app

from util.database import init_db, engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import DatabaseError
from flask import Flask, render_template, request, redirect, url_for, flash, session
from des.mod.Fase import Fase
from adm.mod.Proyecto import Proyecto
from adm.mod.UsuarioRol import UsuarioRol
from adm.mod.Recurso import Recurso
from adm.mod.Permiso import Permiso
from adm.mod.RolPermiso import RolPermiso
from adm.mod.MiembrosComite import MiembrosComite
from adm.proyecto.ProyFormulario import ProyFormulario
import flask, flask.views
import os
import datetime

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
    """ Se obtiene la fecha actual para almacenar la fecha de ultima actualizacion """
    today = datetime.date.today()
    form = ProyFormulario(request.form)
    if request.method == 'POST' and form.validate():
        init_db(db_session)
        if form.fecha_inicio.data > form.fecha_fin.data :
            flash('La fecha de inicio no puede ser mayor que la fecha de finalizacion','error')
            return render_template('proyecto/nuevoproyecto.html', form=form)
        if form.cant_miembros.data %2 == 0 :
            flash('La cantidad maxima de miembros debe ser impar','error')
            return render_template('proyecto/nuevoproyecto.html', form=form)
        try:
            pry = Proyecto(form.nombre.data, form.descripcion.data, 
                    'N', form.cant_miembros.data, 
                    form.fecha_inicio.data, form.fecha_fin.data, 
                    today, form.usuario_lider.data)
            db_session.add(pry)
            db_session.commit()
            mc = MiembrosComite(pry.id, form.usuario_lider.data)
            db_session.add(mc)
            db_session.commit()
            flash('El Proyecto ha sido registrado con exito','info')
            return redirect('/proyecto/administrarproyecto')
        except DatabaseError, e:
            flash('Error en la Base de Datos' + e.args[0],'error')
            return render_template('proyecto/nuevoproyecto.html', form=form)
    else:
        flash_errors(form) 
    return render_template('proyecto/nuevoproyecto.html', form=form)

@app.route('/proyecto/editarproyecto', methods=['GET', 'POST'])
def editarproyecto():
    """ Se obtiene la fecha actual para almacenar la fecha de ultima actualizacion """
    today = datetime.date.today()
    init_db(db_session)
    p = db_session.query(Proyecto).filter_by(nombre=request.args.get('nom')).first()  
    form = ProyFormulario(request.form,p)
    proyecto = db_session.query(Proyecto).filter_by(nombre=form.nombre.data).first()
    mc = proyecto.id_usuario_lider
    if proyecto.estado == 'N' :
        form.estado.data = 'Nuevo'
    elif proyecto.estado == 'P' :
        form.estado.data = 'En Progreso'
    elif proyecto.estado == 'A' :
        form.estado.data = 'Anulado'
    elif proyecto.estado == 'F' :
        form.estado.data = 'Finalizado'
    if request.method == 'POST' and form.validate():
        if form.fecha_inicio.data > form.fecha_fin.data :
            flash('La fecha de inicio no puede ser mayor que la fecha de finalizacion','error')
            return render_template('proyecto/editarproyecto.html', form=form)
        if form.cant_miembros.data %2 == 0 :
            flash('La cantidad maxima de miembros debe ser impar','error')
            return render_template('proyecto/editarproyecto.html', form=form) 
        try:
            form.populate_obj(proyecto)
            proyecto.fecha_ultima_mod = today
            if form.estado.data == 'Nuevo' :
                proyecto.estado = 'N'
            elif form.estado.data == 'En Progreso' :
                proyecto.estado = 'P'
            elif form.estado.data == 'Anulado' :
                proyecto.estado = 'A'
            elif form.estado.data == 'Finalizado' :
                proyecto.estado = 'F'
            db_session.merge(proyecto)
            db_session.commit()
            
#            miembrosComite = db_session.query(MiembrosComite).filter_by(id_usuario=mc).filter_by(id_proyecto=proyecto.id).first()  
#            init_db(db_session)
#            db_session.delete(miembrosComite)
#            db_session.commit()
#        
            miembro = MiembrosComite(proyecto.id, proyecto.id_usuario_lider)
            db_session.add(miembro)
            db_session.commit()
            
            return redirect('/proyecto/administrarproyecto')
        except DatabaseError, e:
            flash('Error en la Base de Datos' + e.args[0],'error')
            return render_template('proyecto/editarproyecto.html', form=form)
    else:
        flash_errors(form)
    return render_template('proyecto/editarproyecto.html', form=form)

@app.route('/proyecto/eliminarproyecto', methods=['GET', 'POST'])
def eliminarproyecto():
    try:
        nom = request.args.get('nom')
        init_db(db_session)
        proyecto = db_session.query(Proyecto).filter_by(nombre=nom).first()
        if proyecto.estado != 'N' :
            flash('No se puede eliminar el Proyecto','info')
            return render_template('proyecto/administrarproyecto.html')
        init_db(db_session)
        db_session.delete(proyecto)
        db_session.commit()
        return redirect('/proyecto/administrarproyecto')
    except DatabaseError, e:
            flash('Error en la Base de Datos' + e.args[0],'info')
            return render_template('proyecto/administrarproyecto.html')
    
@app.route('/proyecto/buscarproyecto', methods=['GET', 'POST'])
def buscarproyecto():
    valor = request.args['patron']
    parametro = request.args['parametro']
    init_db(db_session)
    if valor == "" : 
        administrarproyecto()
    if parametro == 'cant_miembros' or parametro == 'id_usuario_lider':
        p = db_session.query(Proyecto).from_statement("SELECT * FROM proyecto where to_char("+parametro+", '99999') ilike '%"+valor+"%'").all()
    elif parametro == 'fecha_inicio' or parametro == 'fecha_fin':
        p = db_session.query(Proyecto).from_statement("SELECT * FROM proyecto where to_char("+parametro+", 'YYYY-mm-dd') ilike '%"+valor+"%'").all()
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

@app.route('/inicioproyecto')
def getProyectoByUsuario():
    usuario = request.args['id_usuario']
    p = db_session.query(Proyecto).join(Recurso, Proyecto.id == Recurso.id_proyecto).join(Permiso, Permiso.id_recurso == Recurso.id).join(RolPermiso, RolPermiso.id_permiso == Permiso.id).join(UsuarioRol, UsuarioRol.id_rol == RolPermiso.id_rol).filter(UsuarioRol.id_usuario == usuario)
    return render_template('proyecto/principal_proyecto.html', proyectos = p)

@app.route('/proyectoActual')
def proyectoActual():
    proyecto = request.args['pyo']
    session['pry'] = proyecto
    p = db_session.query(Proyecto).filter_by(id = proyecto).first()
    session['proyecto_nombre'] = p.nombre
    return redirect(url_for('index'))