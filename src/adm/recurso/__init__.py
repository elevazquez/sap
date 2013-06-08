
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
    
    parametro = request.args['parametro']
    list =[]
    if parametro == 'fase' :
        list = db_session.query(Fase).all()
    elif parametro == 'proyecto' :
        list = db_session.query(Proyecto).all()
    else:
        parametro= None    
        
    return render_template('recurso/seleccionrecurso.html',lista = list, param= parametro)
    
    
@app.route('/recurso/nuevorecurso', methods=['GET', 'POST'])
def nuevorecurso():
        """ Funcion para agregar registros a la tabla recursos""" 
        form = RecursoFormulario(request.form)
        #init_db(db_session)
        
        if  request.args.get('id_recurso') == None:
            id_recurso= request.form.get('id_recurso')
        else:
            id_recurso= request.args.get('id_recurso')
            
        if  request.args.get('recursoTipo') == None:
            parametro= request.form.get('param')
        else:
            parametro= request.args.get('recursoTipo')
            
        
             
        if  request.method != 'POST' :
            id_recurso= request.args.get('id_recurso')
            parametro= request.args.get('recursoTipo')
            if parametro == 'fase' :
                list = db_session.query(Fase).filter_by(id= id_recurso).first()
                form.id_fase.data= list.id
                form.recurso.data = list.nombre
            elif parametro == 'proyecto' :
                list = db_session.query(Proyecto).filter_by(id= id_recurso).first()
                form.id_proyecto.data= list.id
                form.recurso.data= list.nombre   
           
        if request.method == 'POST' and form.validate():
            #init_db(db_session)
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
                #else:
                #    rec = Recurso(form.nombre.data, form.id_proyecto.data,   None ) 
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
 


@app.route('/recurso/eliminarrecurso', methods=['GET', 'POST'])
def eliminarrecurso():
    """funcion que elimina un recurso"""
    try:
        id_rec = request.args.get('id_recurso')
        #init_db(db_session)
        permiso = db_session.query(Permiso).filter_by(id_recurso= id_rec).first()
        if permiso != None :
            flash('No se ha podido Eliminar..','info')
            return redirect('/recurso/administrarrecurso')     
    
        recurso = db_session.query(Recurso).filter_by(id= id_rec).first()
        #init_db(db_session)
        db_session.delete(recurso)
        db_session.commit()
        return redirect('/recurso/administrarrecurso')
    except DatabaseError, e:
            flash('Error en la Base de Datos' + e.args[0],'error')
            return render_template('recurso/eliminarrecurso.html')
    
@app.route('/recurso/buscarrecurso', methods=['GET', 'POST'])
def buscarrecurso():
    """funcion que permite buscar un recurso"""
    valor = request.args['patron']
    parametro = request.args['parametro']
    #init_db(db_session)
    if valor == "" : 
        administrarrecurso()
    p = db_session.query(Recurso).from_statement("SELECT * FROM recurso where "+parametro+" ilike '%"+valor+"%'").all()
    return render_template('recurso/administrarrecurso.html', recursos = p)    
    
    valor = request.args['patron']
    #init_db(db_session)
    r = db_session.query(Recurso).filter_by(nombre=valor)
    if r == None:
        return 'No existe concordancia'
    return render_template('recurso/administrarrecurso.html', recursos = r)


@app.route('/recurso/administrarrecurso')
def administrarrecurso():
    """funcion que lista todos los recursos"""
    #init_db(db_session)
    recursos = db_session.query(Recurso).order_by(Recurso.nombre)
    return render_template('recurso/administrarrecurso.html', recursos = recursos)


@app.errorhandler(404)
def page_not_found(error):
    """Lanza un mensaje de error en caso de que la pagina solicitada no exista"""
    return 'Esta Pagina no existe', 404


@app.after_request
def shutdown_session(response):
    """Cierra la sesion de la conexion con la base de datos"""
    db_session.remove()
    return response

