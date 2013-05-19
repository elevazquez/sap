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
            
            
 
  
@app.route('/lineaBase/listafaselb', methods=['GET', 'POST'])
def listafaselb():   
    """ Funcion que lista las fases de la cual se escoge una para la creacion de la LB"""   
    init_db(db_session)
    fases = db_session.query(Fase).from_statement(" select * from fase where id_proyecto = "+str(session['pry'])+" and estado !='I' order by nro_orden " )
    return render_template('lineaBase/listafaselb.html', fases = fases)  


    
@app.route('/lineaBase/listaitem', methods=['GET', 'POST'])
def listaitem():   
    """ Funcion que lista los items posibles a formar parte de una linea base""" 
    init_db(db_session)
    items = db_session.query(Item).from_statement(" select * from item where id_fase = "+request.args.get('id_fase')+" and (estado = 'A' and estado != 'B') order by codigo " )
    return render_template('lineaBase/listaitem.html', items = items)  



    
@app.route('/lineaBase/agregaritems', methods=['GET', 'POST'])
def agregaritems():   
    """ Funcion que agrega a una lista los items seleccionados para formar parte de la LB""" 
    init_db(db_session)
    selecteditem=  request.args.get('id_item')    
    
    items = db_session.query(Item).from_statement(" select * from item where id_fase = "+request.args.get('id_fase')+" and (estado = 'A' and estado != 'B') order by codigo " )
    return render_template('lineaBase/listaitem.html', items = items)  
   
   



@app.route('/lineaBase/nuevalineabase', methods=['GET', 'POST'])
def nuevalineabase():
    """ Funcion para agregar registros a tabla de linea base""" 
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
                id_fase= i.id_fase            
            
            #se guarda la linea base junto con los item pertenecientes al mismo          
            for it in list_aux:
                #i = db_session.query(Item).from_statement("select * from item where id ="+str(it)) 
                lbit= LbItem(linea.id, it.id)
                db_session.add(lbit)
                db_session.commit()
            
            fase= db_session.query(Fase).filter_by(id=id_fase).first()  
            fase.estado='L'
            db_session.merge(fase)
            db_session.commit()   
            
            flash('La Linea Base fue creada con exito','info')            
            return redirect('/lineaBase/administrarlineabase') 
        except DatabaseError, e:
                flash('Error en la Base de Datos' + e.args[0],'error')
                return render_template('lineaBase/nuevalineabase.html',items= items, form= form )
    else:
        flash_errors(form) 
    return render_template('lineaBase/nuevalineabase.html',items= items, form= form )


@app.route('/lineaBase/agregaritem', methods=['GET', 'POST'])
def agregaritem():
    """ Funcion para asignar Items a una linea base""" 
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
        itemsdisp = db_session.query(Item).from_statement("Select it.*  from item it, "+ 
                        " (Select  i.codigo cod, max(i.version) vermax from item i, fase f  where i.id_fase = f.id "+
                        " and f.id_proyecto = "+str(session['pry'])+"  group by codigo order by 1 ) s "+
                        " where it.codigo = cod and it.version= vermax and (it.estado = 'A' and it.estado != 'B') and it.id_fase= "+str(item_aux.id_fase)+" order by it.codigo " )
       
    form.fecha_creacion.data=  request.args.get('fecha_crea')
    itemsdisp = db_session.query(Item).from_statement("Select it.*  from item it, "+ 
                        " (Select  i.codigo cod, max(i.version) vermax from item i, fase f  where i.id_fase = f.id "+
                        " and f.id_proyecto = "+str(session['pry'])+"  group by codigo order by 1 ) s "+
                        " where it.codigo = cod and it.version= vermax and (it.estado = 'A' and it.estado != 'B') and it.id_fase= "+str(item_aux.id_fase)+" order by it.codigo " )
       
    
    if request.method == 'POST':
        linea = request.form.get('id_linea')
        items=request.form.getlist('selectitem')
        try:
            list_aux=[]
            #se cambia el estado de los items a ser agregados
            for it in items :
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
     
            flash('Se agrego el Item con Exito','info')   
            return redirect('/lineaBase/administrarlineabase')
        except DatabaseError, e:
            flash('Error en la Base de Datos' + e.args[0],'error')
            return render_template('lineaBase/agregaritem.html', form=form,  items= itemsdisp)    
    return render_template('lineaBase/agregaritem.html', form=form,  items= itemsdisp)  

    
    
@app.route('/lineaBase/editarlineabase', methods=['GET', 'POST'])
def editarlineabase():
    """Funcion para buscar una Linea Base"""
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
        itemsdisp = db_session.query(Item).from_statement("Select it.*  from item it, "+ 
                        " (Select  i.codigo cod, max(i.version) vermax from item i, fase f  where i.id_fase = f.id "+
                        " and f.id_proyecto = "+str(session['pry'])+"  group by codigo order by 1 ) s "+
                        " where it.codigo = cod and it.version= vermax and (it.estado = 'A' and it.estado != 'B') and it.id_fase= "+str(item_aux.id_fase)+" order by it.codigo " )
       
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
    """"Funcion para buscar una linea Base"""
    valor = request.args['patron']
    parametro = request.args['parametro']
    init_db(db_session)
    if valor == "" : 
        p = db_session.query(LineaBase)
    else:
        p = db_session.query(LineaBase).from_statement("SELECT * FROM linea_base where "+parametro+" ilike '%"+valor+"%' ").all()
    return render_template('lineaBase/administrarlineabase.html', fases2 = p)

 
   
@app.route('/lineaBase/liberarlineabase', methods=['GET', 'POST'])
def liberarlineabase():  
    """funcion que permite la liberacion de lineas base"""  
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
           
            list_aux=[]
            #se cambia el estado de los items a ser agregados
            itemslb=  db_session.query(Item).join(LbItem, Item.id== LbItem.id_item).filter(LbItem.id_linea_base== id_linea ).filter(Item.estado=='B').all()   
   
            for i in itemslb :
                #i = db_session.query(Item).filter_by(id=it).first()    
                item = Item(i.codigo, i.nombre, i.descripcion, 'A', i.complejidad, today, i.costo, 
                    session['user_id']  , i.version + 1 , i.id_fase , i.id_tipo_item , i.archivo)            
                db_session.add(item)
                db_session.commit()
                list_aux.append(item)
             
            #se cambia el estado de la linea base a liberado
            #form.populate_obj(linea)
            
            #linea.id= form.id.data
            #linea.descripcion= form.descripcion.data
            linea.estado='L'            
            #linea.fecha_creacion= form.fecha_creacion.data
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
            return render_template('lineaBase/liberarlineabase.html', form=form, itemslb= itemslb )
    else:
        flash_errors(form)
    return render_template('lineaBase/liberarlineabase.html', form=form, itemslb= itemslb )
    
    

@app.route('/lineaBase/administrarlineabase')
def administrarlineabase():
    """Funcion que lista todas las lineas Bases"""
    init_db(db_session)
    LB = db_session.query(LineaBase).join(LbItem, LineaBase.id== LbItem.id_linea_base).join(Item, LbItem.id_item== Item.id).join(Fase,Item.id_fase ==Fase.id).filter(Fase.id_proyecto==session['pry']).all()    
    return render_template('lineaBase/administrarlineabase.html', lineas = LB)



@app.errorhandler(404)
def page_not_found(error):
    """Lanza un mensaje de error en caso de que la pagina solicitada no exista"""
    return 'Esta Pagina no existe', 404


@app.after_request
def shutdown_session(response):
    """Cierra la sesion de la conexion con la base de datos"""
    db_session.remove()
    return response


    
