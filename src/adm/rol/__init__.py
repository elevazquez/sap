from loginC import app
from util.database import init_db, engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import DatabaseError
from flask import Flask, render_template, request, redirect, url_for, flash 
from adm.mod.Rol import Rol
from adm.permiso import administrarpermiso
from adm.rol.RolFormulario import RolFormulario
from adm.mod.RolPermiso import RolPermiso
from adm.permiso import getPermisosByRol
from UserPermission import UserPermission, UserRol
import flask, flask.views
import os

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
class RolControlador(flask.views.MethodView):
    def get(self):
        return flask.render_template('rol.html')
    
def flash_errors(form):
    """Funcion para capturar los errores del Formulario"""
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ),'error')                

@app.route('/add', methods=['GET', 'POST'])
def add():
    """ Funcion para agregar registros a la tabla Rol"""
    permission = UserRol('ADMINISTRADOR')
    if permission.can():
        form = RolFormulario(request.form)
        if request.method == 'POST' and form.validate():
            #init_db(db_session)
            try:
                rol = Rol(form.codigo.data, form.descripcion.data)
                db_session.add(rol)
                db_session.commit()
                flash('El rol ha sido registrado con exito','info')
                return redirect('/administrarrol') #/listarol
            except DatabaseError, e:
                if e.args[0].find('duplicate key value violates unique')!=-1:
                    flash('Clave unica violada por favor ingrese otro CODIGO de Rol' ,'error')
                else:
                    flash('Error en la Base de Datos' + e.args[0],'error')
                return render_template('rol/nuevorol.html', form=form)
        else:
            flash_errors(form) 
        return render_template('rol/nuevorol.html', form=form)
    else:
        return 'sin permisos'

@app.route('/editar', methods=['GET', 'POST'])
def editar():
    """ Funcion para editar registros de la tabla Rol""" 
    #init_db(db_session)
    r = db_session.query(Rol).filter_by(codigo=request.args.get('cod')).first()  
    form = RolFormulario(request.form,r)
    rol = db_session.query(Rol).filter_by(codigo=form.codigo.data).first()  
    if request.method == 'POST' and form.validate():
        try:
            form.populate_obj(rol)
            db_session.merge(rol)
            db_session.commit()
            return redirect('/administrarrol')
        except DatabaseError, e:
            flash('Error en la Base de Datos' + e.args[0],'error')
            return render_template('rol/editarrol.html', form=form)
    else:
        flash_errors(form)
    return render_template('rol/editarrol.html', form=form)

@app.route('/eliminar', methods=['GET', 'POST'])
def eliminar():
    """ Funcion para eliminar registros de la tabla Rol""" 
    try:
        cod = request.args.get('cod')
        #init_db(db_session)
        rol = db_session.query(Rol).filter_by(codigo=cod).first()  
        #init_db(db_session)
        db_session.delete(rol)
        db_session.commit()
        return redirect('/administrarrol')
    except DatabaseError, e:
            flash('Error en la Base de Datos' + e.args[0],'info')
            return render_template('rol/administrarrol.html')

@app.route('/buscar', methods=['GET', 'POST'])
def buscar():
    """ Funcion para buscar registros de la tabla Rol""" 
    valor = request.args['patron']
    parametro = request.args['parametro']
    #init_db(db_session)
    if valor == "" : 
        administrarrol()
    p = db_session.query(Rol).from_statement("SELECT * FROM rol where "+parametro+" ilike '%"+valor+"%'").all()
    return render_template('rol/administrarrol.html', roles = p)
    valor = request.args['patron']
    #init_db(db_session)
    r = db_session.query(Rol).filter_by(codigo=valor)
    if r == None:
        return 'no existe concordancia'
    return render_template('rol/administrarrol.html', roles = r)

@app.route('/administrarrol', methods=['GET', 'POST'])
def administrarrol():
    """ Funcion para listar registros de la tabla Rol""" 
    #init_db(db_session)
    roles = db_session.query(Rol).order_by(Rol.codigo)
    return render_template('rol/administrarrol.html', roles = roles)

@app.route('/rol/asignarpermiso', methods=['GET', 'POST'])
def asignarpermiso():
    """ Funcion para asignar Permisos a cada Rol""" 
    idrol = request.args.get('idrol')
    if request.method == 'POST':
        rol = request.form.get('idrol')
        permisos=request.form.getlist('permisos')
        ps= getPermisosByRol(rol)
        for per in ps:
            #===================================================================
            # Elimina los permisos de los roles que ya no se encuentran seleccionados
            #===================================================================
            if not (permisos.count(per.id) > 0) :
                rp= db_session.query(RolPermiso).filter_by(id_rol=rol, id_permiso=per.id).first()
                db_session.delete(rp)
                db_session.commit()
        #=======================================================================
        # Inserta los roles permisos seleccionados, si no existe realiza el merge y confirma los cambios
        #=======================================================================
        for p in permisos :
            rolper = RolPermiso(rol, p)
            exits = db_session.query(RolPermiso).filter_by(id_rol=rol, id_permiso=p).first()
            if not exits:
                db_session.merge(rolper)
                db_session.commit()
        return redirect('/administrarrol')
    return redirect(url_for('administrarpermiso', isAdministrar = False, idrol = idrol))

@app.errorhandler(404)
def page_not_found(error):
    """Lanza un mensaje de error en caso de que la pagina solicitada no exista"""
    return 'Esta Pagina no existe', 404

@app.after_request
def shutdown_session(response):
    """Cierra la sesion de la conexion con la base de datos"""
    db_session.remove()
    return response
