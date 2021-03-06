from loginC import app

from util.database import init_db, engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import DatabaseError
from flask import Flask, render_template, request, redirect, url_for, flash, session
from des.mod.Fase import Fase
from adm.mod.Rol import Rol
from adm.mod.Proyecto import Proyecto
from adm.mod.Usuario import Usuario
from adm.mod.UsuarioRol import UsuarioRol
from adm.mod.Recurso import Recurso
from adm.mod.Permiso import Permiso
from adm.mod.RolPermiso import RolPermiso
from adm.mod.MiembrosComite import MiembrosComite
from ges.mod.SolicitudCambio import SolicitudCambio
from ges.mod.ResolucionMiembros import ResolucionMiembros
from adm.proyecto.ProyFormulario import ProyFormulario
from UserPermission import UserPermission, UserRol
import flask, flask.views
import os
import datetime
from flask_login import current_user

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
class ProyControlador(flask.views.MethodView):
    def get(self):
        return flask.render_template('proyecto.html')
    
def flash_errors(form):
    """ Funcion para capturar los errores de Formulario""" 
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ),'error')
                
@app.route('/proyecto/nuevoproyecto', methods=['GET', 'POST'])
def nuevoproyecto():
    """ Funcion para agregar registros a la tabla Proyecto""" 
    """ Se obtiene la fecha actual para almacenar la fecha de ultima actualizacion """
    if not current_user.is_authenticated():
        flash('Debe loguearse primeramente!!!!', 'loggin')
        return render_template('index.html')
    
    permission = UserRol('ADMINISTRADOR')
    if permission.can():
        today = datetime.date.today() 
        form = ProyFormulario(request.form)
        r = db_session.query(Rol).filter_by(codigo='COMITE CAMBIOS').first()
        r2 = db_session.query(Rol).filter_by(codigo='LIDER PROYECTO').first()
        form.id_usuario_lider.choices= [(u.id, u.nombre + " " + u.apellido) for u in db_session.query(Usuario).order_by(Usuario.nombre).all()]  
        if request.method == 'POST' and form.validate():
            if form.fecha_inicio.data > form.fecha_fin.data :
                flash('La fecha de inicio no puede ser mayor que la fecha de finalizacion','error')
                return render_template('proyecto/nuevoproyecto.html', form=form)
            if form.cant_miembros.data %2 == 0 :
                flash('La cantidad maxima de miembros debe ser impar','error')
                return render_template('proyecto/nuevoproyecto.html', form=form)
            try:
                pry = Proyecto(form.nombre.data, form.descripcion.data, 
                    'N', form.cant_miembros.data, 
                    form.fecha_inicio.data, form.fecha_fin.data, 
                    today, form.id_usuario_lider.data)
                db_session.add(pry)
                db_session.commit()
                mc = MiembrosComite(pry.id, form.id_usuario_lider.data)
                db_session.add(mc)
                db_session.commit()
                """ Asignar los roles comite cambios y lider proyecto en caso de que no existan"""
                if r == None :
                    r = Rol('COMITE CAMBIOS', 'COMITE CAMBIOS')
                    db_session.add(r)
                    db_session.commit()
                if r2 == None :
                    r2 = Rol('LIDER PROYECTO', 'LIDER PROYECTO')
                    db_session.add(r2)
                    db_session.commit()
                """ Asignar el rol lider proyecto """
                li = UsuarioRol(r2.id, pry.id_usuario_lider, pry.id)
                db_session.add(li)
                db_session.commit()
                """ Asignar los permisos de consulta al comite """                
                re = db_session.query(Recurso).filter_by(id_proyecto=pry.id).filter_by(nombre=pry.nombre).first()  
                if re == None :
                    re = Recurso(pry.nombre, pry.id)
                    db_session.add(re)
                    db_session.commit()
                per = db_session.query(Permiso).filter_by(id_recurso=re.id).filter_by(codigo='CONSULTAR PROYECTO').first()
                if per == None :
                    per = Permiso('CONSULTAR PROYECTO', 'CONSULTAR PROYECTO', re.id)
                    db_session.add(per)
                    db_session.commit()
                rp = db_session.query(RolPermiso).filter_by(id_rol=r.id).filter_by(id_permiso=per.id).first()
                if rp == None :
                    rp = RolPermiso(r.id, per.id)
                    db_session.add(rp)
                    db_session.commit()
                flash('El Proyecto ha sido registrado con exito','info')
                return redirect('/proyecto/administrarproyecto')
            except DatabaseError, e:
                if e.args[0].find('duplicate key value violates unique')!=-1:
                    flash('Clave unica violada por favor ingrese otro NOMBRE de Proyecto' ,'error')
                else:
                    flash('Error en la Base de Datos' + e.args[0],'error')
                return render_template('proyecto/nuevoproyecto.html', form=form)
        else:
            flash_errors(form) 
        return render_template('proyecto/nuevoproyecto.html', form=form)
    else:
        flash('Sin permisos para agregar proyectos', 'permiso')
        return render_template('index.html')

@app.route('/proyecto/editarproyecto', methods=['GET', 'POST'])
def editarproyecto():
    """ Se obtiene la fecha actual para almacenar la fecha de ultima actualizacion """
    if not current_user.is_authenticated():
        flash('Debe loguearse primeramente!!!!', 'loggin')
        return render_template('index.html')
    
    permission = UserRol('ADMINISTRADOR')
    if permission.can():
        today = datetime.date.today()
        #init_db(db_session)
        r2 = db_session.query(Rol).filter_by(codigo='LIDER PROYECTO').first()
        p = db_session.query(Proyecto).filter_by(nombre=request.args.get('nom')).first()  
        form = ProyFormulario(request.form,p)
        proyecto = db_session.query(Proyecto).filter_by(nombre=form.nombre.data).first()
        form.id_usuario_lider.choices= [(u.id, u.nombre + " " + u.apellido) for u in db_session.query(Usuario).order_by(Usuario.nombre).all()]  
        mc = proyecto.id_usuario_lider
        if proyecto.estado == 'N' :
            form.estado.data = 'Nuevo'
        elif proyecto.estado == 'P' :
            form.estado.data = 'En Progreso'
        elif proyecto.estado == 'A' :
            form.estado.data = 'Anulado'
        elif proyecto.estado == 'F' :
            form.estado.data = 'Finalizado'
        if request.method == 'POST' and form.validate():
            if form.fecha_inicio.data > form.fecha_fin.data :
                flash('La fecha de inicio no puede ser mayor que la fecha de finalizacion','error')
                return render_template('proyecto/editarproyecto.html', form=form)
            if form.cant_miembros.data %2 == 0 :
                flash('La cantidad maxima de miembros debe ser impar','error')
                return render_template('proyecto/editarproyecto.html', form=form) 
            try:
                form.populate_obj(proyecto)
                proyecto.fecha_ultima_mod = today
                if form.estado.data == 'Nuevo' :
                    proyecto.estado = 'N'
                elif form.estado.data == 'En Progreso' :
                    proyecto.estado = 'P'
                elif form.estado.data == 'Anulado' :
                    proyecto.estado = 'A'
                elif form.estado.data == 'Finalizado' :
                    proyecto.estado = 'F'
                db_session.merge(proyecto)
                db_session.commit()
            
                if mc != proyecto.id_usuario_lider:
                    miembrosComite = db_session.query(MiembrosComite).filter_by(id_usuario=mc).filter_by(id_proyecto=proyecto.id).first()  
                    #init_db(db_session)
                    db_session.delete(miembrosComite)
                    db_session.commit()

                    lr = db_session.query(UsuarioRol).filter_by(id_rol=r2.id).filter_by(id_usuario=mc).filter_by(id_proyecto=proyecto.id).first()  
                    #init_db(db_session)
                    db_session.delete(lr)
                    db_session.commit()
                    
                    miembro = MiembrosComite(proyecto.id, proyecto.id_usuario_lider)
                    db_session.add(miembro)
                    db_session.commit()
            
                    li = UsuarioRol(r2.id, proyecto.id_usuario_lider, proyecto.id)
                    db_session.add(li)
                    db_session.commit()
                flash('El Proyecto ha sido modificado con exito','info')
                return redirect('/proyecto/administrarproyecto')
            except DatabaseError, e:
                flash('Error en la Base de Datos' + e.args[0],'error')
                return render_template('proyecto/editarproyecto.html', form=form)
        else:
            flash_errors(form)
        return render_template('proyecto/editarproyecto.html', form=form)
    else:
        flash('Sin permisos para editar proyectos', 'permiso')
        return render_template('index.html')

@app.route('/proyecto/eliminarproyecto', methods=['GET', 'POST'])
def eliminarproyecto():
    """ Funcion para eliminar registros de la tabla Proyecto"""
    if not current_user.is_authenticated():
        flash('Debe loguearse primeramente!!!!', 'loggin')
        return render_template('index.html')
    
    permission = UserRol('ADMINISTRADOR')
    if permission.can():
        try:
            r = db_session.query(Rol).filter_by(codigo='COMITE CAMBIOS').first()
            r2 = db_session.query(Rol).filter_by(codigo='LIDER PROYECTO').first()
            nom = request.args.get('nom')
            #init_db(db_session)
            proyecto = db_session.query(Proyecto).filter_by(nombre=nom).first()
            com = db_session.query(MiembrosComite).filter(MiembrosComite.id_usuario!=proyecto.id_usuario_lider).filter_by(id_proyecto=proyecto.id).first()  
            if proyecto.estado != 'N' :
                flash('No se puede eliminar un Proyecto que no se encuentre en estado Nuevo','info')
                return render_template('proyecto/administrarproyecto.html')
            if com != None :
                flash('Por favor desasigne los Miembros del Comite de Cambios del Proyecto para poder eliminar','info')
                return render_template('proyecto/administrarproyecto.html')
        
            mie = db_session.query(MiembrosComite).filter_by(id_usuario=proyecto.id_usuario_lider).filter_by(id_proyecto=proyecto.id).first()  
            #init_db(db_session)
            db_session.delete(mie)
            db_session.commit()
        
            li = db_session.query(UsuarioRol).filter_by(id_rol=r2.id).filter_by(id_usuario=proyecto.id_usuario_lider).filter_by(id_proyecto=proyecto.id).first()  
            #init_db(db_session)
            db_session.delete(li)
            db_session.commit()
        
            re = db_session.query(Recurso).filter_by(id_proyecto=proyecto.id).filter_by(nombre=proyecto.nombre).first()  
            per = db_session.query(Permiso).filter_by(id_recurso=re.id).filter_by(codigo='CONSULTAR PROYECTO').first()
            rp = db_session.query(RolPermiso).filter_by(id_rol=r.id).filter_by(id_permiso=per.id).first()

            db_session.delete(rp)
            db_session.commit()
        
            db_session.delete(per)
            db_session.commit()
        
            db_session.delete(re)
            db_session.commit()
        
            db_session.delete(proyecto)
            db_session.commit()
            flash('El proyecto ha sido eliminado con exito', 'info')
            return redirect('/proyecto/administrarproyecto')
        except DatabaseError, e:
            flash('Error en la Base de Datos' + e.args[0],'info')
            return render_template('proyecto/administrarproyecto.html')
    else:
        flash('Sin permisos para eliminar proyectos', 'permiso')
        return render_template('index.html')
    
@app.route('/proyecto/buscarproyecto', methods=['GET', 'POST'])
def buscarproyecto():
    """ Funcion para buscar registros en la tabla Proyecto"""
    if not current_user.is_authenticated():
        flash('Debe loguearse primeramente!!!!', 'loggin')
        return render_template('index.html')
    
    permission = UserRol('ADMINISTRADOR')
    if permission.can():
        valor = request.args['patron']
        parametro = request.args['parametro']
        if valor == "" : 
            administrarproyecto()
        if parametro == 'cant_miembros' :
            p = db_session.query(Proyecto).from_statement("SELECT * FROM proyecto where to_char("+parametro+", '99999') ilike '%"+valor+"%'").all()
        elif parametro == 'id_usuario_lider':
            p = db_session.query(Proyecto).from_statement("SELECT * FROM proyecto where "+parametro+" in (SELECT id FROM usuario where nombre ilike '%"+valor+"%' or apellido ilike '%"+valor+"%')").all()
        elif parametro == 'fecha_inicio' or parametro == 'fecha_fin':
            p = db_session.query(Proyecto).from_statement("SELECT * FROM proyecto where to_char("+parametro+", 'YYYY-mm-dd') ilike '%"+valor+"%'").all()
        else:
            p = db_session.query(Proyecto).from_statement("SELECT * FROM proyecto where "+parametro+" ilike '%"+valor+"%'").all()
        return render_template('proyecto/administrarproyecto.html', proyectos = p)   

    else:
        idproy = None
        if 'pry' in session:
            idproy = session['pry']
        permiss = UserPermission('LIDER PROYECTO', int(idproy))
        opcionPerm = UserPermission('COMITE CAMBIOS', int(session['pry']))
        if permiss.can() or opcionPerm.can():
            valor = request.args['patron']
            parametro = request.args['parametro']
            if valor == "" : 
                administrarproyecto()
            if parametro == 'cant_miembros' :
                p = db_session.query(Proyecto).from_statement("SELECT * FROM proyecto where to_char("+parametro+", '99999') ilike '%"+valor+"%' and id = "+str(idproy)).all()
            elif parametro == 'id_usuario_lider':
                p = db_session.query(Proyecto).from_statement("SELECT * FROM proyecto where "+parametro+" in (SELECT id FROM usuario where nombre ilike '%"+valor+"%' or apellido ilike '%"+valor+"%') and id = "+str(idproy)).all()
            elif parametro == 'fecha_inicio' or parametro == 'fecha_fin':
                p = db_session.query(Proyecto).from_statement("SELECT * FROM proyecto where to_char("+parametro+", 'YYYY-mm-dd') ilike '%"+valor+"%' and id = "+str(idproy)).all()
            else:
                p = db_session.query(Proyecto).from_statement("SELECT * FROM proyecto where "+parametro+" ilike '%"+valor+"%' and id = "+str(idproy)).all()
            return render_template('proyecto/administrarproyecto.html', proyectos = p)
        else:
            flash('Sin permisos para buscar proyectos', 'permiso')
            return render_template('index.html')

@app.route('/proyecto/administrarproyecto')
def administrarproyecto():
    """ Funcion para listar registros de la tabla Proyecto""" 
    if not current_user.is_authenticated():
        flash('Debe loguearse primeramente!!!!', 'loggin')
        return render_template('index.html')
    
    idproy = None
    if 'pry' in session:
        idproy = session['pry']
    permission = UserRol('ADMINISTRADOR')
    if permission.can():
        if idproy != None :  
            proyectos = db_session.query(Proyecto).filter(Proyecto.id == idproy).all()
        else :
            proyectos = db_session.query(Proyecto).order_by(Proyecto.nombre)
    else:
        permiss = UserPermission('LIDER PROYECTO', int(idproy))
        opcionPerm = UserPermission('COMITE CAMBIOS', int(session['pry']))
        if permiss.can() or opcionPerm.can():
            proyectos = db_session.query(Proyecto).filter(Proyecto.id == idproy).all()
        else:
            flash('Sin permisos para administrar proyectos', 'permiso')
            return render_template('index.html')
    return render_template('proyecto/administrarproyecto.html', proyectos = proyectos)

@app.errorhandler(404)
def page_not_found(error):
    """Lanza un mensaje de error en caso de que la pagina solicitada no exista"""
    return 'Esta Pagina no existe', 404

@app.after_request
def shutdown_session(response):
    """Cierra la sesion de la conexion con la base de datos"""
    db_session.remove()
    return response

@app.route('/inicioproyecto')
def getProyectoByUsuario():
    """Funcion que obtiene la lista de los proyectos de un usuario"""
    if not current_user.is_authenticated():
        flash('Debe loguearse primeramente!!!!', 'loggin')
        return render_template('index.html')
    
    usuario = request.args['id_usuario']
    p = db_session.query(Proyecto).join(UsuarioRol, Proyecto.id == UsuarioRol.id_proyecto).filter(UsuarioRol.id_usuario == usuario).group_by(Proyecto.id).all()
    
    if(len(p) == 0):
        return redirect(url_for('index'))
    return render_template('proyecto/principal_proyecto.html', proyectos = p, id_usuario= usuario)

@app.route('/proyectoActual',methods=['GET', 'POST'])
def proyectoActual():
    """Funcion que obtiene el Proyecto Actual"""
    if not current_user.is_authenticated():
        flash('Debe loguearse primeramente!!!!', 'loggin')
        return render_template('index.html')
    #===========================================================================
    # permission = UserRol('ADMINISTRADOR')
    # if not permission.can():
    #===========================================================================
    proyecto = request.args['pyo']
    session['pry'] = proyecto
    p = db_session.query(Proyecto).filter_by(id = proyecto).first()
    session['proyecto_nombre'] = p.nombre
    rol = "LIDER PROYECTO"
    habilitacion = UserPermission(rol, int(proyecto))
    session['permiso_lider'] = habilitacion
    rol2 = "COMITE CAMBIOS"
    habilitacion2 = UserPermission(rol2, int(proyecto))
    session['permiso_miembro'] = habilitacion2
    usuario= request.args['usuario']
    is_solicitud(usuario)         
   
    return redirect(url_for('index'))
    #===========================================================================
    # else:
    #    return 'sin permisos'
    #===========================================================================

def is_solicitud(userid): 
    """Funcion que verifica si es miembro de un comite y si tiene solicitud pendiente a votar
    @param userid:Id del usuario que se verifica """
    es_comite = db_session.query(MiembrosComite).filter_by(id_usuario= userid).first()
    if es_comite != None:
        solicitudes= db_session.query(SolicitudCambio).filter_by(estado ='E').filter_by(id_proyecto=session['pry']).all()
        for sol in solicitudes :
            if sol != None:
                voto= db_session.query(ResolucionMiembros).filter_by(id_usuario= userid).filter_by(id_solicitud_cambio= sol.id).first() 
                if voto != None :
                    session['is_solicitud'] = False  #ya voto
                else :
                    session['is_solicitud'] = True
    else :
        session['is_solicitud'] = False
                    
@app.route('/proyecto/iniciarproyecto')
def iniciarproyecto():
    """Funcion para iniciar el Proyecto"""
    if not current_user.is_authenticated():
        flash('Debe loguearse primeramente!!!!', 'loggin')
        return render_template('index.html')
    
    permission =UserPermission('LIDER PROYECTO', int(session['pry']))
    if permission.can()==False:
        flash('No posee los permisos suficientes para realizar la operacion', 'permiso')
        return render_template('index.html')
    
    nom = request.args.get('nom')
    pro = db_session.query(Proyecto).filter_by(nombre=nom).first()  
    fase = db_session.query(Fase).from_statement("SELECT * FROM fase WHERE id_proyecto='"+str(pro.id)+"' and nro_orden=(SELECT min(nro_orden) FROM fase WHERE id_proyecto='"+str(pro.id)+"')").first()
    cant = db_session.query(MiembrosComite).filter_by(id_proyecto=pro.id).count()
    if fase == None:
        flash('El Proyecto no puede ser iniciado porque no tiene Fases asociadas','info')
        return redirect('/proyecto/administrarproyecto')
    if cant != pro.cant_miembros:
        flash('El Proyecto no puede ser iniciado porque no tiene la cantidad preestablecida de miembros en el Comite de Cambios','info')
        return redirect('/proyecto/administrarproyecto')
    if pro.estado == 'N':
        try:
            pro.estado = 'P'
            db_session.merge(pro)
            db_session.commit()
            flash('El Proyecto se ha iniciado con exito','info')
            return redirect('/proyecto/administrarproyecto')
        except DatabaseError, e:
            flash('Error en la Base de Datos' + e.args[0],'info')
            return redirect('/proyecto/administrarproyecto')
    else:
            flash('El Proyecto no puede ser iniciado','info')
            return redirect('/proyecto/administrarproyecto')
        
@app.route('/proyecto/finalizarproyecto')
def finalizarproyecto():
    """ Funcion para finalizar registros de la tabla Proyecto""" 
    if not current_user.is_authenticated():
        flash('Debe loguearse primeramente!!!!', 'loggin')
        return render_template('index.html')

    permission =UserPermission('LIDER PROYECTO', int(session['pry']))
    if permission.can()==False:
        flash('No posee los permisos suficientes para realizar la operacion', 'permiso')
        return render_template('index.html')

    nom = request.args.get('nom')
    pry = db_session.query(Proyecto).filter_by(nombre=nom).first()
    fases = db_session.query(Fase).filter_by(id_proyecto=pry.id).all()
    f='S'
    if pry.estado!='P':
        flash('El Proyecto no puede ser finalizado, debe estar en estado En Progreso','info')
        return redirect('/proyecto/administrarproyecto')
    else :
        for fa in fases:
            if fa.estado != 'A' :
                f='N'
        if f=='N':
            flash('El Proyecto no puede ser finalizado alguna fase no ha sido Finalizada','info')
            return redirect('/proyecto/administrarproyecto')
        else :
            try:
                pry.estado = 'F'
                db_session.merge(pry)
                db_session.commit()
            
                flash('El Proyecto ha sido finalizado con exito','info')
                return redirect('/proyecto/administrarproyecto')
            except DatabaseError, e:
                flash('Error en la Base de Datos' + e.args[0],'info')
                return redirect('/proyecto/administrarproyecto')
