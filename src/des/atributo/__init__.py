from loginC import app

from util.database import init_db, engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import DatabaseError
from flask import Flask, render_template, request, redirect, url_for, flash, session 
from des.mod.Atributo import Atributo
from flask_login import current_user
from des.mod.TipoAtributo import TipoAtributo
from des.atributo.AtributoFormulario import AtributoFormulario
from des.atributo.AtributoEdFormulario import AtributoEdFormulario
import flask, flask.views
import os
from UserPermission import UserPermission

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
class AtributoControlador(flask.views.MethodView):
    def get(self):
        return flask.render_template('atributo.html')
    
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ),'error')

@app.route('/atributo/nuevoatributo', methods=['GET', 'POST'])
def nuevoatributo():
    """ Funcion para agregar registros a la tabla ATributos"""
    if not current_user.is_authenticated():
        flash('Debe loguearse primeramente!!!!', 'loggin')
        return render_template('index.html')

    permission =UserPermission('LIDER PROYECTO',int(session['pry']))
    if permission.can()==False:
        flash('No posee los permisos suficientes para realizar la operacion', 'permiso')
        return render_template('index.html') 
    form = AtributoFormulario(request.form)
    form.id_tipo_atributo.choices= [(t.id, t.nombre) for t in db_session.query(TipoAtributo).order_by(TipoAtributo.nombre).all()]
    if request.method == 'POST' and form.validate():
        try: 
            att = Atributo(form.nombre.data, form.descripcion.data, form.id_tipo_atributo.data)
            db_session.add(att)
            db_session.commit()
            flash('El Atributo ha sido registrado con exito','info')
            return redirect('/atributo/administraratributo') 
        except DatabaseError, e:
            if e.args[0].find('duplicate key value violates unique')!=-1:
                flash('Clave unica violada por favor ingrese otro NOMBRE de Atributo' ,'error')
            else:
                flash('Error en la Base de Datos' + e.args[0],'error')
            return render_template('atributo/nuevoatributo.html', form=form)
    else:
        flash_errors(form) 
        return render_template('atributo/nuevoatributo.html', form=form)
 

@app.route('/atributo/editaratributo', methods=['GET', 'POST'])
def editaratributo():
    """funcion que sirve para modificar atributos"""
    if not current_user.is_authenticated():
        flash('Debe loguearse primeramente!!!!', 'loggin')
        return render_template('index.html')
    
    permission =UserPermission('LIDER PROYECTO', int(session['pry']))
    if permission.can()==False:
        flash('No posee los permisos suficientes para realizar la operacion', 'permiso')
        return render_template('index.html')
    a = db_session.query(Atributo).filter_by(nombre=request.args.get('nom')).first()  
    form = AtributoEdFormulario(request.form,a)
    tipo_selected= db_session.query(TipoAtributo).filter_by(nombre=request.args.get('tipo_atributo')).first() 
    atributo = db_session.query(Atributo).filter_by(nombre=form.nombre.data).first()  
    if request.method != 'POST':
        form.id_tipo_atributo.data= tipo_selected.nombre
    if request.method == 'POST' and form.validate():
        try:
            tipo=db_session.query(TipoAtributo).filter_by(nombre=form.id_tipo_atributo.data).first() 
            form.populate_obj(atributo)
            atributo.id_tipo_atributo = tipo.id
            db_session.merge(atributo)
            db_session.commit()
            flash('El atributo ha sido editado con exito','info')
            return redirect('/atributo/administraratributo')
        except DatabaseError, e:
            flash('Error en la Base de Datos' + e.args[0],'error')
            return render_template('atributo/editaratributo.html', form=form)
    else:
        flash_errors(form)
    return render_template('atributo/editaratributo.html', form=form)

@app.route('/atributo/eliminaratributo', methods=['GET', 'POST'])
def eliminaratributo():
    """funcion que elimina un atributo"""
    if not current_user.is_authenticated():
        flash('Debe loguearse primeramente!!!!', 'loggin')
        return render_template('index.html')
    
    permission =UserPermission('LIDER PROYECTO', int(session['pry']))
    if permission.can()==False:
        flash('No posee los permisos suficientes para realizar la operacion', 'permiso')
        return render_template('index.html') 
    try:
        cod = request.args.get('nom')
        atributo = db_session.query(Atributo).filter_by(nombre=cod).first()
        db_session.delete(atributo)
        db_session.commit()
        flash('El atributo ha sido eliminado con exito','info')
        return redirect('/atributo/administraratributo')
    except DatabaseError, e:
            flash('Error en la Base de Datos' + e.args[0],'error')
            return render_template('atributo/eliminaratributo.html')
    
@app.route('/atributo/buscaratributo', methods=['GET', 'POST'])
def buscaratributo():
    """funcion que permite buscar un atributos"""
    if not current_user.is_authenticated():
        flash('Debe loguearse primeramente!!!!', 'loggin')
        return render_template('index.html')

    permission =UserPermission('LIDER PROYECTO',int(session['pry']))
    if permission.can()==False:
        flash('No posee los permisos suficientes para realizar la operacion', 'permiso')
        return render_template('index.html')
    
    valor = request.args['patron']
    parametro = request.args['parametro']
    if valor == "" : 
        administraratributo()
    if parametro == 'id_tipo_atributo':
        p = db_session.query(Atributo).from_statement("SELECT a.* FROM atributo a , tipo_atributo ta where ta.nombre  ilike '%"+valor+"%' and a.id_tipo_atributo= ta.id").all()
    else:
        p = db_session.query(Atributo).from_statement("SELECT * FROM atributo where "+parametro+" ilike '%"+valor+"%'").all()
    return render_template('atributo/administraratributo.html', atributos = p)

@app.route('/atributo/administraratributo')
def administraratributo():
    """funcion que lista todos los atributos"""
    if not current_user.is_authenticated():
        flash('Debe loguearse primeramente!!!!', 'loggin')
        return render_template('index.html')
    
    permission =UserPermission('LIDER PROYECTO', int(session['pry']))
    if permission.can()==False:
        flash('No posee los permisos suficientes para realizar la operacion', 'permiso')
        return render_template('index.html') 
    atributos = db_session.query(Atributo).order_by(Atributo.nombre)
    return render_template('atributo/administraratributo.html', atributos = atributos)

@app.errorhandler(404)
def page_not_found(error):
    """Lanza un mensaje de error en caso de que la pagina solicitada no exista"""
    return 'Esta Pagina no existe', 404

@app.after_request
def shutdown_session(response):
    """Cierra la sesion de la conexion con la base de datos"""
    db_session.remove()
    return response