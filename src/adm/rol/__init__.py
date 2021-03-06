from loginC import app
from UserPermission import UserRol
from adm.mod.Permiso import Permiso
from adm.mod.Proyecto import Proyecto
from adm.mod.Rol import Rol
from adm.mod.Recurso import Recurso
from adm.mod.RolPermiso import RolPermiso
from adm.mod.UsuarioRol import UsuarioRol
from des.mod.Fase import Fase
from adm.permiso import administrarpermiso, getPermisosByRol
from adm.rol.RolFormulario import RolFormulario
from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy.exc import DatabaseError
from sqlalchemy import or_
from sqlalchemy.orm import scoped_session, sessionmaker
from util.database import init_db, engine
import flask
import flask.views
import os
from flask_login import current_user
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
            ), 'error')                

@app.route('/add', methods=['GET', 'POST'])
def add():
    """ Funcion para agregar registros a la tabla Rol"""
    if not current_user.is_authenticated():
        flash('Debe loguearse primeramente!!!!', 'loggin')
        return render_template('index.html')
    
    permission = UserRol('ADMINISTRADOR')
    if permission.can():
        form = RolFormulario(request.form)
        if request.method == 'POST' and form.validate():
            # init_db(db_session)
            try:
                rol = Rol(form.codigo.data, form.descripcion.data)
                db_session.add(rol)
                db_session.commit()
                flash('El rol ha sido registrado con exito', 'info')
                return redirect('/administrarrol')  # /listarol
            except DatabaseError, e:
                if e.args[0].find('duplicate key value violates unique') != -1:
                    flash('Clave unica violada por favor ingrese otro CODIGO de Rol' , 'error')
                else:
                    flash('Error en la Base de Datos' + e.args[0], 'error')
                return render_template('rol/nuevorol.html', form=form)
        else:
            flash_errors(form) 
        return render_template('rol/nuevorol.html', form=form)
    else:
        flash('Sin permisos para agregar roles', 'permiso')
        return render_template('index.html')

@app.route('/editar', methods=['GET', 'POST'])
def editar():
    """ Funcion para editar registros de la tabla Rol"""
    if not current_user.is_authenticated():
        flash('Debe loguearse primeramente!!!!', 'loggin')
        return render_template('index.html')
     
    permission = UserRol('ADMINISTRADOR')
    if permission.can():
        r = db_session.query(Rol).filter_by(codigo=request.args.get('cod')).first()  
        form = RolFormulario(request.form, r)
        rol = db_session.query(Rol).filter_by(codigo=form.codigo.data).first()  
        if request.method == 'POST' and form.validate():
            try:
                form.populate_obj(rol)
                db_session.merge(rol)
                db_session.commit()
                flash('El rol ha sido modificado con exito', 'info')
                return redirect('/administrarrol')
            except DatabaseError, e:
                flash('Error en la Base de Datos' + e.args[0], 'error')
                return render_template('rol/editarrol.html', form=form)
        else:
            flash_errors(form)
        return render_template('rol/editarrol.html', form=form)
    else:
        flash('Sin permisos para editar roles', 'permiso')
        return render_template('index.html')

@app.route('/eliminar', methods=['GET', 'POST'])
def eliminar():
    """ Funcion para eliminar registros de la tabla Rol""" 
    if not current_user.is_authenticated():
        flash('Debe loguearse primeramente!!!!', 'loggin')
        return render_template('index.html')
    
    permission = UserRol('ADMINISTRADOR')
    if permission.can():
        try:
            cod = request.args.get('cod')
            rol = db_session.query(Rol).filter_by(codigo=cod).first()  
            db_session.delete(rol)
            db_session.commit()
            flash('El rol ha sido eliminado con exito', 'info')
            return redirect('/administrarrol')
        except DatabaseError, e:
            flash('Error en la Base de Datos' + e.args[0], 'info')
            return render_template('rol/administrarrol.html')
    else:
        flash('Sin permisos para eliminar roles', 'permiso')
        return render_template('index.html')

@app.route('/buscar', methods=['GET', 'POST'])
def buscar():
    """ Funcion para buscar registros de la tabla Rol""" 
    if not current_user.is_authenticated():
        flash('Debe loguearse primeramente!!!!', 'loggin')
        return render_template('index.html')
    
    permission = UserRol('ADMINISTRADOR')
    if permission.can():
        valor = request.args['patron']
        parametro = request.args['parametro']
        if valor == "" : 
            administrarrol()
        p = db_session.query(Rol).from_statement("SELECT * FROM rol where " + parametro + " ilike '%" + valor + "%'").all()
        return render_template('rol/administrarrol.html', roles=p)
        valor = request.args['patron']
        r = db_session.query(Rol).filter_by(codigo=valor)
        if r == None:
            return 'no existe concordancia'
        return render_template('rol/administrarrol.html', roles=r)
    else:
        flash('Sin permisos para buscar roles', 'permiso')
        return render_template('index.html')

@app.route('/administrarrol', methods=['GET', 'POST'])
def administrarrol():
    """ Funcion para listar registros de la tabla Rol"""
    if not current_user.is_authenticated():
        flash('Debe loguearse primeramente!!!!', 'loggin')
        return render_template('index.html')
    
    permission = UserRol('ADMINISTRADOR')
    if permission.can():
        roles = db_session.query(Rol).order_by(Rol.codigo)
        return render_template('rol/administrarrol.html', roles=roles)
    else:
        flash('Sin permisos para administrar roles', 'permiso')
        return render_template('index.html')

@app.route('/rol/asignarpermiso', methods=['GET', 'POST'])
def asignarpermiso():
    """ Funcion para asignar Permisos a cada Rol"""
    if not current_user.is_authenticated():
        flash('Debe loguearse primeramente!!!!', 'loggin')
        return render_template('index.html')
    
    permission = UserRol('ADMINISTRADOR')
    if permission.can(): 
        #=======================================================================
        # desde aqui : Ejecuta esta seccion la primera vez que entra, cuando selecciona solo el usuario
        #=======================================================================
        idproyecto = request.args.get('idproyecto')
        idrol = request.args.get('idrol')
        rolobtenido = db_session.query(Rol).filter_by(id=idrol).first()
        if not rolobtenido == None:
            if str(rolobtenido.codigo) == 'ADMINISTRADOR':
                flash('El rol no tiene permisos', 'info')
                return redirect('/administrarrol')
        if request.method == 'POST':
            rol = request.form.get('idrol')
            permisos = request.form.getlist('permisos')
            #=======================================================================
            # Inserta los permisos seleccionados
            #=======================================================================
            for p in permisos :
                rolper = RolPermiso(rol, p)
                exits = db_session.query(RolPermiso).filter_by(id_rol=rol, id_permiso=p).first()
                if not exits:
                    db_session.merge(rolper)
                    db_session.commit()
                flash('Permisos asignados correctamente', 'info')
            return redirect('/administrarrol')
        if idproyecto == None:
            #significa que no se selecciono proyecto
            #obtiene permisos de un rol
            permisos = getPermisosByRol(idrol)
            if len(permisos) > 0:
                #si tiene permisos muestra directamente permisos del proyecto
                #obtiene idproyecto del permiso que tenga especificado una fase
                idproyecto = getProyectoByPermiso(permisos)
                #obtiene permisos no asignados al rol
                permisos = listadoPermisosNoAsignados(idproyecto, idrol)
                return render_template('rol/asignarpermisos.html', permisos = permisos, idrol = idrol, idproyecto = idproyecto)
            else :  
                #si no tiene permisos asignados 
                proyectos = db_session.query(Proyecto).order_by(Proyecto.nombre);
                return render_template('proyecto/seleccionproyecto.html', proyectos=proyectos, idrol=idrol)
        else:
            permisos = getPermisosByProyecto(idproyecto)
            return render_template('rol/asignarpermisos.html', permisos = permisos, idrol = idrol, idproyecto = idproyecto)
    else:
        flash('Sin permisos para asignar permisos al rol', 'permiso')
        return render_template('index.html')

@app.route('/rol/buscarpermisoSinasignar', methods=['GET', 'POST'])
def buscarpermisoSinasignar():
    """ Funcion para buscar permisos que no pertenecen al rol """
    if not current_user.is_authenticated():
        flash('Debe loguearse primeramente!!!!', 'loggin')
        return render_template('index.html')
    
    permission = UserRol('ADMINISTRADOR')
    if permission.can():
        idrol = request.args.get('idrol')
        valor = request.args['patron']
        parametro = request.args['parametro']
        if valor == "" : 
            permisos = getPermisosByRol(idrol)
            if len(permisos) > 0:
                #si tiene permisos muestra directamente permisos del proyecto
                #obtiene idproyecto del permiso que tenga especificado una fase
                idproyecto = getProyectoByPermiso(permisos)
                #obtiene permisos no asignados al rol
                permisos = listadoPermisosNoAsignados(idproyecto, idrol)
                return render_template('rol/asignarpermisos.html', permisos = permisos, idrol = idrol)
        else:
            if parametro == 'id_recurso':
                p = db_session.query(Permiso).from_statement("SELECT * FROM permiso where to_char("+parametro+", '99999') ilike '%"+valor+"%'").all()
                #p = db_session.query(Permiso).from_statement("SELECT * FROM permiso where "+parametro+" = CAST("+valor+" AS Int)").all()
            else:
                p = db_session.query(Permiso).from_statement("SELECT * FROM permiso where "+parametro+" ilike '%"+valor+"%'").all()
                
        return render_template('rol/asignarpermisos.html', permisos = p, idrol = idrol)
        valor = request.args['patron']
        # init_db(db_session)
        r = db_session.query(Rol).filter_by(codigo=valor)
        if r == None:
            return 'no existe concordancia'
        return render_template('rol/administrarrol.html', roles=r)
    else:
        flash('Sin permisos para buscar permisos no asignados', 'permiso')
        return render_template('index.html')

@app.route('/rol/desasignarpermiso', methods=['GET', 'POST'])
def desasignarpermiso():
    """ Funcion para desasignar los permisos de un rol """
    if not current_user.is_authenticated():
        flash('Debe loguearse primeramente!!!!', 'loggin')
        return render_template('index.html')
    
    permission = UserRol('ADMINISTRADOR')
    if permission.can():
        idrol = request.args.get('idrol')
        permisos = getPermisosByRol(idrol)
        if request.method == 'POST':
            rol = request.form.get('idrol')
            permisosMarcados = request.form.getlist('permisos')
            permisosAsignados = getPermisosByRol(rol)
            #=======================================================================
            # Inserta los permisos seleccionados
            #=======================================================================
            for pa in permisosAsignados :
                bandera = False
                for pm in permisosMarcados :
                    if int(pm) == pa.id : 
                        bandera = True
                if not bandera : 
                    rolper = db_session.query(RolPermiso).filter_by(id_rol=rol, id_permiso=pa.id).first()
                    db_session.delete(rolper)
                    db_session.commit()
                    flash('Permiso desasignado correctamente', 'info')
            return redirect('/administrarrol')
        return render_template('rol/desasignarpermisos.html', permisos = permisos, idrol = idrol)
    else: 
        flash('Sin permisos para la operacion', 'info')
        return redirect('/administrarrol')

@app.errorhandler(404)
def page_not_found(error):
    """Lanza un mensaje de error en caso de que la pagina solicitada no exista"""
    return 'Esta Pagina no existe', 404

@app.after_request
def shutdown_session(response):
    """Cierra la sesion de la conexion con la base de datos"""
    db_session.remove()
    return response

def getRolesByUsuario(idusuario):
    """ Funcion para obtener los roles segun un usuario
    @param idusuario: id de un usuario """
    yourRoles = db_session.query(Rol).join(UsuarioRol, UsuarioRol.id_rol == Rol.id).filter(UsuarioRol.id_usuario == idusuario).all()
    return yourRoles

def getPermisosByProyecto(idproyecto):
    """ Obtiene todos los permisos pertenecientes a un proyecto, mediante el id de la fase """
    #yourPermisos = db_session.query(Permiso).join(Recurso, Recurso.id == Permiso.id_recurso).join(Proyecto, Proyecto.id == Recurso.id_proyecto).join(Fase, Fase.id == Recurso.id_fase).filter(or_(Proyecto.id == idproyecto, Permiso.id.in_(db_session.query(Permiso.id).join(Recurso, Recurso.id == Permiso.id_recurso).join(Fase, Fase.id == Recurso.id_fase).join(Proyecto, Proyecto.id == Fase.id_proyecto).filter(Proyecto.id == idproyecto)))).all()
    yourPermisos = db_session.query(Permiso).from_statement('SELECT p.id FROM permiso p' +
    ' JOIN recurso r ON r.id = p.id_recurso JOIN ('+
        ' (SELECT rec.id AS recu, pr.id AS proy FROM recurso rec'+
        ' JOIN proyecto pr ON pr.id = rec.id_proyecto'+ 
        ' WHERE pr.id= '+str(idproyecto)+')'+
        ' UNION ALL'+
        ' (SELECT recur.id AS recu, pro.id AS proy FROM recurso recur'+
        ' JOIN fase fa ON fa.id = recur.id_fase'+
        ' JOIN proyecto pro ON pro.id = fa.id_proyecto'+ 
        ' WHERE pro.id = '+str(idproyecto)+')) AS all_rec'+
    ' ON r.id = all_rec.recu'+
    ' WHERE all_rec.proy = '+str(idproyecto)).all()
    return yourPermisos

def listadoPermisosNoAsignados(idproyecto, idrol):
    """ Obtiene los permisos no asignados a un rol
    @param idproyecto: id del proyecto
    @param idrol: id del rol"""
    #permisos = db_session.query(Permiso).join(Recurso, Recurso.id == Permiso.id_recurso).join(Proyecto, Proyecto.id == Recurso.id_proyecto).filter(Proyecto.id == idproyecto).filter(~Permiso.id.in_(db_session.query(Permiso.id).join(RolPermiso, RolPermiso.id_permiso == Permiso.id).filter(RolPermiso.id_rol == idrol))).all()
    permisos = db_session.query(Permiso).from_statement('SELECT p.id FROM permiso p' +
    ' JOIN recurso r ON r.id = p.id_recurso JOIN ('+
        ' (SELECT rec.id AS recu, pr.id AS proy FROM recurso rec'+
        ' JOIN proyecto pr ON pr.id = rec.id_proyecto'+ 
        ' WHERE pr.id= '+str(idproyecto)+')'+
        ' UNION ALL'+
        ' (SELECT recur.id AS recu, pro.id AS proy FROM recurso recur'+
        ' JOIN fase fa ON fa.id = recur.id_fase'+
        ' JOIN proyecto pro ON pro.id = fa.id_proyecto'+ 
        ' WHERE pro.id = '+str(idproyecto)+')) AS all_rec'+
    ' ON r.id = all_rec.recu'+
    ' WHERE all_rec.proy = '+str(idproyecto) +
    ' AND p.id NOT IN (SELECT per.id FROM permiso per'+ 
                ' JOIN rol_permiso rp ON rp.id_permiso = per.id'
                ' WHERE rp.id_rol = '+str(idrol)+')').all()
    return permisos

def getProyectoByPermiso(permisos):
    """ Obtiene el proyecto segun los permisos """
    bandera = False
    pry = None
    for p in permisos:
        recurso = db_session.query(Recurso).filter_by(id = p.id_recurso).first()
        if recurso.id_proyecto == None and not (bandera) :
            pry = db_session.query(Proyecto).join(Fase, Fase.id_proyecto == Proyecto.id).filter(Fase.id == recurso.id_fase).first();
            bandera = True
        else :
            if not(recurso.id_proyecto == None) and not (bandera) :
                bandera = True
                pry = db_session.query(Proyecto).filter(Proyecto.id == recurso.id_proyecto).first();
    return pry.id
