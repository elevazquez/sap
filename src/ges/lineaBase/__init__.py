from loginC import app

from util.database import init_db, engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import Flask,  request, redirect, url_for, flash, session, render_template
from adm.mod.Usuario import Usuario
from des.mod.Fase import Fase
from des.mod.Item import Item
from adm.mod.Proyecto import Proyecto
from ges.mod.LineaBase import LineaBase
from des.mod.LbItem import LbItem
from ges.lineaBase.LineaBaseFormulario import LineaBaseFormulario
from ges.lineaBase.LineaBaseModifFormulario import LineaBaseModifFormulario
import flask, flask.views
from sqlalchemy.exc import DatabaseError
from UserPermission import *
import os
import datetime

fase_global= None;
linea_global= None;
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
class LineaBaseControlador(flask.views.MethodView):
    def get(self):
        return flask.render_template('lineaBase.html')
    
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ),'error')
            
            
 
""" Funcion que lista las fases de la cual se escoge una para la creacion de la LB"""     
@app.route('/lineaBase/listafase', methods=['GET', 'POST'])
def listafase():   
    init_db(db_session)
    fases = db_session.query(Fase).from_statement(" select * from fase where id_proyecto = "+str(session['pry'])+" order by nro_orden " )
    return render_template('lineaBase/listafase.html', fases = fases)  


""" Funcion que lista los items posibles a formar parte de una linea base"""     
@app.route('/lineaBase/listaitem', methods=['GET', 'POST'])
def listaitem():   
    init_db(db_session)
    items = db_session.query(Item).from_statement(" select * from item where id_fase = "+request.args.get('id_fase')+" and (estado = 'A' and estado != 'B') order by codigo " )
    return render_template('lineaBase/listaitem.html', items = items)  



""" Funcion que agrega a una lista los items seleccionados para formar parte de la LB"""     
@app.route('/lineaBase/agregaritems', methods=['GET', 'POST'])
def agregaritems():   
    init_db(db_session)
    selecteditem=  request.args.get('id_item')    
    
    items = db_session.query(Item).from_statement(" select * from item where id_fase = "+request.args.get('id_fase')+" and (estado = 'A' and estado != 'B') order by codigo " )
    return render_template('lineaBase/listaitem.html', items = items)  
   
   


""" Funcion para agregar registros a tabla de linea base""" 
@app.route('/lineaBase/nuevalineabase', methods=['GET', 'POST'])
def nuevalineabase():
    today = datetime.date.today()
    form =  LineaBaseFormulario(request.form)
    form.fechaCreacion.data= today
    init_db(db_session)       
    #items = db_session.query(Item).from_statement(" select i.* from item i where i.id_fase = "+str(request.args.get('id_fase'))+" and (i.estado = 'A' and i.estado != 'B') order by i.codigo " )
     
    items = db_session.query(Item).from_statement("Select it.*  from item it, "+ 
                        " (Select  i.codigo cod, max(i.version) vermax from item i, fase f  where i.id_fase = f.id "+
                        " and f.id_proyecto = "+str(session['pry'])+"  group by codigo order by 1 ) s "+
                        " where it.codigo = cod and it.version= vermax and (it.estado = 'A' and it.estado != 'B') and it.id_fase= "+str(request.args.get('id_fase'))+" order by it.codigo " )
        
    if request.method == 'POST' and form.validate():                
        try:      
            linea = LineaBase( form.descripcion.data, form.estado.data, form.fechaCreacion.data, None)
            db_session.add(linea)
            db_session.commit()            
            #listitem= request.form['selecitems']
            multiselect = request.form.getlist('selecitems')
            list_aux=[]
            #se cambia el estado de los items involucrados
            for it in multiselect :
                i = db_session.query(Item).filter_by(id=it).first()    
                item = Item(i.codigo, i.nombre, i.descripcion, 'B', i.complejidad, today, i.costo, 
                    session['user_id']  , i.version +1 , i.id_fase , i.id_tipo_item , i.archivo)            
                db_session.add(item)
                db_session.commit()
                list_aux.append(item)            
            
            #se guarda la linea base junto con los item pertenecientes al mismo          
            for it in list_aux:
                #i = db_session.query(Item).from_statement("select * from item where id ="+str(it)) 
                lbit= LbItem(linea.id, it.id)
                db_session.add(lbit)
                db_session.commit()
                
            flash('La Linea Base fue creada con exito','info')            
            return redirect('/lineaBase/administrarlineabase') 
        except DatabaseError, e:
                flash('Error en la Base de Datos' + e.args[0],'error')
                return render_template('lineaBase/nuevalineabase.html',items= items, form= form )
    else:
        flash_errors(form) 
    return render_template('lineaBase/nuevalineabase.html',items= items, form= form )


    
@app.route('/lineaBase/editarlineabase', methods=['GET', 'POST'])
def editarlineabase():
    today = datetime.date.today()
    init_db(db_session)   
    lin = db_session.query(LineaBase).filter_by(id=request.args.get('id_linea')).first()  
   
    if  request.args.get('id_linea') == None:
        id_linea= request.form.get('id')
    else:
        id_linea=request.args.get('id_linea')
        
    estado= request.args.get('estado_linea')    
    form = LineaBaseModifFormulario(request.form,lin) 
    
    linea = db_session.query(LineaBase).filter_by(id= form.id.data).first() 
    itemslb=  db_session.query(Item).join(LbItem, Item.id== LbItem.id_item).filter(LbItem.id_linea_base== id_linea ).filter(Item.estado=='B').all()   
    item_aux= db_session.query(Item).join(LbItem, Item.id== LbItem.id_item).filter(LbItem.id_linea_base== id_linea).first()   
     
    if estado == 'V':
        form.estado.data = 'Valido'
    elif estado == 'N':
        estado.data = 'No Valido'
    elif estado == 'L':
        form.estado.data = 'Liberado'
        
    form.fecha_creacion.data=  request.args.get('fecha_crea')
    itemsdisp = db_session.query(Item).from_statement("Select it.*  from item it, "+ 
                        " (Select  i.codigo cod, max(i.version) vermax from item i, fase f  where i.id_fase = f.id "+
                        " and f.id_proyecto = "+str(session['pry'])+"  group by codigo order by 1 ) s "+
                        " where it.codigo = cod and it.version= vermax and (it.estado = 'A' and it.estado != 'B') and it.id_fase= "+str(item_aux.id_fase)+" order by it.codigo " )
       
          
    if request.method == 'POST' and form.validate():        
        try:  
            multiselect = request.form.getlist('selecitems')
            list_aux=[]
            #se cambia el estado de los items a ser agregados
            for it in multiselect :
                i = db_session.query(Item).filter_by(id=it).first()    
                item = Item(i.codigo, i.nombre, i.descripcion, 'B', i.complejidad, today, i.costo, 
                    session['user_id']  , i.version +1 , i.id_fase , i.id_tipo_item , i.archivo)            
                db_session.add(item)
                db_session.commit()
                list_aux.append(item)
                
            #se guarda la linea base junto con los item pertenecientes al mismo          
            for it in list_aux:
                lbit= LbItem(linea.id, it.id)
                db_session.add(lbit)
                db_session.commit()
            flash('La Linea Base se modifico con Exito','info')   
            return redirect('/lineaBase/administrarlineabase')
        except DatabaseError, e:
            flash('Error en la Base de Datos' + e.args[0],'error')
            return render_template('lineaBase/editarlineabase.html', form=form, itemslb= itemslb, itemsdisp= itemsdisp)
    else:
        flash_errors(form)
    return render_template('lineaBase/editarlineabase.html', form=form, itemslb= itemslb, itemsdisp=itemsdisp)
    

@app.route('/lineaBase/buscarlineabase', methods=['GET', 'POST'])
def buscarlineabase():
    valor = request.args['patron']
    parametro = request.args['parametro']
    init_db(db_session)
    if valor == "" : 
        p = db_session.query(LineaBase)
    else:
        p = db_session.query(LineaBase).from_statement("SELECT * FROM linea_base where "+parametro+" ilike '%"+valor+"%' ").all()
    return render_template('lineaBase/buscarlineabase.html', fases2 = p)

 
"""funcion que permite la liberacion de lineas base"""     
@app.route('/lineaBase/liberarlineabase', methods=['GET', 'POST'])
def liberarlineabase():  
    today = datetime.date.today()
    init_db(db_session)   
    lin = db_session.query(LineaBase).filter_by(id=request.args.get('id_linea')).first() 
    if  request.args.get('id_linea') == None:
        id_linea= request.form.get('id')
    else:
        id_linea=request.args.get('id_linea')
        
    estado= request.args.get('estado_linea')    
    form = LineaBaseModifFormulario(request.form,lin)     
    linea = db_session.query(LineaBase).filter_by(id= form.id.data).first() 
    itemslb=  db_session.query(Item).join(LbItem, Item.id== LbItem.id_item).filter(LbItem.id_linea_base== id_linea ).filter(Item.estado=='B').all()   
   
    if estado == 'V':
        form.estado.data = 'Valido'
    elif estado == 'N':
        estado.data = 'No Valido'
    elif estado == 'L':
        form.estado.data = 'Liberado'
        
    form.fecha_creacion.data=  request.args.get('fecha_crea')
    
    if request.method == 'POST' and form.validate():        
        try:  
            # multiselect = request.form.getlist('selecitems')
            list_aux=[]
            #se cambia el estado de los items a Aprobados
            for i in itemslb :
                #i = db_session.query(Item).filter_by(id=it).first()    
                item = Item(i.codigo, i.nombre, i.descripcion, 'A', i.complejidad, today, i.costo, 
                    session['user_id']  , i.version +1 , i.id_fase , i.id_tipo_item , i.archivo)            
                db_session.add(item)
                db_session.commit()
                list_aux.append(item)
                
            #se cambia el estado de la linea base a liberado
            form.populate_obj(linea)
            linea.id= form.id.data
            linea.descripcion= form.descripcion.data
            linea.estado='L'            
            linea.fecha_creacion= form.fecha_creacion.data
            db_session.merge(linea)
            db_session.commit()
           
            #se guarda la linea base junto con los item pertenecientes al mismo          
            for it in list_aux:
                lbit= LbItem(linea.id, it.id)
                db_session.add(lbit)
                db_session.commit()
                
            flash('La Linea Base fue liberada. Todos sus Item se encuentran Aprobados!','info')    
            return redirect('/lineaBase/administrarlineabase')
        except DatabaseError, e:
            flash('Error en la Base de Datos' + e.args[0],'error')
            return render_template('lineaBase/liberarlineabase.html', form=form, items= itemslb)
    else:
        flash_errors(form)
    return render_template('lineaBase/liberarlineabase.html', form=form, items= itemslb)
    
              

@app.route('/lineaBase/administrarlineabase')
def administrarlineabase():
    init_db(db_session)
    LB = db_session.query(LineaBase).join(LbItem, LineaBase.id== LbItem.id_linea_base).join(Item, LbItem.id_item== Item.id).join(Fase,Item.id_fase ==Fase.id).filter(Fase.id_proyecto==session['pry']).all()    
    return render_template('lineaBase/administrarlineabase.html', lineas = LB)


"""Lanza un mensaje de error en caso de que la pagina solicitada no exista"""
@app.errorhandler(404)
def page_not_found(error):
    return 'Esta Pagina no existe', 404

"""Cierra la sesion de la conexion con la base de datos"""
@app.after_request
def shutdown_session(response):
    db_session.remove()
    return response


    
