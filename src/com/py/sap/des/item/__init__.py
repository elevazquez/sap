from com.py.sap.loginC import app

from com.py.sap.util.database import init_db, engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import Flask,  request, redirect, url_for, flash, session, render_template
from com.py.sap.des.mod.Item import Item
from com.py.sap.des.item.ItemFormulario import ItemFormulario
from com.py.sap.des.item.ItemEditarFormulario import ItemEditarFormulario 
from com.py.sap.adm.mod.Usuario import Usuario
from com.py.sap.des.mod.Fase import Fase
from com.py.sap.des.mod.TipoItem import TipoItem
#from com.py.sap.des.mod.LbItem import LbItem
#from com.py.sap.ges.mod.LineaBase import LineaBase
#from com.py.sap.ges.mod.Relacion  import Relacion
#from com.py.sap.ges.mod.TipoRelacion import TipoRelacion
import flask, flask.views
from sqlalchemy.exc import DatabaseError
from com.py.sap.UserPermission import *
import os
import datetime

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
            ),'error')
                
""" Funcion para agregar registros a la tabla de Item""" 
@app.route('/item/nuevoitem', methods=['GET', 'POST'])
def nuevoitem():
    today = datetime.date.today()
    form = ItemFormulario(request.form)
    init_db(db_session)    
    form.usuario.data = session['user_id']
    form.fase.choices= [(f.id,f.nombre) for f in db_session.query(Fase).filter_by(id_proyecto=session['pry']).order_by(Fase.nombre).all()]
    form.tipo_item.choices=[(f.id, f.nombre) for f in db_session.query(TipoItem).order_by(TipoItem.nombre).all()]
    #form.id_tipo_item.choices=  [(f.id, f.nombre) for f in db_session.query(TipoItem).filter_by(id_fase=form.id_fase.data).order_by(TipoItem.nombre).all()]
    form.version.data= 1    
    form.fecha.data= today   
    if request.method == 'POST' and form.validate():
        try:
            tipo_selected = db_session.query(TipoItem).filter_by(id_fase=form.fase.data ).first()
            if tipo_selected == None:
                flash('El Tipo de Item no corresponde a la Fase seleccionada','error')
                return render_template('item/nuevoitem.html', form=form)
            item = Item(form.codigo.data, form.nombre.data, form.descripcion.data, 
                    form.estado.data, form.complejidad.data, form.fecha.data, form.costo.data, 
                    form.usuario.data , form.version.data, form.fase.data, form.tipo_item.data )
            db_session.add(item)
            db_session.commit()
            flash('El Item ha sido registrada con Exito','info')
            return redirect('/item/administraritem') 
        except DatabaseError, e:
                flash('Error en la Base de Datos' + e.args[0],'error')
                return render_template('item/nuevoitem.html', form=form)
    else:
        flash_errors(form) 
    return render_template('item/nuevoitem.html', form=form)


@app.route('/item/buscarItem', methods=['GET', 'POST'])
def buscarItem():
    valor = request.args['patron']
    parametro = request.args['parametro']
    init_db(db_session)
    
    if valor == "" : 
            administraritem()
    if parametro == 'id_fase' :
            i = db_session.query(Item).from_statement("SELECT i.* FROM item i, fase f where i.id_fase = f.id  and lower( f.nombre)  ilike lower( '%"+valor+"%' ) ").all()
    if parametro == 'id_tipo_item':
            i = db_session.query(Item).from_statement("SELECT i.* FROM item i, tipo_item f where  i.id_tipo_item = f.id  and lower( f.nombre )  ilike lower('%"+valor+"%')").all()
    else:
            i = db_session.query(Item).from_statement("SELECT * FROM item where "+parametro+" ilike '%"+valor+"%'").all()
            return render_template('item/administraritem.html', items = i)    
    valor = request.args['patron']
    init_db(db_session)
    r = db_session.query(Item).filter_by(nombre=valor)
    if r == None:
        return 'no existe concordancia'
    return render_template('item/administraritem.html', items = r)


@app.route('/item/editaritem', methods=['GET', 'POST'])
def editaritem():
    today = datetime.date.today()
    init_db(db_session)  
    i = db_session.query(Item).filter_by(codigo=request.args.get('codigo')).filter_by(id=request.args.get('id')).first() 
    form = ItemEditarFormulario(request.form,i)        
    #item = db_session.query(Item).filter_by(codigo=form.codigo.data).first()      
    item = db_session.query(Item).filter_by(nombre=form.nombre.data).order_by(Item.version.desc()).first()  
    
    form.usuario.data = session['user_id']  
    form.fecha.data= today 
    fase_selected= db_session.query(Fase).filter_by(id=request.args.get('fase') ).first() 
    tipo_selected= db_session.query(TipoItem).filter_by(id=request.args.get('tipo') ).first()
             
    if request.method != 'POST':        
        form.fase.data= fase_selected.nombre  
        form.tipo_item.data= tipo_selected.nombre  
   # enlb= db_session.query(LbItem).filter_by(id_item=request.args.get('id')).first() 
    form.version.data= form.version.data + 1 #modifica la version
    form.fecha.data= today
#    relac = db_session.query(Relacion).from_statement("select r.* from item i,  relacion r where (r.id_item_duenho= "+item.id +" or r.id_item= "+item.id +" ) and r.id_item = i.id ").all()
#    item_relac = db_session.query(Item).from_statement("select i.* from item i,  relacion r where (r.id_item_duenho= "+item.id +" or r.id_item= "+item.id +" ) and r.id_item = i.id ").all()
    #verifica si puede ser modificado
#    if enlb == None and form.estado.data != 'E' :
#        flash('El Item no puede ser modificado, ya que se encuebra en una Linea Base o esta Eliminado!','error')
#        return render_template('item/editaritem.html', form=form)
    if request.method == 'POST' and form.validate():
        try:                    
            
            items = Item(form.codigo.data, form.nombre.data, form.descripcion.data, 
                    form.estado.data, form.complejidad.data, form.fecha.data, form.costo.data, 
                    form.usuario.data , form.version.data, form.fase.data , form.tipo_item.data  )
         
            form.populate_obj(item)            
            item.fecha = today
            db_session.add(item)
            db_session.commit()
#            for it in item_relac:
#                it.estado= 'V'
#                it.version= it.version+1
#                db_session.merge(it)
#                db_session.commit()
            
            flash('El Item ha sido modificado con Exito','info')
            return redirect('/item/administraritem')     
        except DatabaseError, e:
            flash('Error en la Base de Datos' + e.args[0],'error')
            return render_template('item/editaritem.html', form=form)
    else:
        flash_errors(form)
    return render_template('item/editaritem.html', form=form)



@app.route('/item/eliminaritem', methods=['GET', 'POST'])
def eliminaritem():
        cod = request.args.get('cod')
        init_db(db_session)    
        

@app.route('/item/administraritem')
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


