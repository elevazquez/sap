from com.py.sap.loginC import app

from com.py.sap.util.database import init_db, engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import Flask,  request, redirect, url_for, flash, session, render_template
from com.py.sap.des.mod.Item import Item
from com.py.sap.des.item.ItemFormulario import ItemFormulario
from com.py.sap.adm.mod.Usuario import Usuario
import flask, flask.views
import os

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
class ItemControlador(flask.views.MethodView):
    def get(self):
        return flask.render_template('item.html')
    
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ))
                
""" Funcion para agregar registros a la tabla Item""" 
@app.route('/nuevoitem', methods=['GET', 'POST'])
def nuevoitem():
    form = ItemFormulario(request.form)
    init_db(db_session) 
     
    if request.method == 'POST' and form.validate():
        item = Item(form.codigo.data, form.nombre.data, form.descripcion.data, 
                    form.estado.data, form.complejidad.data, form.fecha.data, form.costo.data, 
                    None, None, session['user_id'],
                    form.version.data,form.id_fase.data, form.id_tipo_item.data )
        db_session.add(item) 
        db_session.commit()
        flash('El Item ha sido registrada con exito','info')
        return redirect('/administraritem') 
    return render_template('item/nuevoitem.html', form=form)

@app.route('/administraritem')
def administraritem():
    init_db(db_session)
    item = db_session.query(Item).order_by(Item.codigo)
    return render_template('item/administraritem.html', items = item)



"""Lanza un mensaje de error en caso de que la pagina solicitada no exista"""
@app.errorhandler(404)
def page_not_found(error):
    return 'Esta Pagina no existe', 404

"""Cierra la sesion de la conexion con la base de datos"""
@app.after_request
def shutdown_session(response):
    db_session.remove()
    return response


