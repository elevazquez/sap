from loginC import app

from util.database import init_db, engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import DatabaseError
from flask import Flask, render_template, request, redirect, url_for, flash 
from adm.mod.Usuario import Usuario
from adm.mod.Permiso import Permiso
from adm.mod.RolPermiso import RolPermiso
from des.mod.Fase import Fase
from adm.usuario.UsuarioFormulario import UsuarioFormulario
from adm.rol import getRolesByUsuario
import flask, flask.views
from UserPermission import UserRol
from sqlalchemy import or_
import os
import datetime
import md5
from adm.mod.UsuarioRol import UsuarioRol
from adm.mod.Rol import Rol
from adm.mod.Recurso import Recurso
from adm.mod.Proyecto import Proyecto
from flask_login import current_user
    
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
                
@app.route('/usuario/nuevousuario', methods=['GET', 'POST'])
def nuevousuario():
    """ Funcion para agregar registros a la tabla Usuario""" 
    """ Se obtiene la fecha actual para verificar la fecha de nacimiento """
    if not current_user.is_authenticated():
        flash('Debe loguearse primeramente!!!!', 'loggin')
        return render_template('index.html')
    
    permission = UserRol('ADMINISTRADOR')
    if permission.can():
        today = datetime.date.today()
        form = UsuarioFormulario(request.form)
        """ Se un objeto md5 para encriptar la contrasenha del usuario """    
        con = md5.new()  
        if request.method == 'POST' and form.validate():
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
    else:
        flash('Sin permisos para agregar usuarios', 'permiso')
        return render_template('index.html')

@app.route('/usuario/editarusuario', methods=['GET', 'POST'])
def editarusuario():
    """ Funcion para editar registros de la tabla Usuario""" 
    """ Se obtiene la fecha actual para almacenar la fecha de ultima actualizacion """
    if not current_user.is_authenticated():
        flash('Debe loguearse primeramente!!!!', 'loggin')
        return render_template('index.html')
    
    permission = UserRol('ADMINISTRADOR')
    if permission.can():
        today = datetime.date.today()
        """ Se un objeto md5 para encriptar la contrasenha del usuario """    
        con = md5.new()
        conf = md5.new()
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
                aux = usuario.id
                form.populate_obj(usuario)
                usuario.password = con.hexdigest()
                usuario.id = aux
                db_session.merge(usuario)
                db_session.commit()
                flash('El usuario ha sido modificado con exito','info')
                return redirect('/usuario/administrarusuario')
            except DatabaseError, e:
                flash('Error en la Base de Datos' + e.args[0],'error')
                return render_template('usuario/editarusuario.html', form=form)
        else:
            flash_errors(form)
        return render_template('usuario/editarusuario.html', form=form)
    else:
        flash('Sin permisos para editar usuarios', 'permiso')
        return render_template('index.html')

@app.route('/usuario/eliminarusuario', methods=['GET', 'POST'])
def eliminarusuario():
    """ Funcion para eliminar registros de la tabla Usuario""" 
    if not current_user.is_authenticated():
        flash('Debe loguearse primeramente!!!!', 'loggin')
        return render_template('index.html')
    
    permission = UserRol('ADMINISTRADOR')
    if permission.can():
        try:
            usu = request.args.get('usu')
            usuario = db_session.query(Usuario).filter_by(usuario=usu).first()  
            db_session.delete(usuario)
            db_session.commit()
            flash('El usuario ha sido eliminado con exito','info')
            return redirect('/usuario/administrarusuario')
        except DatabaseError, e:
            flash('Error en la Base de Datos' + e.args[0],'info')
            return render_template('usuario/administrarusuario.html')
    else:
        flash('Sin permisos para eliminar usuarios', 'permiso')
        return render_template('index.html')
    
@app.route('/usuario/buscarusuario', methods=['GET', 'POST'])
def buscarusuario():
    """ Funcion para buscar registros de la tabla Usuario""" 
    if not current_user.is_authenticated():
        flash('Debe loguearse primeramente!!!!', 'loggin')
        return render_template('index.html')
    
    permission = UserRol('ADMINISTRADOR')
    if permission.can():
        valor = request.args['patron']
        parametro = request.args['parametro']
        if valor == "" : 
            administrarusuario()
        if parametro == 'fecha_nac':
            p = db_session.query(Usuario).from_statement("SELECT * FROM usuario where to_char("+parametro+", 'YYYY-mm-dd') ilike '%"+valor+"%'").all()
        else:
            p = db_session.query(Usuario).from_statement("SELECT * FROM usuario where "+parametro+" ilike '%"+valor+"%'").all()
        return render_template('usuario/administrarusuario.html', usuarios = p)   
        valor = request.args['patron']
        r = db_session.query(Usuario).filter_by(usuario=valor)
        return render_template('usuario/administrarusuario.html', usuarios = r)
    else:
        flash('Sin permisos para buscar usuarios', 'permiso')
        return render_template('index.html')

@app.route('/usuario/administrarusuario')
def administrarusuario():
    """ Funcion para listar registros de la tabla Usuario """ 
    if not current_user.is_authenticated():
        flash('Debe loguearse primeramente!!!!', 'loggin')
        return render_template('index.html')
    
    permission = UserRol('ADMINISTRADOR')
    if permission.can():
        usuarios = db_session.query(Usuario).order_by(Usuario.nombre)
        return render_template('usuario/administrarusuario.html', usuarios = usuarios)
    else:
        flash('Sin permisos para administrar usuarios', 'permiso')
        return render_template('index.html')

#===============================================================================
# @app.route('/usuario/asignarrol')    
# def asignarrol():
#    """ Funcion para asignar roles a un usuario """ 
#    if not current_user.is_authenticated():
#        flash('Debe loguearse primeramente!!!!', 'loggin')
#        return render_template('index.html')
#    
#    permission = UserRol('ADMINISTRADOR')
#    if permission.can():
#        idusuario = request.args.get('usu')
#        asignados= db_session.query(UsuarioRol).filter_by(id_usuario = idusuario).all()
#        if request.method == 'POST':
#            idusuario = request.form.get('usu')
#            
#            rolesmarcados=request.form.getlist('roles')
#            #===================================================================
#            # Inserta los roles permisos seleccionados, si no existe realiza el merge y confirma los cambios
#            #===================================================================
#            for r in rolesmarcados :
#                rolusu = UsuarioRol(idusuario, r, 1)
#                exits = db_session.query(UsuarioRol).filter_by(id_usuario=idusuario, id_rol=r).first()
#                if not exits:
#                    db_session.merge(rolusu)
#                    db_session.commit()
#            return redirect('/administrarusuario')
#        return redirect(url_for('asignarrol', idusuario = idusuario, asignados = asignados))
#    else:
#        flash('Sin permisos para asignar roles a los usuarios', 'permiso')
#        return render_template('index.html')
#===============================================================================
    
@app.route('/usuario/agregarrolusu', methods=['GET', 'POST'])
def agregarrolusu():
    """ Funcion para asignar Roles a un Usuario""" 
    if not current_user.is_authenticated():
        flash('Debe loguearse primeramente!!!!', 'loggin')
        return render_template('index.html')
    
    permission =UserRol('ADMINISTRADOR')
    if permission.can()==False:
        flash('No posee los permisos suficientes para realizar la operacion', 'permiso')
        return render_template('index.html')
  
    if  request.args.get('usu') == None:
        id_usu= request.form.get('id')
    else:
        id_usu=request.args.get('usu')
    usu = db_session.query(Usuario).filter_by(id=id_usu).first()
    rolesv=  db_session.query(Rol).from_statement("select * from rol where id not in (select id_rol from usuario_rol where id_usuario="+str(usu.id)+
                                                  ") and rol.codigo <> 'LIDER PROYECTO' and rol.codigo <> 'COMITE CAMBIOS'").all()
    aux=[]
    for rl in rolesv :
        pro=  db_session.query(Proyecto).from_statement("select * from proyecto where id in "+
                                                        "(select id_proyecto from fase where id in"+
                                                            "(select id_fase from recurso where id in"+
                                                                "(select id_recurso from permiso where id in"+
                                                                    "(select id_permiso from rol_permiso where id_rol="+str(rl.id)+" limit 1)"+
                                                                ")))").first()
        aux.append(pro)
    form = UsuarioFormulario(request.form,usu)
    usuario = db_session.query(Usuario).filter_by(id=usu.id).first()     
    if request.method == 'POST' : 
        roles=request.form.getlist('selectrol')
        try:
            list_aux=[]
            for rl in roles :
                r = db_session.query(Rol).filter_by(id=rl).first()    
                list_aux.append(r)

            if list_aux == None or list_aux == []:
                flash('Debe seleccionar un Rol','info')
                return render_template('usuario/administrarusuario.html')         
                             
            for rl in list_aux:
                recu = db_session.query(Recurso).join(Permiso, Permiso.id_recurso == Recurso.id).join(RolPermiso, Permiso.id ==RolPermiso.id_permiso).filter(RolPermiso.id_rol == rl.id).first()
                if recu != None:
                    proyecto = db_session.query(Proyecto).join(Recurso, Recurso.id_proyecto == Proyecto.id ).filter(Proyecto.id == recu.id_proyecto).first()
                    if proyecto == None:
                        proyecto = db_session.query(Proyecto).join(Fase, Fase.id_proyecto == Proyecto.id).join(Recurso, Recurso.id_fase == Fase.id).filter(Recurso.id_fase == recu.id_fase).first()
                    if proyecto != None:
                        rousu = UsuarioRol(rl.id, usuario.id, proyecto.id)
                        db_session.add(rousu)
                        db_session.commit()
                    else:
                        flash('El Rol aun no tiene asignado Permisos','info')   
                        return redirect('/usuario/administrarusuario')
                else:
                    if rl.codigo =='ADMINISTRADOR':
                        rousu = UsuarioRol(rl.id, usuario.id, None)
                        db_session.add(rousu)
                        db_session.commit()
                #===============================================================
                # re = db_session.query(Recurso).from_statement("select * from recurso where id in ( select id_recurso from permiso where id in " +
                #    " (select id_permiso from rol_permiso where id_rol="+str(rl.id)+" limit 1))").first() 
                #===============================================================
            flash('Se agrego el Rol con Exito','info')   
            return redirect('/usuario/administrarusuario')
        except DatabaseError, e:
            flash('Error en la Base de Datos' + e.args[0],'error')
        return render_template('usuario/agregarrolusu.html', form=form, roles= rolesv, pro=aux)  
    return render_template('usuario/agregarrolusu.html', form=form, roles= rolesv, pro=aux)  

@app.route('/usuario/quitarrolusu', methods=['GET', 'POST'])
def quitarrolusu():
    """ Funcion para quitar Roles al Usuario""" 
    if not current_user.is_authenticated():
        flash('Debe loguearse primeramente!!!!', 'loggin')
        return render_template('index.html')
 
    permission =UserRol('ADMINISTRADOR')
    if permission.can()==False:
        flash('No posee los permisos suficientes para realizar la operacion', 'permiso')
        return render_template('index.html')
 
    if  request.args.get('usu') == None:
        id_usu= request.form.get('id')
    else:
        id_usu=request.args.get('usu')    
    usu = db_session.query(Usuario).filter_by(id=id_usu).first()  
    form = UsuarioFormulario(request.form,usu)    
    rolesv=  db_session.query(Rol).from_statement("select * from rol where id in (select id_rol from usuario_rol where id_usuario="+str(usu.id)+")").all()
    aux=[]
    for rl in rolesv :
        pro=  db_session.query(Proyecto).from_statement("select * from proyecto where id in (select id_proyecto from recurso where id in "+ 
       " ( select id_recurso from permiso where id in (select id_permiso from rol_permiso where id_rol="+str(rl.id)+" limit 1)))").first()
        aux.append(pro)
    if request.method == 'POST' : 
        roles=request.form.getlist('selectrol')
        try:
            list_aux=[]
            #===================================================================
            # if len(rolesv) == len(roles):
            #    flash('El Usuario no puede quedarse sin Roles','info')   
            #    return redirect('/usuario/administrarusuario')
            #===================================================================
            for rl in roles :
                r = db_session.query(Rol).filter_by(id=rl).first()
                list_aux.append(r)
                          
            for rl in list_aux:
                ur = db_session.query(UsuarioRol).filter_by(id_rol=rl.id,id_usuario=request.form.get('id')).first()  
                db_session.delete(ur)
                db_session.commit()
                flash('Se quito el Rol con Exito','info')   
            return redirect('/usuario/administrarusuario')
        except DatabaseError, e:
            flash('Error en la Base de Datos' + e.args[0],'error')
            return render_template('usuario/quitarrolusu.html', form=form, roles=rolesv, pro=aux)
    return render_template('usuario/quitarrolusu.html', form=form, roles=rolesv, pro=aux)  

@app.route('/usuario/verrolusu')
def verrolusu():
    """ Funcion para listar Roles de un Usuario""" 
    if not current_user.is_authenticated():
        flash('Debe loguearse primeramente!!!!', 'loggin')
        return render_template('index.html')
    
    permission =UserRol('ADMINISTRADOR')
    if permission.can()==False:
        flash('No posee los permisos suficientes para realizar la operacion', 'permiso')
        return render_template('index.html')
    
    id_usu = request.args.get('usu') 
    usu = db_session.query(Usuario).filter_by(id=id_usu).first()
    rolesv=  db_session.query(Rol).from_statement("select * from rol where id in (select id_rol from usuario_rol where id_usuario="+str(usu.id)+")").all()
    aux=[]
    for rl in rolesv :
        pro=  db_session.query(Proyecto).from_statement("select * from proyecto where id in (select id_proyecto from recurso where id in "+ 
       " ( select id_recurso from permiso where id in (select id_permiso from rol_permiso where id_rol="+str(rl.id)+" limit 1)))").first()
        aux.append(pro)
    form = UsuarioFormulario(request.form,usu)
    return render_template('usuario/verrolusu.html', form=form, roles= rolesv, pro=aux)  

@app.errorhandler(404)
def page_not_found(error):
    """Lanza un mensaje de error en caso de que la pagina solicitada no exista"""
    return 'Esta Pagina no existe', 404

@app.after_request
def shutdown_session(response):
    """Cierra la sesion de la conexion con la base de datos"""
    db_session.remove()
    return response