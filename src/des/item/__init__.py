from loginC import app

from util.database import init_db, engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import Flask,  request, redirect, url_for, flash, session, render_template
from des.mod.Item import Item
from des.item.ItemFormulario import ItemFormulario
from des.item.ItemEditarFormulario import ItemEditarFormulario 
from adm.mod.Usuario import Usuario
from des.mod.Fase import Fase
from des.mod.TipoItem import TipoItem
from des.mod.LbItem import LbItem
from ges.mod.LineaBase import LineaBase
from des.mod.ItemAtributo import ItemAtributo

#from ges.mod.Relacion  import Relacion
#from ges.mod.TipoRelacion import TipoRelacion
import flask, flask.views
from sqlalchemy.exc import DatabaseError
from UserPermission import *
import os
import datetime

fase_global= None;
tipo_global = None; 
estado_global= None;

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
 
 
""" Funcion que lista las fases en la cual se creara el item"""     
@app.route('/item/listafase', methods=['GET', 'POST'])
def listafase():   
    init_db(db_session)
    fases = db_session.query(Fase).from_statement(" select * from fase where id_proyecto = "+str(session['pry'])+" order by nro_orden " )
    return render_template('item/listafase.html', fases = fases)  
    
 
""" Funcion que lista los tipo de items posibles del item a crear"""     
@app.route('/item/listatipoitem', methods=['GET', 'POST'])
def listatipoitem():   
    init_db(db_session)
    tipo = db_session.query(TipoItem).from_statement(" select * from tipo_item where id_fase = "+request.args.get('id_fase')+" order by codigo " )
    global fase_global
    fase_global = request.args.get('id_fase')
    return render_template('item/listatipoitem.html', tipos = tipo)  
    
                   
""" Funcion para agregar registros a la tabla de Item""" 
@app.route('/item/nuevoitem', methods=['GET', 'POST'])
def nuevoitem():
    today = datetime.date.today()
    form = ItemFormulario(request.form)
    init_db(db_session)    
    form.usuario.data = session['user_id']    
    #form.fase.choices= [(f.id,f.nombre) for f in db_session.query(Fase).filter_by(id_proyecto=session['pry']).order_by(Fase.nombre).all()]
    #form.tipo_item.choices=[(f.id, f.nombre) for f in db_session.query(TipoItem).filter_by(id_fase=request.args.get('id_fase')).order_by(TipoItem.nombre).all()]
    form.version.data= 1    
    form.fecha.data= today   
    if request.method != 'POST':   
        global tipo_global
        tipo_global=  request.args.get('id_tipo') 
    if request.method == 'POST' and form.validate():
        try:
#            tipo_selected = db_session.query(TipoItem).filter_by(id_fase=request.args.get('fase') ).first()
#            if tipo_selected == None:
#                flash('El Tipo de Item no corresponde a la Fase seleccionada','error')
#                return render_template('item/nuevoitem.html', form=form)
            item = Item(form.codigo.data, form.nombre.data, form.descripcion.data, 
                    form.estado.data, form.complejidad.data, form.fecha.data, form.costo.data, 
                    form.usuario.data , form.version.data, fase_global ,tipo_global )
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


"""Funcion que permite realizar busqueda de items"""
@app.route('/item/buscarItem', methods=['GET', 'POST'])
def buscarItem():
    valor = request.args['patron']
    parametro = request.args['parametro']
    init_db(db_session)
    
    if valor == "" : 
            administraritem()
    if parametro == 'id_fase' :
            i = db_session.query(Item).from_statement("SELECT i.* FROM item i, fase f where i.id_fase = f.id  and lower( f.nombre)  ilike lower( '%"+valor+"%' ) ").all()
    elif parametro == 'id_tipo_item':
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

"""Funcion que permite editar un item"""
@app.route('/item/editaritem', methods=['GET', 'POST'])
def editaritem():   
    today = datetime.date.today()
    init_db(db_session)      
    i = db_session.query(Item).filter_by(codigo=request.args.get('codigo')).filter_by(id=request.args.get('id')).first() 
    form = ItemEditarFormulario(request.form,i)             
    item = db_session.query(Item).filter_by(nombre=form.nombre.data).filter_by(id=request.args.get('id')).first()  
    form.usuario.data = session['user_id']  
    form.fecha.data= today     
    fase_selected= db_session.query(Fase).filter_by(id=request.args.get('fase')).first()      
    tipo_selected= db_session.query(TipoItem).filter_by(id= request.args.get('tipo') ).first()
    enlb= db_session.query(LbItem).filter_by(id_item=request.args.get('id')).first() 
    estado= request.args.get('es')    
               
    if request.method != 'POST':   
        form.fase.data= fase_selected.nombre  
        form.tipo_item.data= tipo_selected.nombre
        global fase_global
        fase_global = fase_selected.id
        global tipo_global
        tipo_global= tipo_selected.id
        form.version.data= form.version.data + 1 #modifica la version
        if estado == 'I':
            form.estado.data= 'Abierto'
        elif estado == 'P':
            form.estado.data = 'En Progreso'
        elif estado == 'R':
            form.estado.data = 'Resuelto'
        elif estado == 'A':
            form.estado.data = 'Aprobado'
        elif estado == 'E':
            form.estado.data = 'Eliminado'
        elif estado == 'Z':
            form.estado.data = 'Rechazado'
        elif estado == 'V':
            form.estado.data = 'Revision'
        elif estado == 'B':
            form.estado.data = 'Bloqueado'
        global estado_global
        estado_global = estado
     
#    relac = db_session.query(Relacion).from_statement("select r.* from item i,  relacion r where (r.id_item_duenho= "+item.id +" or r.id_item= "+item.id +" ) and r.id_item = i.id ").all()
#    item_relac = db_session.query(Item).from_statement("select i.* from item i,  relacion r where (r.id_item_duenho= "+item.id +" or r.id_item= "+item.id +" ) and r.id_item = i.id ").all()
    
    #verifica si puede ser modificado:
    if enlb != None and form.estado.data == 'E' :
        flash('El Item no puede ser modificado, ya que se encuebra en una Linea Base o esta Eliminado!','error')
        return render_template('item/editaritem.html', form=form)
    
    if request.method == 'POST' and form.validate():
        init_db(db_session)
        try:   
            item = Item(form.codigo.data, form.nombre.data, form.descripcion.data, 
                    estado_global, form.complejidad.data, form.fecha.data, form.costo.data, 
                    form.usuario.data , form.version.data, fase_global , tipo_global )
            
            db_session.add(item)
            db_session.commit()
            session.pop('fase_global',None)
            session.pop('tipo_global',None)
            session.pop('estado_global',None)
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


"""funcion que permite eliminar items"""
@app.route('/item/eliminaritem', methods=['GET', 'POST'])
def eliminaritem():
    today = datetime.date.today()
    try:
        id_item = request.args.get('id')
        init_db(db_session)
        item = db_session.query(Item).filter_by(id= id_item).first()
        
        if item.estado == 'A' :
            items = Item(item.codigo, item.nombre, item.descripcion, 
                     'P' , item.complejidad, today, item.costo, 
                    session['user_id']  , item.version +1 , item.id_fase , item.id_tipo_item )       
            init_db(db_session)
            db_session.add(items)
            db_session.commit()   
            item= items   
            
        items = Item(item.codigo, item.nombre, item.descripcion, 
                    'E', item.complejidad, today, item.costo, 
                    session['user_id']  , item.version+1 , item.id_fase , item.id_tipo_item )
       
        init_db(db_session)
        db_session.add(items)
        db_session.commit() 
        return redirect('/item/administraritem')
    except DatabaseError, e:
            flash('Error en la Base de Datos' + e.args[0],'error')
            return render_template('item/administraritem.html')
     

"""funcion que lista los item a escoger para la reversion"""     
@app.route('/item/listarreversionitem', methods=['GET', 'POST'])
def listarreversionitem():   
    init_db(db_session)
    item2 = db_session.query(Item).from_statement(" select * from item where codigo = '"+str(request.args.get('cod'))+"' and id != "+str(request.args.get('id'))+" order by version " )
    return render_template('item/listarreversionitem.html', items2 = item2)  
    
     
"""funcion que permite la reversion de items"""     
@app.route('/item/reversionaritem', methods=['GET', 'POST'])
def reversionaritem():  
    today = datetime.date.today()
    init_db(db_session)      
    i = db_session.query(Item).filter_by(codigo=request.args.get('cod')).filter_by(id=request.args.get('id')).first() 
    form = ItemEditarFormulario(request.form,i)             
    item = db_session.query(Item).filter_by(nombre=form.nombre.data).filter_by(id=request.args.get('id')).first()  
    form.usuario.data = session['user_id']   
    fase_selected= db_session.query(Fase).filter_by(id=request.args.get('fase')).first()      
    tipo_selected= db_session.query(TipoItem).filter_by(id= request.args.get('tipo') ).first()
    estado= request.args.get('es')    
               
    if request.method != 'POST':        
        form.fase.data= fase_selected.nombre  
        form.tipo_item.data= tipo_selected.nombre
        global fase_global
        fase_global = fase_selected.id
        global tipo_global
        tipo_global= tipo_selected.id
        if estado == 'I':
            form.estado.data= 'Abierto'
        elif estado == 'P':
            form.estado.data = 'En Progreso'
        elif estado == 'R':
            form.estado.data = 'Resuelto'
        elif estado == 'A':
            form.estado.data = 'Aprobado'
        elif estado == 'E':
            form.estado.data = 'Eliminado'
        elif estado == 'Z':
            form.estado.data = 'Rechazado'
        elif estado == 'V':
            form.estado.data = 'Revision'
        elif estado == 'B':
            form.estado.data = 'Bloqueado'
        global estado_global
        estado_global = estado

    if request.method == 'POST' and form.validate():
        init_db(db_session)
        try:
            maxversionitem = db_session.query(Item.version).from_statement("select *  from item where codigo = '"+form.codigo.data+"' and version = ( "+ 
                                                                    " select max(version) from item i where i.codigo = '"+form.codigo.data+"' )" ).first()
            
            item_aux = Item(form.codigo.data, form.nombre.data, form.descripcion.data, 
                    'R', form.complejidad.data, today, form.costo.data, 
                     session['user_id']  , maxversionitem.version + 1 , fase_global , tipo_global )
            
            db_session.add(item_aux)
            db_session.commit()
            session.pop('fase_global',None)
            session.pop('tipo_global',None)
            session.pop('estado_global',None)
            
            flash('El Item ha sido Reversionado con Exito','info')
            return redirect('/item/administraritem')     
        except DatabaseError, e:
            flash('Error en la Base de Datos' + e.args[0],'error')
            return render_template('item/reversionaritem.html', form=form)
    else:
        flash_errors(form)
    return render_template('item/reversionaritem.html', form=form)
    

"""funcion que lista los items a ser revividos"""
@app.route('/item/listarreviviritem', methods=['GET', 'POST'])
def listarreviviritem():   
    init_db(db_session)
    item2 = db_session.query(Item).from_statement(" select i.* from item i where i.estado = 'E' and version = (Select max(i2.version) from item i2 where i2.codigo = i.codigo ) order by i.codigo " )
    return render_template('item/listarreviviritem.html', items2 = item2)  
    
"""funcion que permite revivir un item"""
@app.route('/item/reviviritem', methods=['GET', 'POST'])
def reviviritem():   
    today = datetime.date.today()
    init_db(db_session)      
    i = db_session.query(Item).filter_by(codigo=request.args.get('cod')).filter_by(id=request.args.get('id')).first() 
    form = ItemEditarFormulario(request.form,i)             
    item = db_session.query(Item).filter_by(nombre=form.nombre.data).filter_by(id=request.args.get('id')).first()  
    form.usuario.data = session['user_id']       
    fase_selected= db_session.query(Fase).filter_by(id=request.args.get('fase')).first()      
    tipo_selected= db_session.query(TipoItem).filter_by(id= request.args.get('tipo') ).first()
    estado= request.args.get('es')
    
               
    if request.method != 'POST':        
        form.fase.data= fase_selected.nombre  
        form.tipo_item.data= tipo_selected.nombre
        global fase_global
        fase_global = fase_selected.id
        global tipo_global
        tipo_global= tipo_selected.id
        if estado == 'I':
            form.estado.data= 'Abierto'
        elif estado == 'P':
            form.estado.data = 'En Progreso'
        elif estado == 'R':
            form.estado.data = 'Resuelto'
        elif estado == 'A':
            form.estado.data = 'Aprobado'
        elif estado == 'E':
            form.estado.data = 'Eliminado'
        elif estado == 'Z':
            form.estado.data = 'Rechazado'
        elif estado == 'V':
            form.estado.data = 'Revision'
        elif estado == 'B':
            form.estado.data = 'Bloqueado'
        global estado_global
        estado_global = estado
     
#    relac = db_session.query(Relacion).from_statement("select r.* from item i,  relacion r where (r.id_item_duenho= "+item.id +" or r.id_item= "+item.id +" ) and r.id_item = i.id ").all()
#    item_relac = db_session.query(Item).from_statement("select i.* from item i,  relacion r where (r.id_item_duenho= "+item.id +" or r.id_item= "+item.id +" ) and r.id_item = i.id ").all()
    
    #verifica si puede ser modificado:
   
    if request.method == 'POST' and form.validate():
        init_db(db_session)
        try:   
            item_aux = db_session.query(Item).from_statement("select * from item where codigo= '"+form.codigo.data+"' and version = "+str(form.version.data)+"-1 " ).first()
            
            item = Item(item_aux.codigo, item_aux.nombre, item_aux.descripcion, 
                    'R', item_aux.complejidad, today, item_aux.costo, 
                     session['user_id']  , form.version.data + 1 , fase_global , tipo_global )
            
            db_session.add(item)
            db_session.commit()
            session.pop('fase_global',None)
            session.pop('tipo_global',None)
            session.pop('estado_global',None)
#            for it in item_relac:
#                it.estado= 'V'
#                it.version= it.version+1
#                db_session.merge(it)
#                db_session.commit()
            
            flash('El Item ha sido Revivido con Exito','info')
            return redirect('/item/administraritem')     
        except DatabaseError, e:
            flash('Error en la Base de Datos' + e.args[0],'error')
            return render_template('item/reviviritem.html', form=form)
    else:
        flash_errors(form)
    return render_template('item/reviviritem.html', form=form)

       

@app.route('/item/administraritem')
def administraritem():
    init_db(db_session)
    item = db_session.query(Item).from_statement("Select it.*  from item it, "+ 
                        " (Select  i.codigo cod, max(i.version) vermax from item i, fase f  where i.id_fase = f.id "+
                        " and f.id_proyecto = "+str(session['pry'])+"  group by codigo order by 1 ) s "+
                        " where it.codigo = cod and it.version= vermax and it.estado != 'E' " )
    
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


