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
from adm.proyecto.ProyFormulario import ProyFormulario
import flask, flask.views
import os
import datetime

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
    today = datetime.date.today()
    form = ProyFormulario(request.form)
    r = db_session.query(Rol).filter_by(codigo='COMITE CAMBIOS').first()
    r2 = db_session.query(Rol).filter_by(codigo='LIDER PROYECTO').first()
    form.id_usuario_lider.choices= [(u.id, u.nombre + " " + u.apellido) for u in db_session.query(Usuario).order_by(Usuario.nombre).all()]  
    if request.method == 'POST' and form.validate():
        #init_db(db_session)
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

@app.route('/proyecto/editarproyecto', methods=['GET', 'POST'])
def editarproyecto():
    """ Se obtiene la fecha actual para almacenar la fecha de ultima actualizacion """
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
            
            return redirect('/proyecto/administrarproyecto')
        except DatabaseError, e:
            flash('Error en la Base de Datos' + e.args[0],'error')
            return render_template('proyecto/editarproyecto.html', form=form)
    else:
        flash_errors(form)
    return render_template('proyecto/editarproyecto.html', form=form)

@app.route('/proyecto/eliminarproyecto', methods=['GET', 'POST'])
def eliminarproyecto():
    """ Funcion para eliminar registros de la tabla Proyecto""" 
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
        
        #init_db(db_session)
        db_session.delete(rp)
        db_session.commit()
        
        #init_db(db_session)
        db_session.delete(per)
        db_session.commit()
        
        #init_db(db_session)
        db_session.delete(re)
        db_session.commit()
        
        #init_db(db_session)
        db_session.delete(proyecto)
        db_session.commit()
        return redirect('/proyecto/administrarproyecto')
    except DatabaseError, e:
            flash('Error en la Base de Datos' + e.args[0],'info')
            return render_template('proyecto/administrarproyecto.html')
    
@app.route('/proyecto/buscarproyecto', methods=['GET', 'POST'])
def buscarproyecto():
    """ Funcion para buscar registros en la tabla Proyecto""" 
    valor = request.args['patron']
    parametro = request.args['parametro']
    #init_db(db_session)
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
    valor = request.args['patron']
    #init_db(db_session)
    r = db_session.query(Proyecto).filter_by(nombre=valor)
    if r == None:
        return 'no existe concordancia'
    return render_template('proyecto/administrarproyecto.html', proyectos = r)

@app.route('/proyecto/administrarproyecto')
def administrarproyecto():
    """ Funcion para listar registros de la tabla Proyecto""" 
    #init_db(db_session)
    proyectos = db_session.query(Proyecto).order_by(Proyecto.nombre)
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
    usuario = request.args['id_usuario']
    p = db_session.query(Proyecto).join(UsuarioRol, Proyecto.id == UsuarioRol.id_proyecto).filter(UsuarioRol.id_usuario == usuario).group_by(Proyecto.id).all()
    return render_template('proyecto/principal_proyecto.html', proyectos = p)

@app.route('/proyectoActual')
def proyectoActual():
    """Funcion que obtiene el Proyecto Actual"""
    proyecto = request.args['pyo']
    session['pry'] = proyecto
    p = db_session.query(Proyecto).filter_by(id = proyecto).first()
    session['proyecto_nombre'] = p.nombre
    return redirect(url_for('index'))

@app.route('/proyecto/iniciarproyecto')
def iniciarproyecto():
    """Funcion para iniciar el Proyecto"""
    #init_db(db_session)
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
            
#            fase.estado = 'P'
#            db_session.merge(fase)
#            db_session.commit()
            flash('El Proyecto se ha iniciado con exito','info')
            return redirect('/proyecto/administrarproyecto')
        except DatabaseError, e:
            flash('Error en la Base de Datos' + e.args[0],'info')
            return redirect('/proyecto/administrarproyecto')
    else:
            flash('El Proyecto no puede ser iniciado','info')
            return redirect('/proyecto/administrarproyecto')