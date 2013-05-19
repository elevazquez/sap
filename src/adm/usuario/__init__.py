from loginC import app

from util.database import init_db, engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import DatabaseError
from flask import Flask, render_template, request, redirect, url_for, flash 
from adm.mod.Usuario import Usuario
from adm.usuario.UsuarioFormulario import UsuarioFormulario
import flask, flask.views
import os
import datetime
import md5
#import hashlib
    
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
class ProyControlador(flask.views.MethodView):
    def get(self):
        return flask.render_template('usuario.html')
    
def flash_errors(form):
    """Funcion que captura los errores de Formulario"""
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ),'error')

#    texto = md5.new()
#    variable = "hola"
#    texto.update(variable)
#    print texto.digest()
#    print texto.hexdigest()
#    print texto.hexdigest()
                
@app.route('/usuario/nuevousuario', methods=['GET', 'POST'])
def nuevousuario():
    """ Funcion para agregar registros a la tabla Usuario""" 
    """ Se obtiene la fecha actual para verificar la fecha de nacimiento """
    today = datetime.date.today()
    form = UsuarioFormulario(request.form)
    """ Se un objeto md5 para encriptar la contrasenha del usuario """    
    con = md5.new()    
    if request.method == 'POST' and form.validate():
        #init_db(db_session)
        if form.fecha_nac.data > today :
            flash('Ingrese una fecha de nacimiento valida','error')
            return render_template('usuario/nuevousuario.html', form=form)  
        if form.password.data != form.confirmar.data :
            flash('Las contrasenhas deben coincidir','error')
            return render_template('usuario/nuevousuario.html', form=form)  
        try:
            con.update(form.password.data)
            usu = Usuario(form.usuario.data,  
                    form.nombre.data, form.apellido.data, con.hexdigest(), 
                    form.correo.data, form.domicilio.data, 
                    form.telefono.data, form.fecha_nac.data)
            db_session.add(usu)
            db_session.commit()
            flash('El Usuario ha sido registrado con exito ','info')
            return redirect('/usuario/administrarusuario')
        except DatabaseError, e:
            if e.args[0].find('duplicate key value violates unique')!=-1:
                flash('Clave unica violada por favor ingrese otro USUARIO para el registro' ,'error')
            else:
                flash('Error en la Base de Datos' + e.args[0],'error')
            return render_template('usuario/nuevousuario.html', form=form)
    else:
        flash_errors(form) 
    return render_template('usuario/nuevousuario.html', form=form)

@app.route('/usuario/editarusuario', methods=['GET', 'POST'])
def editarusuario():
    """ Funcion para editar registros de la tabla Usuario""" 
    """ Se obtiene la fecha actual para almacenar la fecha de ultima actualizacion """
    today = datetime.date.today()
    """ Se un objeto md5 para encriptar la contrasenha del usuario """    
    con = md5.new()
    conf = md5.new()    
    #init_db(db_session)
    p = db_session.query(Usuario).filter_by(usuario=request.args.get('usu')).first()  
    form = UsuarioFormulario(request.form,p)
    usuario = db_session.query(Usuario).filter_by(usuario=form.usuario.data).first()  
    if request.method == 'POST' and form.validate():
        if form.fecha_nac.data > today :
            flash('Ingrese una fecha de nacimiento valida','error')
            return render_template('usuario/editarusuario.html', form=form)  
        if form.password.data != form.confirmar.data :
            conf.update(form.confirmar.data)
            confir = conf.hexdigest()
            if form.password.data != confir :
                flash('Las contrasenhas deben coincidir','error')
                return render_template('usuario/editarusuario.html', form=form)  
        try:
            con.update(form.password.data)
            form.populate_obj(usuario)
            usuario.password = con.hexdigest()
            db_session.merge(usuario)
            db_session.commit()
            return redirect('/usuario/administrarusuario')
        except DatabaseError, e:
            flash('Error en la Base de Datos' + e.args[0],'error')
            return render_template('usuario/editarusuario.html', form=form)
    else:
        flash_errors(form)
    return render_template('usuario/editarusuario.html', form=form)

@app.route('/usuario/eliminarusuario', methods=['GET', 'POST'])
def eliminarusuario():
    """ Funcion para eliminar registros de la tabla Usuario""" 
    try:
        usu = request.args.get('usu')
        #init_db(db_session)
        usuario = db_session.query(Usuario).filter_by(usuario=usu).first()  
        #init_db(db_session)
        db_session.delete(usuario)
        db_session.commit()
        return redirect('/usuario/administrarusuario')
    except DatabaseError, e:
            flash('Error en la Base de Datos' + e.args[0],'info')
            return render_template('usuario/administrarusuario.html')
    
@app.route('/usuario/buscarusuario', methods=['GET', 'POST'])
def buscarusuario():
    """ Funcion para buscar registros de la tabla Usuario""" 
    valor = request.args['patron']
    parametro = request.args['parametro']
    #init_db(db_session)
    if valor == "" : 
        administrarusuario()
    if parametro == 'fecha_nac':
        p = db_session.query(Usuario).from_statement("SELECT * FROM usuario where to_char("+parametro+", 'YYYY-mm-dd') ilike '%"+valor+"%'").all()
    else:
        p = db_session.query(Usuario).from_statement("SELECT * FROM usuario where "+parametro+" ilike '%"+valor+"%'").all()
    return render_template('usuario/administrarusuario.html', usuarios = p)   
    valor = request.args['patron']
    #init_db(db_session)
    r = db_session.query(Usuario).filter_by(usuario=valor)
    if r == None:
        return 'no existe concordancia'
    return render_template('usuario/administrarusuario.html', usuarios = r)

@app.route('/usuario/administrarusuario')
def administrarusuario():
    """ Funcion para listar registros de la tabla Usuario""" 
    #init_db(db_session)
    usuarios = db_session.query(Usuario).order_by(Usuario.nombre)
    return render_template('usuario/administrarusuario.html', usuarios = usuarios)

@app.errorhandler(404)
def page_not_found(error):
    """Lanza un mensaje de error en caso de que la pagina solicitada no exista"""
    return 'Esta Pagina no existe', 404

@app.after_request
def shutdown_session(response):
    """Cierra la sesion de la conexion con la base de datos"""
    db_session.remove()
    return response