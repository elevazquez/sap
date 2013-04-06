from com.py.sap.util.database import init_db, engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import Flask, render_template, request, redirect, url_for, flash
from com.py.sap.adm.mod.Rol import Rol
from com.py.sap.adm.gui.RolFormulario import RolFormulario
import flask, flask.views
import os

app = flask.Flask(__name__)
app.secret_key="sap"
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
class RolControlador(flask.views.MethodView):
    def get(self):
        return flask.render_template('rol.html')
    
""" Funcion para agregar registros a la tabla Rol""" 
@app.route('/add', methods=['GET', 'POST'])
def add():
    form = RolFormulario(request.form)
    if request.method == 'POST' and form.validate():
        init_db(db_session)
        rol = Rol(form.codigo.data, form.descripcion.data)
        db_session.add(rol)
        db_session.commit()
        print 'Rol Creado'
    return render_template('nuevorol.html', form=form)

@app.route('/editar', methods=['GET', 'POST'])
def editar():
    form = RolFormulario(request.form)
    init_db(db_session)
    rol = db_session.query(Rol).filter_by(codigo=form.codigo.data).first()  
    if request.method == 'POST' and form.validate():
        form.populate_obj(rol)
        init_db(db_session)
        db_session.dirty(rol)
        db_session.commit()
        print 'Rol Actualizado'
    return render_template('actualizarrol.html', form=form)

@app.route('/eliminar', methods=['GET', 'POST'])
def eliminar():
    #rol = request.current_user
    form = RolFormulario(request.form)
    init_db(db_session)
    rol = db_session.query(Rol).filter_by(codigo=form.codigo.data).first()  
    #form = RolFormulario(request.form, rol)
    if request.method == 'POST' and form.validate():
        form.populate_obj(rol)
        init_db(db_session)
        db_session.delete(rol)
        db_session.commit()
        print 'Rol Eliminado'
    return render_template('eliminarrol.html', form=form)

@app.route('/buscar', methods=['GET', 'POST'])
def buscar():
    valor = request.form
    #v = valor.getvalue().toString()
    init_db(db_session)
    r = db_session.query(Rol).filter_by(codigo=valor.patron.data).first()
    if r == None:
        return 'no existe concordancia'
    return '%d, %s, %s' %(r.id, r.codigo, r.descripcion)

@app.route('/listarol')
def listar():
    init_db(db_session)
    roles = db_session.query(Rol).order_by(Rol.id)
    return render_template('listarol.html', roles = roles)

"""Lanza un mensaje de error en caso de que la pagina solicitada no exista"""
@app.errorhandler(404)
def page_not_found(error):
    return 'Esta Pagina no existe', 404

"""Cierra la sesion de la conexion con la base de datos"""
@app.after_request
def shutdown_session(response):
    db_session.remove()
    return response

app.add_url_rule('/',
                 view_func= RolControlador.as_view('rol'),
                 methods=["GET","POST"])

app.debug = True
app.run()