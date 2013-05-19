from loginC import app

from util.database import init_db, engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import DatabaseError
from flask import Flask, render_template, request, redirect, url_for, flash 
from des.mod.Atributo import Atributo
from des.mod.TipoAtributo import TipoAtributo
from des.atributo.AtributoFormulario import AtributoFormulario
from des.atributo.AtributoEdFormulario import AtributoEdFormulario
import flask, flask.views
import os

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
        form = AtributoFormulario(request.form)
        init_db(db_session)
        form.id_tipo_atributo.choices= [(t.id, t.nombre) for t in db_session.query(TipoAtributo).order_by(TipoAtributo.nombre).all()]
        if request.method == 'POST' and form.validate():
            init_db(db_session)
            try: 
                att = Atributo(form.nombre.data, form.descripcion.data, form.id_tipo_atributo.data)
                db_session.add(att)
                db_session.commit()
                flash('El Atributo ha sido registrado con exito','info')
                return redirect('/atributo/administraratributo') 
            except DatabaseError, e:
                flash('Error en la Base de Datos' + e.args[0],'error')
                return render_template('usuario/nuevousuario.html', form=form)
        else:
            flash_errors(form) 
            return render_template('atributo/nuevoatributo.html', form=form)
 

@app.route('/atributo/editaratributo', methods=['GET', 'POST'])
def editaratributo():
    """funcion que sirve para modificar atributos"""
    init_db(db_session)
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
    try:
        cod = request.args.get('nom')
        init_db(db_session)
        atributo = db_session.query(Atributo).filter_by(nombre=cod).first()
        init_db(db_session)
        db_session.delete(atributo)
        db_session.commit()
        return redirect('/atributo/administraratributo')
    except DatabaseError, e:
            flash('Error en la Base de Datos' + e.args[0],'error')
            return render_template('atributo/eliminaratributo.html')
    
@app.route('/atributo/buscaratributo', methods=['GET', 'POST'])
def buscaratributo():
    """funcion que permite buscar un atributos"""
    valor = request.args['patron']
    parametro = request.args['parametro']
    init_db(db_session)
    if valor == "" : 
        administraratributo()
    if parametro == 'id_tipo_atributo':
        p = db_session.query(Atributo).from_statement("SELECT a.* FROM atributo a , tipo_atributo ta where ta.nombre  ilike '%"+valor+"%' and a.id_tipo_atributo= ta.id").all()
    else:
        p = db_session.query(Atributo).from_statement("SELECT * FROM atributo where "+parametro+" ilike '%"+valor+"%'").all()
    return render_template('atributo/administraratributo.html', atributos = p)
    
    
    valor = request.args['patron']
    init_db(db_session)
    r = db_session.query(Atributo).filter_by(nombre=valor)
    if r == None:
        return 'No existe concordancia'
    return render_template('atributo/administraratributo.html', atributos = r)

@app.route('/atributo/administraratributo')
def administraratributo():
    """funcion que lista todos los atributos"""
    init_db(db_session)
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