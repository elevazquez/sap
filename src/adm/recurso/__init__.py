from loginC import app

from util.database import init_db, engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import DatabaseError
from flask import Flask, render_template, request, redirect, url_for, flash 
from des.mod.Fase import Fase
from adm.mod.Proyecto import Proyecto
from adm.mod.Recurso import Recurso
from adm.mod.Permiso import Permiso
from adm.recurso.RecursoFormulario import RecursoFormulario
from UserPermission import UserRol

import flask, flask.views
import os

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
class AtributoControlador(flask.views.MethodView):
    def get(self):
        return flask.render_template('recurso.html')
    
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ),'error')

@app.route('/recurso/seleccionrecurso', methods=['GET', 'POST'])
def seleccionrecurso():
    """ Funcion para seleccionar tipo de recurso a crear""" 
    permission = UserRol('ADMINISTRADOR')
    if permission.can():
        parametro = request.args['parametro']
        lista = []
        if parametro == 'fase' :
            lista = db_session.query(Fase).filter(~Fase.id.in_(db_session.query(Recurso.id_fase).from_statement('SELECT recurso.id_fase '+
                                                                                                                              'from recurso '+
                                                                                                                              'where recurso.id_fase is not null'))).all()
        elif parametro == 'proyecto' :
            lista = db_session.query(Proyecto).filter(~Proyecto.id.in_(db_session.query(Recurso.id_proyecto).from_statement('SELECT recurso.id_proyecto '+
                                                                                                                              'from recurso '+
                                                                                                                              'where recurso.id_proyecto is not null'))).all()
        else:
            parametro= None    
        return render_template('recurso/seleccionrecurso.html',lista = lista, param= parametro)
    else:
        flash('Sin permisos para seleccionar recursos', 'permiso')
        return render_template('index.html')
    
@app.route('/recurso/nuevorecurso', methods=['GET', 'POST'])
def nuevorecurso():
    """ Funcion para agregar registros a la tabla recursos""" 
    permission = UserRol('ADMINISTRADOR')
    if permission.can():
        form = RecursoFormulario(request.form)
        if  request.args.get('id_recurso') == None:
            id_recurso= request.form.get('id')
        else:
            id_recurso= request.args.get('id_recurso')
            
        if  request.args.get('recursoTipo') == None:
            parametro= request.form.get('param')
        else:
            parametro= request.args.get('recursoTipo')
             
        if  request.method != 'POST' :
            id_recurso= request.args.get('id_recurso')
            parametro= request.args.get('recursoTipo')
            lista=None
            if parametro == 'fase' :
                lista = db_session.query(Fase).filter_by(id= id_recurso).first()
                form.id_fase.data= lista.id
                form.recurso.data = lista.nombre
            elif parametro == 'proyecto' :
                lista = db_session.query(Proyecto).filter_by(id= id_recurso).first()
                form.id_proyecto.data= lista.id
                form.recurso.data= lista.nombre   
           
        if request.method == 'POST' and form.validate():
            try: 
                if form.id_proyecto.data == 'None':
                    form.id_proyecto.data = None
                else :
                    form.id_proyecto.data = int(form.id_proyecto.data)
                
                if form.id_fase.data == 'None':
                    form.id_fase.data = None
                else :
                    form.id_fase.data = int(form.id_fase.data)
                
                rec = Recurso(form.nombre.data, form.id_proyecto.data, form.id_fase.data )
                db_session.add(rec)
                db_session.commit()
                flash('El Recurso ha sido registrado con exito','info')
                return redirect('/recurso/administrarrecurso') 
            except DatabaseError, e:
                flash('Error en la Base de Datos' + e.args[0],'error')
                return render_template('recurso/nuevorecurso.html', form=form)
        else:
            flash_errors(form) 
            return render_template('recurso/nuevorecurso.html', form=form)
    else:
        flash('Sin permisos para agregar recursos', 'permiso')
        return render_template('index.html')
 
@app.route('/recurso/eliminarrecurso', methods=['GET', 'POST'])
def eliminarrecurso():
    """funcion que elimina un recurso
    @param id_recurso: indica el id del recurso a eliminar.
    @return: retorna a la pagina de administrar recurso.
    @bug: Error de base de datos al tratar de eliminar el recurso.
    @precondition: No debe existir permisos con el recurso para que se elimine con exito.
    @attention: Requiere que se tenga el rol de administrador para realizar la opcion."""
    permission = UserRol('ADMINISTRADOR')
    if permission.can():
        try:
            print request.args.get('id_recurso')
            if request.args.get('id_recurso') != None:
                r = db_session.query(Recurso).filter_by(id=request.args.get('id_recurso')).first()
                form = RecursoFormulario(request.form, r)
                if r.id_fase != None :
                    form.id_fase.data = r.recursofase.nombre
                    form.id_proyecto.data = None
                else:
                    form.id_fase.data = None
                    form.id_proyecto.data = r.recursoproyecto.nombre
            else :
                form = RecursoFormulario(request.form)
            if request.method == 'POST':
                permiso = db_session.query(Permiso).filter_by(id_recurso= form.id.data).first()
                if permiso != None :
                    flash('No se ha podido Eliminar, existe permisos que utiliza el recurso','info')
                    return redirect('/recurso/administrarrecurso')     
    
                recurso = db_session.query(Recurso).filter_by(id= form.id.data).first()
                db_session.delete(recurso)
                db_session.commit()
                flash('El recurso ha sido eliminado con exito','info')
                return redirect('/recurso/administrarrecurso')
            return render_template('recurso/eliminarrecurso.html', form=form)
        except DatabaseError, e:
            flash('Error en la Base de Datos' + e.args[0],'error')
            return render_template('recurso/eliminarrecurso.html', form= form)
    else:
        flash('Sin permisos para eliminar recursos', 'permiso')
        return render_template('index.html')
    
@app.route('/recurso/buscarrecurso', methods=['GET', 'POST'])
def buscarrecurso():
    """funcion que permite buscar un recurso"""
    permission = UserRol('ADMINISTRADOR')
    if permission.can():
        valor = request.args['patron']
        parametro = request.args['parametro']
        if valor == "" : 
            administrarrecurso()
            
        p = db_session.query(Recurso).from_statement("SELECT * FROM recurso where "+parametro+" ilike '%"+valor+"%'").all()
        return render_template('recurso/administrarrecurso.html', recursos = p)
    else:
        flash('Sin permisos para buscar recursos', 'permiso')
        return render_template('index.html')

@app.route('/recurso/administrarrecurso')
def administrarrecurso():
    """funcion que lista todos los recursos"""
    permission = UserRol('ADMINISTRADOR')
    if permission.can():
        recursos = db_session.query(Recurso).order_by(Recurso.nombre)
        return render_template('recurso/administrarrecurso.html', recursos = recursos)
    else:
        flash('Sin permisos para administrar recursos', 'permiso')
        return render_template('index.html')

@app.errorhandler(404)
def page_not_found(error):
    """Lanza un mensaje de error en caso de que la pagina solicitada no exista"""
    return 'Esta Pagina no existe', 404

@app.after_request
def shutdown_session(response):
    """Cierra la sesion de la conexion con la base de datos"""
    db_session.remove()
    return response