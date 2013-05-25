from loginC import app
from util.database import init_db, engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import func
from flask import Flask, render_template, request, redirect, url_for, flash, session
import flask, flask.views
from ges.mod.SolicitudCambio import SolicitudCambio
from adm.mod.MiembrosComite import MiembrosComite
from ges.mod.ResolucionMiembros import ResolucionMiembros
from adm.mod.Proyecto import Proyecto

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

@app.route('/solicitudavotar/administraravotar', methods=['GET', 'POST'])
def administraravotar():
    idusuario = session['user_id']
    idproyecto= session['pry']
    solicitudes = db_session.query(SolicitudCambio).join(MiembrosComite, MiembrosComite.id_proyecto == SolicitudCambio.id_proyecto).filter(MiembrosComite.id_usuario == idusuario).filter(SolicitudCambio.id_proyecto == idproyecto).filter(SolicitudCambio.estado == 'E').all()
    return render_template('solicitudavotar/administrarsolicitudavotar.html', solicitudes = solicitudes)

@app.route('/solicitudavotar/veritems', methods=['GET', 'POST'])  
def veritems():
    return 'prueba'

def aprobarSolicitud():
    idproyecto=1
    idsolicitud=1
    cantidadaprobado = db_session.query(func.count(ResolucionMiembros)).filter(ResolucionMiembros.id_solicitud_cambio == idsolicitud).filter(ResolucionMiembros.voto == True);
    db_session.query(Proyecto).filter(Proyecto.id == idproyecto);