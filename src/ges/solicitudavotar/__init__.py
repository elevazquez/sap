from loginC import app
from util.database import init_db, engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import func, or_
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session
import flask, flask.views
from ges.mod.SolicitudCambio import SolicitudCambio
from adm.mod.MiembrosComite import MiembrosComite
from ges.mod.ResolucionMiembros import ResolucionMiembros
from adm.mod.Usuario import Usuario
from adm.mod.Proyecto import Proyecto
from ges.mod.ResolucionMiembros import ResolucionMiembros
from flask_login import current_user
from des.mod.Item import Item
from ges.solicitud.SolicitudFormulario import SolicitudFormulario

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

class SolicitudAvotarControlador(flask.views.MethodView):
    def get(self):
        return flask.render_template('solicitudAvotar.html')

def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ),'error')

@app.route('/solicitudavotar/administrarsolicitudavotar', methods=['GET', 'POST'])
def administrarsolicitudavotar():
    idusuario = current_user.id
    idproyecto= session['pry']
    solicitudes = db_session.query(SolicitudCambio).join(MiembrosComite, MiembrosComite.id_proyecto == SolicitudCambio.id_proyecto).filter(MiembrosComite.id_usuario == idusuario).filter(SolicitudCambio.id_proyecto == idproyecto).filter(SolicitudCambio.estado == 'E').all()
    return render_template('solicitudavotar/administrarsolicitudavotar.html', solicitudes = solicitudes)

@app.route('/solicitudavotar/buscarsolicitudavotar', methods=['GET', 'POST'])
def buscarsolicitudavotar():
    idusuario = current_user.id
    idproyecto= session['pry']
    valor = request.args['patron']
    parametro = request.args['parametro']
    if valor=='' or valor == None:
        return administrarsolicitudavotar()
    else:
        if parametro == 'fecha':
            try:
                fecha = datetime.strptime(valor, '%Y-%m-%d')
                solicitudes = db_session.query(SolicitudCambio).join(MiembrosComite, MiembrosComite.id_proyecto == SolicitudCambio.id_proyecto).filter(MiembrosComite.id_usuario == idusuario).filter(SolicitudCambio.id_proyecto == idproyecto).filter(SolicitudCambio.estado == 'E').filter(SolicitudCambio.fecha == fecha).all()
            except ValueError:
                solicitudes =[]
        elif parametro == 'nombre':
            solicitudes = db_session.query(SolicitudCambio).join(MiembrosComite, MiembrosComite.id_proyecto == SolicitudCambio.id_proyecto).filter(MiembrosComite.id_usuario == idusuario).join(Usuario, SolicitudCambio.id_usuario == Usuario.id).filter(SolicitudCambio.id_proyecto == idproyecto).filter(SolicitudCambio.estado == 'E').filter(or_(Usuario.nombre.ilike('%'+valor+'%'),Usuario.apellido.ilike('%'+valor+'%'))).all()
        elif parametro == 'cant_votos':
            if valor.isdigit() :
                solicitudes = db_session.query(SolicitudCambio).join(MiembrosComite, MiembrosComite.id_proyecto == SolicitudCambio.id_proyecto).filter(MiembrosComite.id_usuario == idusuario).filter(SolicitudCambio.id_proyecto == idproyecto).filter(SolicitudCambio.estado == 'E').filter(SolicitudCambio.cant_votos == valor).all()
            else :
                solicitudes = []
        elif parametro == 'descripcion' :
            solicitudes = db_session.query(SolicitudCambio).join(MiembrosComite, MiembrosComite.id_proyecto == SolicitudCambio.id_proyecto).filter(MiembrosComite.id_usuario == idusuario).filter(SolicitudCambio.id_proyecto == idproyecto).filter(SolicitudCambio.estado == 'E').filter(SolicitudCambio.descripcion.ilike('%'+valor+'%')).all()
            #relaciones = db_session.query(Relacion).from_statement("SELECT * FROM relacion where to_char("+parametro+", '99999') ilike '%"+valor+"%'").all()
            #p = db_session.query(Relacion).from_statement("SELECT * FROM relacion where "+parametro+" = CAST("+valor+" AS Int)").all()
        else:
            return administrarsolicitudavotar()()
    #p = db_session.query(Relacion).filter(Relacion.codigo.like('%'+valor+ '%'))
        return render_template('solicitudavotar/administrarsolicitudavotar.html', solicitudes = solicitudes)


@app.route('/solicitudavotar/veritems', methods=['GET', 'POST'])  
def veritems():
    """ Funcion para editar registros de la tabla Solicitud""" 
#    init_db(db_session)
    pro = db_session.query(Proyecto).filter_by(id=session['pry']).first()
    idusuario= current_user.id
    if  request.args.get('id') == None:
        id_sol= request.form.get('id')
    else:
        id_sol=request.args.get('id')
    solicitud = db_session.query(SolicitudCambio).filter_by(id=id_sol).filter_by(id_proyecto=session['pry']).first()
    itemssol=  db_session.query(Item).from_statement("select * from item where id in(select id_item from solicitud_item where id_solicitud="+str(id_sol)+")")  
    form = SolicitudFormulario(request.form,solicitud)
    usuario =db_session.query(Usuario).filter_by(id=solicitud.id_usuario).first()
    voto = db_session.query(ResolucionMiembros).filter(ResolucionMiembros.id_solicitud_cambio == id_sol).filter(ResolucionMiembros.id_usuario == idusuario).first()
    form.id_proyecto.data = pro.nombre
    form.id_usuario.data = usuario.usuario
    if solicitud.estado=='E':
        form.estado.data='Enviada'
    return render_template('solicitudavotar/itemssolicitud.html', form=form, items=itemssol, voto = voto)

@app.route('/solicitudavotar/votar', methods=['GET', 'POST'])  
def votar():
    voto = request.form.get('voto')
    idsolicitud = request.form.get('id')
    iduser = current_user.id
    resolucion=ResolucionMiembros(voto, idsolicitud, iduser)
    db_session.add(resolucion)
    db_session.commit()
    comiteCambio = db_session.query(SolicitudCambio).filter_by(id = idsolicitud).first()
    comiteCambio.cant_votos = comiteCambio.cant_votos + 1
    db_session.merge(comiteCambio)
    db_session.commit()
    aprobarSolicitud(session['pry'], idsolicitud)
    return redirect('/solicitudavotar/administrarsolicitudavotar')
        
def aprobarSolicitud(idproyecto, idsolicitud):
    cantidadvotante = db_session.query(func.count(ResolucionMiembros)).filter(ResolucionMiembros.id_solicitud_cambio == idsolicitud);
    cantidadaprobado = db_session.query(func.count(ResolucionMiembros)).filter(ResolucionMiembros.id_solicitud_cambio == idsolicitud).filter(ResolucionMiembros.voto == True);
    proyecto = db_session.query(Proyecto).filter(Proyecto.id == idproyecto).first();
    mayoria = (proyecto.cant_miembros // 2) + 1
    if (cantidadvotante == proyecto.cant_miembros) and (cantidadaprobado >= (mayoria )):
        solicitud = db_session.query(SolicitudCambio).filter_by(id= idsolicitud).first()
        solicitud.estado= 'A'
        db_session.merge(solicitud)
        db_session.commit()
        flash ('Solicitud aprobada','info')
    else:
        flash ('Solicitud no aprobada','info')
        
@app.errorhandler(404)
def page_not_found(error):
    return 'Esta Pagina no existe', 404

"""Cierra la sesion de la conexion con la base de datos"""
@app.after_request
def shutdown_session(response):
    db_session.remove()
    return response