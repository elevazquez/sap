from loginC import app

from util.database import init_db, engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import DatabaseError
from flask import Flask, render_template, request, redirect, url_for, flash, session 
from adm.mod.Proyecto import Proyecto
from adm.mod.Usuario import Usuario
from adm.mod.Recurso import Recurso
from adm.mod.Permiso import Permiso
from adm.mod.Rol import Rol
from adm.mod.RolPermiso import RolPermiso
from adm.mod.UsuarioRol import UsuarioRol
from UserPermission import UserPermission
from flask_login import current_user

from adm.mod.MiembrosComite import MiembrosComite
from adm.miembrosComite.MiembrosComiteFormulario import MiembrosComiteFormulario
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
    """ Funcion para capturar los errores de Formulario""" 
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ),'error')

@app.route('/miembrosComite/nuevomiembrosComite', methods=['GET', 'POST'])
def nuevomiembrosComite():
    """ Funcion para agregar registros a la tabla MiembrosComite"""
    if not current_user.is_authenticated():
        flash('Debe loguearse primeramente!!!!', 'loggin')
        return render_template('index.html')
    
    permission =UserPermission('LIDER PROYECTO', int(session['pry']))
    if permission.can()==False:
        flash('No posee los permisos suficientes para realizar la operacion', 'permiso')
        return render_template('index.html')
    pro = db_session.query(Proyecto).filter_by(id=session['pry']).first()
    u = db_session.query(Usuario).filter_by(usuario=request.args.get('usu')).first()  
    form = MiembrosComiteFormulario(request.form,u)
    usuario = db_session.query(Usuario).filter_by(usuario=form.usuario.data).first()
    cant = db_session.query(MiembrosComite).filter_by(id_proyecto=pro.id).count()
    r = db_session.query(Rol).filter_by(codigo='COMITE CAMBIOS').first()  
    if pro.estado != 'N' :
        flash('No se pueden asignar Miembros al Comite de Cambios','info')
        return render_template('miembrosComite/administrarmiembrosComite.html')
    if cant == pro.cant_miembros :
        flash('No se pueden asignar Miembros al Comite de Cambios, numero maximo de miembros alcanzado','info')
        return render_template('miembrosComite/administrarmiembrosComite.html')  
    if request.method == 'POST' and form.validate():
        try:
            miembrosComite = MiembrosComite(pro.id, usuario.id)
            db_session.add(miembrosComite)
            db_session.commit()
            ur = UsuarioRol(r.id, usuario.id, pro.id)
            db_session.add(ur)
            db_session.commit()
            flash('Se ha asignado el usuario al Comite de Cambios','info')
            return redirect('/miembrosComite/administrarmiembrosComite')
        except DatabaseError, e:
            if e.args[0].find('duplicate key value violates unique')!=-1:
                flash('Clave unica violada por favor ingrese otro usuario' ,'error')
            else:
                flash('Error en la Base de Datos' + e.args[0],'error')
            return render_template('miembrosComite/nuevomiembrosComite.html', form=form)
    else:
        flash_errors(form)  
    return render_template('miembrosComite/nuevomiembrosComite.html', form=form)

@app.route('/miembrosComite/eliminarmiembrosComite', methods=['GET', 'POST'])
def eliminarmiembrosComite():
    """ Funcion para eliminar registros de la tabla MiembrosComite""" 
    if not current_user.is_authenticated():
        flash('Debe loguearse primeramente!!!!', 'loggin')
        return render_template('index.html')
    
    permission =UserPermission('LIDER PROYECTO', int(session['pry']))
    if permission.can()==False:
        flash('No posee los permisos suficientes para realizar la operacion', 'permiso')
        return render_template('index.html')
    
    r = db_session.query(Rol).filter_by(codigo='COMITE CAMBIOS').first()  
    pro = db_session.query(Proyecto).filter_by(id=session['pry']).first()
    if pro.estado != 'N' :
        flash('No se pueden desasignar Miembros al Comites de Cambios','info')
        return render_template('miembrosComite/administrarmiembrosComite.html')
    if pro.id_usuario_lider.__repr__() == request.args.get('usu'):
        flash('No se pueden desasignar al Lider de Proyecto del Comite de Cambios','info')
        return render_template('miembrosComite/administrarmiembrosComite.html')   
    try:
        print request.args.get('id_mc')
        mc = db_session.query(MiembrosComite).filter_by(id=request.args.get('id_mc')).first()  
        ur = db_session.query(UsuarioRol).filter_by(id_rol=r.id).filter_by(id_usuario=mc.id_usuario).filter_by(id_proyecto=pro.id).first()  
        db_session.delete(ur)
        db_session.commit()
        
        miembrosComite = db_session.query(MiembrosComite).filter_by(id=request.args.get('id_mc')).first()  
        db_session.delete(miembrosComite)
        db_session.commit()
        flash('El Miembro ha sido eliminado con exito','info')
        return redirect('/miembrosComite/administrarmiembrosComite')
    except DatabaseError, e:
            flash('Error en la Base de Datos' + e.args[0],'info')
            return render_template('/miembrosComite/administrarmiembrosComite.html')
    
@app.route('/miembrosComite/buscarmiembrosComite', methods=['GET', 'POST'])
def buscarmiembrosComite():
    """ Funcion para buscar registros en la tabla MiembrosComite"""
    if not current_user.is_authenticated():
        flash('Debe loguearse primeramente!!!!', 'loggin')
        return render_template('index.html')
    
    permission =UserPermission('LIDER PROYECTO', int(session['pry']))
    if permission.can()==False:
        flash('No posee los permisos suficientes para realizar la operacion', 'permiso')
        return render_template('index.html')
    
    valor = request.args['patron']
    parametro = request.args['parametro']
    if valor == "" : 
        p = db_session.query(MiembrosComite).filter_by(id_proyecto=session['pry'])
    else :
        p = db_session.query(MiembrosComite).from_statement("SELECT * FROM miembros_comite where id_usuario in (SELECT id FROM usuario where "+parametro+" ilike '%"+valor+"%') and id_proyecto='"+session['pry']+"'").all() 
    return render_template('miembrosComite/administrarmiembrosComite.html', miembrosComites = p)

@app.route('/miembrosComite/buscarmiembrosComite2', methods=['GET', 'POST'])
def buscarmiembrosComite2():
    """ Funcion para buscar registros en la tabla MiembrosComite""" 
    if not current_user.is_authenticated():
        flash('Debe loguearse primeramente!!!!', 'loggin')
        return render_template('index.html')
    
    permission =UserPermission('LIDER PROYECTO', int(session['pry']))
    if permission.can()==False:
        flash('No posee los permisos suficientes para realizar la operacion', 'permiso')
        return render_template('index.html')
    
    valor = request.args['patron']
    parametro = request.args['parametro']
    if valor == "" : 
        p = db_session.query(Usuario).from_statement("select * from usuario where id not in (select id_usuario from miembros_comite where id_proyecto='"+session['pry']+"')").all()
    else :
        p = db_session.query(Usuario).from_statement("select * from usuario where "+parametro+" ilike '%"+valor+"%' and id not in (select id_usuario from miembros_comite where id_proyecto='"+session['pry']+"')").all() 
    return render_template('miembrosComite/listarusuarios.html', usuarios = p)

@app.route('/miembrosComite/administrarmiembrosComite')
def administrarmiembrosComite():
    """ Funcion para listar registros de la tabla MiembrosComite
    @precondition: El usuario debe haber seleccionado el proyecto que administrara
    @author: Lila Pamela Perez Miranda""" 
    if not current_user.is_authenticated():
        flash('Debe loguearse primeramente!!!!', 'loggin')
        return render_template('index.html')
    
    permission =UserPermission('LIDER PROYECTO', int(session['pry']))
    if permission.can():
        miembrosComites = db_session.query(MiembrosComite).filter_by(id_proyecto=session['pry']).order_by(MiembrosComite.id_usuario)
        return render_template('miembrosComite/administrarmiembrosComite.html', miembrosComites = miembrosComites)
    else:
        flash('Sin permisos para administrar miembros Comite', 'permiso')
        return render_template('index.html')

@app.route('/miembrosComite/listarusuarios')
def listarusuarios():
    """ Funcion para listar registros de la tabla Usuarios""" 
    if not current_user.is_authenticated():
        flash('Debe loguearse primeramente!!!!', 'loggin')
        return render_template('index.html')
    
    permission =UserPermission('LIDER PROYECTO', int(session['pry']))
    if permission.can():
        usuarios = db_session.query(Usuario).from_statement("select * from usuario where id not in (select id_usuario from miembros_comite where id_proyecto='"+session['pry']+"')").all()
        return render_template('miembrosComite/listarusuarios.html', usuarios = usuarios)
    else:
        flash('No posee los permisos suficientes para realizar la operacion', 'permiso')
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