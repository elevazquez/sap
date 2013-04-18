from com.py.sap.loginC import app
from flask import render_template

from com.py.sap.util.database import init_db, engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import Flask, render_template, request, redirect, url_for, flash 
from com.py.sap.des.mod.Fase import Fase
from com.py.sap.des.fase.FaseFormulario import FaseFormulario
import flask, flask.views
import os

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
class FaseControlador(flask.views.MethodView):
    def get(self):
        return flask.render_template('fase.html')
    
""" Funcion para agregar registros a la tabla Fase""" 
@app.route('/fase/nuevafase', methods=['GET', 'POST'])
def nuevafase():
    form = FaseFormulario(request.form)
    if request.method == 'POST' and form.validate():
        init_db(db_session)
        fase = Fase(form.nro_orden.data, form.descripcion.data, 
                    form.estado.data, form.fecha_inicio.data, 
                    form.fecha_fin.data, form.id_proyecto.data)
        db_session.add(fase)
        db_session.commit()
        return redirect('/administrarfase') 
    return render_template('fase/nuevafase.html', form=form)

@app.route('/fase/editarfase', methods=['GET', 'POST'])
def editarfase():
    form = FaseFormulario(request.form)
    init_db(db_session)
    fase = db_session.query(Fase).filter_by(id=form.id.data).first()  
    if request.method == 'POST' and form.validate():
        form.populate_obj(fase)
        db_session.merge(fase)
        db_session.commit()
        return redirect('/administrarfase')
    return render_template('fase/editarfase.html', form=form)

@app.route('/fase/eliminarfase', methods=['GET', 'POST'])
def eliminarfase():
    id = request.args.get('id')
    init_db(db_session)
    fase = db_session.query(Fase).filter_by(id=id).first()  
    init_db(db_session)
    db_session.delete(fase)
    db_session.commit()
    return redirect('/administrarfase')
    
@app.route('/fase/buscarfase', methods=['GET', 'POST'])
def buscarfase():
    valor = request.args['patron']
    init_db(db_session)
    r = db_session.query(Fase).filter_by(nro_orden=valor)
    if r == None:
        return 'no existe concordancia'
    return render_template('fase/administrarfase.html', fases = r)

@app.route('/fase/administrarfase')
def administrarfase():
    init_db(db_session)
    fases = db_session.query(Fase).order_by(Fase.nro_orden)
    return render_template('fase/administrarfase.html', fases = fases)

"""Lanza un mensaje de error en caso de que la pagina solicitada no exista"""
@app.errorhandler(404)
def page_not_found(error):
    return 'Esta Pagina no existe', 404

"""Cierra la sesion de la conexion con la base de datos"""
@app.after_request
def shutdown_session(response):
    db_session.remove()
    return response


