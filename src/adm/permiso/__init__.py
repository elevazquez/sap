from loginC import app
from util.database import init_db, engine
import sqlalchemy
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import Flask, render_template, request, redirect, url_for, flash 
from adm.mod.Permiso import Permiso
from adm.mod.RolPermiso import RolPermiso
from adm.mod.Recurso import Recurso
from sqlalchemy.exc import DatabaseError
from adm.permiso.PermisoFormulario import PermisoFormulario
import flask, flask.views
from UserPermission import UserPermission, UserRol
from flask_login import current_user
import os

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
class PermisoControlador(flask.views.MethodView):
    def get(self):
        return flask.render_template('permiso.html')

def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ),'error')

@app.route('/permiso/nuevopermiso', methods=['GET', 'POST'])
def nuevopermiso():
    """ Funcion para agregar registros a la tabla Permiso""" 
    if not current_user.is_authenticated():
        flash('Debe loguearse primeramente!!!!', 'loggin')
        return render_template('index.html')
    
    permission = UserRol('ADMINISTRADOR')
    if permission.can():
        form = PermisoFormulario(request.form)
        form.id_recurso.choices= [(r.id, r.nombre) for r in db_session.query(Recurso).order_by(Recurso.nombre)]
        if request.method == 'POST' and form.validate():
            try:
                permiso = Permiso(form.codigo.data, form.descripcion.data, form.id_recurso.data)
                db_session.add(permiso)
                db_session.commit()
                flash('El permiso ha sido registrado con exito','info')
                return redirect('/permiso/administrarpermiso')
            except DatabaseError, e:
                if e.args[0].find('duplicate key value violates unique') != -1:
                    flash('Clave unica violada por favor ingrese otra combinacion de permiso con recurso unica' , 'error')
                else:
                    flash('Error en la Base de Datos' + e.args[0], 'error')
                return render_template('permiso/nuevopermiso.html', form=form)
        return render_template('permiso/nuevopermiso.html', form=form)
    else:
        flash('Sin permisos para agregar permisos', 'permiso')
        return render_template('index.html')

@app.route('/permiso/editarpermiso', methods=['GET', 'POST'])
def editarpermiso():
    """ Funcion para editar registros a la tabla Permiso"""
    if not current_user.is_authenticated():
        flash('Debe loguearse primeramente!!!!', 'loggin')
        return render_template('index.html')

    permission = UserRol('ADMINISTRADOR')
    if permission.can():
        p = db_session.query(Permiso).filter_by(codigo=request.args.get('codigo')).first()
        form = PermisoFormulario(request.form,p)
        permiso = db_session.query(Permiso).filter_by(codigo=form.codigo.data).first()
        if request.method == 'POST':
            if form.validate():
                form.populate_obj(permiso)
                db_session.merge(permiso)
                db_session.commit()
                flash('El permiso ha sido modificado con exito','info')
                return redirect('/permiso/administrarpermiso')
            else:
                flash_errors(form)
        else:
            flash_errors(form)
        return render_template('permiso/editarpermiso.html', form=form)
    else:
        flash('Sin permisos para modificar permisos', 'permiso')
        return render_template('index.html')
    
@app.route('/permiso/eliminarpermiso', methods=['GET', 'POST'])
def eliminarpermiso():
    """ Funcion para eliminar registros a la tabla Permiso"""
    if not current_user.is_authenticated():
        flash('Debe loguearse primeramente!!!!', 'loggin')
        return render_template('index.html')
    
    permission = UserRol('ADMINISTRADOR')
    if permission.can():
        cod = request.args.get('codigo')
        rol = db_session.query(Permiso).filter_by(codigo=cod).first()
        db_session.delete(rol)
        db_session.commit()
        flash('El permiso ha sido eliminado con exito','info')
        return redirect('/permiso/administrarpermiso')
    else:
        flash('Sin permisos para eliminar permisos', 'permiso')
        return render_template('index.html')

@app.route('/permiso/buscarpermiso', methods=['GET', 'POST'])
def buscarpermiso():
    """ Funcion para buscar registros en la tabla Permiso"""
    if not current_user.is_authenticated():
        flash('Debe loguearse primeramente!!!!', 'loggin')
        return render_template('index.html')
    
    permission = UserRol('ADMINISTRADOR')
    if permission.can():
        valor = request.args['patron']
        parametro = request.args['parametro']
        idrol =request.form.get('rol')
        #init_db(db_session)
        if valor=='' or valor == None:
            return administrarpermiso()
        else:
            if parametro == 'id_recurso':
                p = db_session.query(Permiso).from_statement("SELECT * FROM permiso where to_char("+parametro+", '99999') ilike '%"+valor+"%'").all()
                #p = db_session.query(Permiso).from_statement("SELECT * FROM permiso where "+parametro+" = CAST("+valor+" AS Int)").all()
            else:
                p = db_session.query(Permiso).from_statement("SELECT * FROM permiso where "+parametro+" ilike '%"+valor+"%'").all()
                #p = db_session.query(Permiso).filter(Permiso.codigo.like('%'+valor+'%'))
        if idrol != '' and idrol != None:
            yourPermiso=getPermisosByRol(idrol)
            lista = []
            for per in yourPermiso:
                lista.append(per)
            return render_template('permiso/administrarpermiso.html', permisos = p, isAdministrar = False, idrol = idrol, asignados = lista)
        return render_template('permiso/administrarpermiso.html', permisos = p, isAdministrar = True)
    else:
        flash('Sin permisos para buscar permisos', 'permiso')
        return render_template('index.html')

@app.route('/permiso/administrarpermiso')
def administrarpermiso():
    """ Funcion para ver registros a la tabla Permiso"""
    if not current_user.is_authenticated():
        flash('Debe loguearse primeramente!!!!', 'loggin')
        return render_template('index.html')
    
    permission = UserRol('ADMINISTRADOR')
    if permission.can():
        isAdmin = request.args.get('value')
        rol = request.args.get('idrol')
        permisos = db_session.query(Permiso).order_by(Permiso.id)
        lista = []
        if not isAdmin :
            #=======================================================================
            # en esta lista se inserta los permisos que estan asignados a un rol
            #=======================================================================
            yourPermiso=getPermisosByRol(rol)
            for p in yourPermiso:
                lista.append(p)
        return render_template('permiso/administrarpermiso.html', permisos = permisos, isAdministrar = isAdmin, idrol = rol, asignados = lista)
    else:
        flash('Sin permisos para administrar proyectos', 'permiso')
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

def getPermisosByRol(idrol):
    """ Funcion obtener los permisos asociados a un rol
    @param idrol: id del rol del que se obtendra sus permisos
    @return: retorna una lista de permisos """
    yourPermisos = db_session.query(Permiso).join(RolPermiso, RolPermiso.id_permiso == Permiso.id).filter(RolPermiso.id_rol == idrol).all()
    return yourPermisos

