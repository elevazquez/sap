from loginC import app

from util.database import init_db, engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import Flask,  request, redirect, url_for, flash, session, render_template
from adm.mod.Usuario import Usuario
from des.mod.Fase import Fase
from des.mod.Item import Item
from adm.mod.Proyecto import Proyecto
from adm.mod.Recurso import Recurso
from ges.mod.LineaBase import LineaBase
from des.mod.LbItem import LbItem
from des.mod.Atributo import Atributo
from des.mod.ItemAtributo import ItemAtributo
from ges.lineaBase.LineaBaseFormulario import LineaBaseFormulario
from ges.lineaBase.LineaBaseModifFormulario import LineaBaseModifFormulario
from ges.mod.SolicitudCambio import SolicitudCambio
from ges.mod.SolicitudItem import SolicitudItem
import flask, flask.views
from sqlalchemy.exc import DatabaseError
from UserPermission import *
import os
import datetime
from ges.mod.Relacion  import Relacion
from ges.mod.TipoRelacion import TipoRelacion
from adm.mod.Permiso import Permiso

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
            
def verificarPermiso ( id_fase, permiso):
    recurso = db_session.query(Recurso).filter_by(id_fase=id_fase).first()
    if recurso != None: 
        permission = UserPermission(permiso, int(recurso.id))
        if permission.can() == False:
            return False
        else: 
            return True
    else :
        return False            
 
  
@app.route('/lineaBase/listafaselb', methods=['GET', 'POST'])
def listafaselb():   
    """ Funcion que lista las fases de la cual se escoge una para la creacion de la LB"""   
    ##init_db(db_session)    
    fases = db_session.query(Fase).from_statement(" select * from fase where id_proyecto = "+str(session['pry'])+" and estado !='I' order by nro_orden " )
    return render_template('lineaBase/listafaselb.html', fases = fases)  


    
@app.route('/lineaBase/listaitem', methods=['GET', 'POST'])
def listaitem():   
    """ Funcion que lista los items posibles a formar parte de una linea base"""     
    ##init_db(db_session)
    idfase = request.args.get('id_fase')
    if verificarPermiso(idfase, "CREAR LINEA BASE") == False:
            flash('No posee los Permisos suficientes para realizar esta Operacion','info')
            return redirect('/lineaBase/administrarlineabase') 
        
    items = db_session.query(Item).from_statement(" select * from item where id_fase = "+request.args.get('id_fase')+" and (estado = 'A' and estado != 'B') order by codigo " )
    return render_template('lineaBase/listaitem.html', items = items)  



    
@app.route('/lineaBase/agregaritems', methods=['GET', 'POST'])
def agregaritems():   
    """ Funcion que agrega a una lista los items seleccionados para formar parte de la LB""" 
    ##init_db(db_session)
    selecteditem=  request.args.get('id_item')      
    items = db_session.query(Item).from_statement(" select * from item where id_fase = "+request.args.get('id_fase')+" and (estado = 'A' and estado != 'B') order by codigo " )
    return render_template('lineaBase/listaitem.html', items = items)  
   
 


@app.route('/lineaBase/nuevalineabase', methods=['GET', 'POST'])
def nuevalineabase():
    """ Funcion para agregar registros a tabla de linea base""" 
    today = datetime.date.today()
    idfase = request.args.get('id_fase')
    recurso = db_session.query(Recurso).filter_by(id_fase = idfase).first()
    
    form =  LineaBaseFormulario(request.form)
    form.fechaCreacion.data= today
             
    items = db_session.query(Item).from_statement("Select it.*  from item it, "+ 
                        " (Select  i.codigo cod, max(i.version) vermax from item i, fase f  where i.id_fase = f.id "+
                        " and f.id_proyecto = "+str(session['pry'])+"  group by codigo order by 1 ) s "+
                        " where it.codigo = cod and it.version= vermax and (it.estado = 'A' and it.estado != 'B') and it.id_fase= "+str(request.args.get('id_fase'))+" and it.id not in (select  id_item from lb_item ) order by it.codigo " )
   
      
           
    if request.method != 'POST' :
        items = db_session.query(Item).from_statement("Select it.*  from item it, "+ 
                        " (Select  i.codigo cod, max(i.version) vermax from item i, fase f  where i.id_fase = f.id "+
                        " and f.id_proyecto = "+str(session['pry'])+"  group by codigo order by 1 ) s "+
                        " where it.codigo = cod and it.version= vermax and (it.estado = 'A' and it.estado != 'B') and it.id_fase= "+str(request.args.get('id_fase'))+" and it.id not in (select  id_item from lb_item ) order by it.codigo " )
   
        idfase = request.args.get('id_fase')
        for it in items :
            if it.id != None:
                idfase= it.id_fase
    
    
    
        if verificarPermiso(idfase, "CREAR LINEA BASE") == False:
            flash('No posee los Permisos suficientes para realizar esta Operacion','info')
            return redirect('/lineaBase/administrarlineabase') 
        
        verfase= db_session.query(Fase).filter_by(id_proyecto= session['pry']).filter_by(id=request.args.get('id_fase')).first()
        primerafase= db_session.query(Fase).from_statement("select f2.* from fase f2 where f2.nro_orden = (select min(f.nro_orden) from fase f)").first()
        
        if verfase.nro_orden != primerafase.nro_orden :   
            for it in items:  
                relac_padre = db_session.query(Relacion).filter_by(id_item_duenho= it.id).filter_by(estado='A').all()
               
                for rp in relac_padre :
                    linea= db_session.query(LbItem).join(LineaBase, LineaBase.id==LbItem.id_linea_base).filter(LbItem.id_item==rp.id_item).filter(LineaBase.estado=='V').first()
                    if linea == None:
                       
                        items = db_session.query(Item).from_statement("Select it.*  from item it, "+ 
                                                                      " (Select  i.codigo cod, max(i.version) vermax from item i, fase f  where i.id_fase = f.id "+
                                                                      " and f.id_proyecto = "+str(session['pry'])+"  group by codigo order by 1 ) s "+
                                                                      " where it.codigo = cod and it.version= vermax and (it.estado = 'A' and it.estado != 'B') and it.id_fase= "+str(request.args.get('id_fase'))+" and it.id not in (select  id_item from lb_item )  and it.id != "+str(it.id)+"  order by it.codigo " )
                    else:
                        items = db_session.query(Item).from_statement("Select it.*  from item it, "+ 
                                                                      " (Select  i.codigo cod, max(i.version) vermax from item i, fase f  where i.id_fase = f.id "+
                                                                      " and f.id_proyecto = "+str(session['pry'])+"  group by codigo order by 1 ) s "+
                                                                      " where it.codigo = cod and it.version= vermax and (it.estado = 'A' and it.estado != 'B') and it.id_fase= "+str(request.args.get('id_fase'))+" and it.id not in (select  id_item from lb_item ) order by it.codigo " )
       
    
                else:
                    items = db_session.query(Item).from_statement("Select it.*  from item it, "+ 
                        " (Select  i.codigo cod, max(i.version) vermax from item i, fase f  where i.id_fase = f.id "+
                        " and f.id_proyecto = "+str(session['pry'])+"  group by codigo order by 1 ) s "+
                        " where it.codigo = cod and it.version= vermax and (it.estado = 'A' and it.estado != 'B') and it.id_fase= "+str(request.args.get('id_fase'))+" and it.id not in (select  id_item from lb_item )  and it.id != "+str(it.id)+"  order by it.codigo " )
      
        
    if request.method == 'POST' and form.validate():                
        try:      
            
            linea = LineaBase( form.descripcion.data, form.estado.data, form.fechaCreacion.data, None)
            db_session.add(linea)
            db_session.commit()  
            multiselect= request.form.getlist('selectitem')  
            list_aux=[]
            
            
            #se cambia el estado de los items involucrados
            for it in multiselect :
                i = db_session.query(Item).filter_by(id=it).first()  
                atributo = db_session.query(Atributo).from_statement(" select a.* from tipo_item ti , titem_atributo ta, atributo a "+
                                                        " where ti.id = ta.id_tipo_item and a.id = ta.id_atributo and ti.id=  " +str(i.id_tipo_item) )
    
                valores_atr = db_session.query(ItemAtributo).from_statement(" select ia.* from item_atributo ia where ia.id_item= " +str(i.id) )
                            
                item = Item(i.codigo, i.nombre, i.descripcion, 'B', i.complejidad, today, i.costo, 
                    session['user_id']  , i.version +1 , i.id_fase , i.id_tipo_item , i.archivo)            
                db_session.add(item)         
                          
    
     
                db_session.commit()
                list_aux.append(item)
                id_fase= i.id_fase  
                # se actualizan los atributos del item si es que tienen
                if atributo != None:
                    for atr in atributo:
                        for val in valores_atr:   
                            if val.id_atributo == atr.id:                  
                                ia= ItemAtributo(val.valor, item.id, atr.id)
                                db_session.add(ia)
                                db_session.commit()       
            
                # --------------------------------------------------------------------------------------------------
                #  # si el item poseia alguna relacion,estas se recuperan y se cambia el estado de sus relaciones directas a Revision
                #---------------------------------------------------------------------------------------------------
            
                #items padres y sus relaciones
                list_item_padres = db_session.query(Item).from_statement(" select * from item where id in ( select r.id_item  from item i, relacion r "+
                                                            " where i.id = r.id_item_duenho and r.id_item_duenho= "+str(i.id)+" and r.estado = 'A' ) ")

                list_relac_padres = db_session.query(Relacion).from_statement("select * from relacion where id in  ( select r.id  from item i, relacion r "+ 
                                                               " where i.id = r.id_item_duenho and r.id_item_duenho=  "+str(i.id)+" and r.estado = 'A') ")
                #item hijos y sus relaciones
                list_item_hijos = db_session.query(Item).from_statement(" select * from item where id in ( select r.id_item_duenho   from item i, relacion r "+
                                                            " where i.id = r.id_item and r.id_item = "+str(i.id)+" and r.estado = 'A' ) ")
    
                list_relac_hijos = db_session.query(Relacion).from_statement("select * from relacion where id in  ( select r.id  from item i, relacion r "+
                                                                 " where i.id = r.id_item  and r.id_item= "+str(i.id)+" and r.estado = 'A' ) ")
                # cambios en items hijos
                if list_item_hijos != None   :                   
                        for rel_hijo in list_relac_hijos :
                            rel_hijo.estado= 'E'
                            db_session.merge(rel_hijo)
                            db_session.commit() 
                            relacion= Relacion(rel_hijo.fecha_creacion, today, rel_hijo.id_tipo_relacion, item.id, rel_hijo.id_item_duenho, 'A')
                            db_session.add(relacion)
                            db_session.commit() 
                 
                # cambios en items padres
                if list_item_padres != None     :                        
                        for rel_padre in list_relac_padres:
                            rel_padre.estado= 'E'
                            db_session.merge(rel_padre)
                            db_session.commit() 
                            relacion= Relacion(rel_padre.fecha_creacion, today, rel_padre.id_tipo_relacion, rel_padre.id_item, item.id,  'A')
                            db_session.add(relacion)
                            db_session.commit() 
           
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
    ##init_db(db_session)   
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
                        " where it.codigo = cod and it.version= vermax and (it.estado = 'A' and it.estado != 'B') and it.id_fase= "+str(item_aux.id_fase)+" and it.id not in (select  id_item from lb_item ) order by it.codigo " )
    
    idfase = item_aux.id_fase
    if verificarPermiso(idfase, "AGREGAR ITEM LINEA BASE") == False:
            flash('No posee los Permisos suficientes para realizar esta Operacion','info')
            return redirect('/lineaBase/administrarlineabase') 
           
    if request.method != 'POST':
        
        verfase= db_session.query(Fase).filter_by(id_proyecto= session['pry']).filter_by(id=item_aux.id_fase ).first()
        primerafase= db_session.query(Fase).from_statement("select f2.* from fase f2 where f2.nro_orden = (select min(f.nro_orden) from fase f)").first()
        
        if verfase.nro_orden != primerafase.nro_orden :             
           
            for it in itemsdisp: 
                relac_padre = db_session.query(Relacion).filter_by(id_item_duenho= it.id).filter_by(estado='A').all()
               
                for rp in relac_padre :
                    linea= db_session.query(LbItem).join(LineaBase, LineaBase.id==LbItem.id_linea_base).filter(LbItem.id_item==rp.id_item).filter(LineaBase.estado=='V').first()
                    if linea == None:
                     
                        itemsdisp = db_session.query(Item).from_statement("Select it.*  from item it, "+ 
                                                                      " (Select  i.codigo cod, max(i.version) vermax from item i, fase f  where i.id_fase = f.id "+
                                                                      " and f.id_proyecto = "+str(session['pry'])+"  group by codigo order by 1 ) s "+
                                                                      " where it.codigo = cod and it.version= vermax and (it.estado = 'A' and it.estado != 'B') and it.id_fase= "+str(request.args.get('id_fase'))+" and it.id not in (select  id_item from lb_item )  and it.id != "+str(it.id)+"  order by it.codigo " )
                    else:
                        itemsdisp = db_session.query(Item).from_statement("Select it.*  from item it, "+ 
                                                                      " (Select  i.codigo cod, max(i.version) vermax from item i, fase f  where i.id_fase = f.id "+
                                                                      " and f.id_proyecto = "+str(session['pry'])+"  group by codigo order by 1 ) s "+
                                                                      " where it.codigo = cod and it.version= vermax and (it.estado = 'A' and it.estado != 'B') and it.id_fase= "+str(request.args.get('id_fase'))+" and it.id not in (select  id_item from lb_item ) order by it.codigo " )
       
    
                else:
                    itemsdisp = db_session.query(Item).from_statement("Select it.*  from item it, "+ 
                        " (Select  i.codigo cod, max(i.version) vermax from item i, fase f  where i.id_fase = f.id "+
                        " and f.id_proyecto = "+str(session['pry'])+"  group by codigo order by 1 ) s "+
                        " where it.codigo = cod and it.version= vermax and (it.estado = 'A' and it.estado != 'B') and it.id_fase= "+str(request.args.get('id_fase'))+" and it.id not in (select  id_item from lb_item )  and it.id != "+str(it.id)+"  order by it.codigo " )

                        
    if request.method == 'POST' and form.validate(): 
        items=request.form.getlist('selectitem')
        try:
            list_aux=[]
            #se cambia el estado de los items a ser agregados
            for it in items :
                atri = db_session.query(Atributo).from_statement(" select at.* from tipo_item ti , titem_atributo ta, atributo at "+
                                                        " where ti.id = ta.id_tipo_item and at.id = ta.id_atributo and ti.id=  " +str(it.id_tipo_item) )
    
                valores_atr = db_session.query(ItemAtributo).from_statement(" select ia.* from item_atributo ia where ia.id_item= " +str(it.id) )
                    
                i = db_session.query(Item).filter_by(id=it).first()    
                item = Item(i.codigo, i.nombre, i.descripcion, 'B', i.complejidad, today, i.costo, 
                  session['user_id']  , i.version +1 , i.id_fase , i.id_tipo_item , i.archivo)            
                db_session.add(item)
                db_session.commit()
                list_aux.append(item)
                # se actualizan los atributos del item si es que tienen
                if atri != None :
                        for atr in atri :
                            for val in valores_atr :   
                                if val.id_atributo == atr.id :                  
                                    ia= ItemAtributo(val.valor, item.id, atr.id)
                                    db_session.add(ia)
                                    db_session.commit()   
                
                # --------------------------------------------------------------------------------------------------
                #  # si el item poseia alguna relacion,estas se recuperan y se cambia el estado de sus relaciones directas a Revision
                #---------------------------------------------------------------------------------------------------
            
                #items padres y sus relaciones
                list_item_padres = db_session.query(Item).from_statement(" select * from item where id in ( select r.id_item  from item i, relacion r "+
                                                            " where i.id = r.id_item_duenho and r.id_item_duenho= "+str(i.id)+" and r.estado = 'A' ) ")

                list_relac_padres = db_session.query(Relacion).from_statement("select * from relacion where id in  ( select r.id  from item i, relacion r "+ 
                                                               " where i.id = r.id_item_duenho and r.id_item_duenho=  "+str(i.id)+" and r.estado = 'A') ")
                #item hijos y sus relaciones
                list_item_hijos = db_session.query(Item).from_statement(" select * from item where id in ( select r.id_item_duenho   from item i, relacion r "+
                                                            " where i.id = r.id_item and r.id_item = "+str(i.id)+"  and r.estado = 'A') ")
    
                list_relac_hijos = db_session.query(Relacion).from_statement("select * from relacion where id in  ( select r.id  from item i, relacion r "+
                                                                 " where i.id = r.id_item  and r.id_item= "+str(i.id)+" and r.estado = 'A') ")
                # cambios en items hijos
                if list_item_hijos != None   :                   
                        for rel_hijo in list_relac_hijos :
                            rel_hijo.estado= 'E'
                            db_session.merge(rel_hijo)
                            db_session.commit() 
                            relacion= Relacion(rel_hijo.fecha_creacion, today, rel_hijo.id_tipo_relacion, item.id, rel_hijo.id_item_duenho, 'A')
                            db_session.add(relacion)
                            db_session.commit() 
                 
                # cambios en items padres
                if list_item_padres != None     :                      
                        for rel_padre in list_relac_padres:
                            rel_padre.estado= 'E'
                            db_session.merge(rel_padre)
                            db_session.commit() 
                            relacion= Relacion(rel_padre.fecha_creacion, today, rel_padre.id_tipo_relacion, rel_padre.id_item, item.id,  'A')
                            db_session.add(relacion)
                            db_session.commit() 
           
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
    else:
        flash_errors(form)    
    return render_template('lineaBase/agregaritem.html', form=form,  items= itemsdisp)  

    
@app.route('/lineaBase/quitaritem', methods=['GET', 'POST'])
def quitaritem():
    """ Funcion para quitar Items de una linea base""" 
    today = datetime.date.today()
    ##init_db(db_session)   
    lin = db_session.query(LineaBase).filter_by(id=request.args.get('id_linea')).first()  
   
    if  request.args.get('id_linea') == None:
        id_linea= request.form.get('id')
    else:
        id_linea=request.args.get('id_linea')
        
    estado= request.args.get('estado_linea')    
    form = LineaBaseModifFormulario(request.form,lin) 
    
    linea = db_session.query(LineaBase).filter_by(id= form.id.data).first() 
    if linea.estado == 'L':
        itemslb=  db_session.query(Item).join(LbItem, Item.id== LbItem.id_item).filter(LbItem.id_linea_base== id_linea ).filter(Item.estado=='A').all()   
    else :
        itemslb=  db_session.query(Item).join(LbItem, Item.id== LbItem.id_item).filter(LbItem.id_linea_base== id_linea ).filter(Item.estado=='B').all()   
    
    item_aux= db_session.query(Item).join(LbItem, Item.id== LbItem.id_item).filter(LbItem.id_linea_base== id_linea).first()   
     
   
    if estado == 'V':
        form.estado.data = 'Valido'
    elif estado == 'N':
        estado.data = 'No Valido'
    elif estado == 'L':
        form.estado.data = 'Liberado'
    
    idfase = item_aux.id_fase
    if verificarPermiso(idfase, "QUITAR ITEM LINEA BASE") == False:
            flash('No posee los Permisos suficientes para realizar esta Operacion','info')
            return redirect('/lineaBase/administrarlineabase') 
            
    form.fecha_creacion.data=  request.args.get('fecha_crea')        
    if request.method == 'POST' and form.validate(): 
        items=request.form.getlist('selectitem')
        try:
            list_aux=[]
            if len(itemslb) == len(items):
                flash('La linea Base no puede quedarse sin Items','info')   
                return redirect('/lineaBase/administrarlineabase')
            #se cambia el estado de los items a ser quitados de la Linea Base
            for it in items :
                atri = db_session.query(Atributo).from_statement(" select at.* from tipo_item ti , titem_atributo ta, atributo at "+
                                                        " where ti.id = ta.id_tipo_item and at.id = ta.id_atributo and ti.id=  " +str(it.id_tipo_item) )
    
                valores_atr = db_session.query(ItemAtributo).from_statement(" select ia.* from item_atributo ia where ia.id_item= " +str(it.id) )
                 
                i = db_session.query(Item).filter_by(id=it).first()    
                item = Item(i.codigo, i.nombre, i.descripcion, 'A', i.complejidad, today, i.costo, 
                  session['user_id']  , i.version +1 , i.id_fase , i.id_tipo_item , i.archivo)            
                db_session.add(item)
                db_session.commit()
                list_aux.append(i)
                # se actualizan los atributos del item si es que tienen
                if atri != None :
                        for atr in atri :
                            for val in valores_atr :   
                                if val.id_atributo == atr.id :                  
                                    ia= ItemAtributo(val.valor, item.id, atr.id)
                                    db_session.add(ia)
                                    db_session.commit()   
                # --------------------------------------------------------------------------------------------------
                #  # si el item poseia alguna relacion
                #---------------------------------------------------------------------------------------------------
            
                #items padres y sus relaciones
                list_item_padres = db_session.query(Item).from_statement(" select * from item where id in ( select r.id_item  from item i, relacion r "+
                                                            " where i.id = r.id_item_duenho and r.id_item_duenho= "+str(i.id)+" and r.estado = 'A' ) ")

                list_relac_padres = db_session.query(Relacion).from_statement("select * from relacion where id in  ( select r.id  from item i, relacion r "+ 
                                                               " where i.id = r.id_item_duenho and r.id_item_duenho=  "+str(i.id)+" and r.estado = 'A') ")
                #item hijos y sus relaciones
                list_item_hijos = db_session.query(Item).from_statement(" select * from item where id in ( select r.id_item_duenho   from item i, relacion r "+
                                                            " where i.id = r.id_item and r.id_item = "+str(i.id)+" and r.estado = 'A' ) ")
    
                list_relac_hijos = db_session.query(Relacion).from_statement("select * from relacion where id in  ( select r.id  from item i, relacion r "+
                                                                 " where i.id = r.id_item  and r.id_item= "+str(i.id)+" and r.estado = 'A') ")
                # cambios en items hijos
                if list_item_hijos != None   :                 
                        for rel_hijo in list_relac_hijos :
                            rel_hijo.estado= 'E'
                            db_session.merge(rel_hijo)
                            db_session.commit() 
                            relacion= Relacion(rel_hijo.fecha_creacion, today, rel_hijo.id_tipo_relacion, item.id, rel_hijo.id_item_duenho, 'A')
                            db_session.add(relacion)
                            db_session.commit() 
                 
                # cambios en items padres
                if list_item_padres != None     :                      
                        for rel_padre in list_relac_padres:
                            rel_padre.estado= 'E'
                            db_session.merge(rel_padre)
                            db_session.commit() 
                            relacion= Relacion(rel_padre.fecha_creacion, today, rel_padre.id_tipo_relacion, rel_padre.id_item, item.id,  'A')
                            db_session.add(relacion)
                            db_session.commit() 
           
            #se elimina el id de los item de la linea base          
            for it in list_aux:
                lin = db_session.query(LbItem).filter_by(id_item=it.id).first()  
                db_session.delete(lin)
                db_session.commit()
                 
            
            flash('Se quito el Item con Exito','info')   
            return redirect('/lineaBase/administrarlineabase')
        except DatabaseError, e:
            if e.args[0].find('duplicate key value violates unique')!=-1:
                    flash('Clave unica violada' ,'error')
            else:
                    flash('Error en la Base de Datos' + e.args[0],'error')
            return render_template('lineaBase/quitaritem.html', form=form,  items= itemslb)
    else:
        flash_errors(form)    
    return render_template('lineaBase/quitaritem.html', form=form,  items= itemslb)  

    
@app.route('/lineaBase/editarlineabase', methods=['GET', 'POST'])
def editarlineabase():
    """Funcion para buscar una Linea Base"""
    today = datetime.date.today()
    ##init_db(db_session)   
    lin = db_session.query(LineaBase).filter_by(id=request.args.get('id_linea')).first()  
   
    if  request.args.get('id_linea') == None:
        id_linea= request.form.get('id')
    else:
        id_linea=request.args.get('id_linea')
        
    estado= request.args.get('estado_linea')    
    form = LineaBaseModifFormulario(request.form,lin) 
    
    linea = db_session.query(LineaBase).filter_by(id= form.id.data).first() 
#    if linea.estado == 'L':
#        itemslb=  db_session.query(Item).join(LbItem, Item.id== LbItem.id_item).filter(LbItem.id_linea_base== id_linea ).filter(Item.estado=='A').all()   
#    else :
#        itemslb=  db_session.query(Item).join(LbItem, Item.id== LbItem.id_item).filter(LbItem.id_linea_base== id_linea ).filter(Item.estado=='B').all()   
    itemslb=  db_session.query(Item).join(LbItem, Item.id== LbItem.id_item).filter(LbItem.id_linea_base== id_linea ).all()  
    item_aux= db_session.query(Item).join(LbItem, Item.id== LbItem.id_item).filter(LbItem.id_linea_base== id_linea).first()   
     
    if estado == 'V':
        form.estado.data = 'Valido'
    elif estado == 'N':
        form.estado.data = 'No Valido'
    elif estado == 'L':
        form.estado.data = 'Liberado'
       
    form.fecha_creacion.data=  request.args.get('fecha_crea')
    
    idfase = item_aux.id_fase
    if verificarPermiso(idfase, "VER LINEA BASE") == False:
            flash('No posee los Permisos suficientes para realizar esta Operacion','info')
            return redirect('/lineaBase/administrarlineabase') 
        
    if request.method == 'POST' and form.validate():        
        try:  
            multiselect = request.form.getlist('selecitems')
            list_aux=[]
            #se cambia el estado de los items a ser agregados
            for it in multiselect : 
                atri = db_session.query(Atributo).from_statement(" select at.* from tipo_item ti , titem_atributo ta, atributo at "+
                                                        " where ti.id = ta.id_tipo_item and at.id = ta.id_atributo and ti.id=  " +str(it.id_tipo_item) )
    
                valores_atr = db_session.query(ItemAtributo).from_statement(" select ia.* from item_atributo ia where ia.id_item= " +str(it.id) )
                 
                i = db_session.query(Item).filter_by(id=it).first()    
                item = Item(i.codigo, i.nombre, i.descripcion, 'B', i.complejidad, today, i.costo, 
                    session['user_id']  , i.version +1 , i.id_fase , i.id_tipo_item , i.archivo)            
                db_session.add(item)
                db_session.commit()
                list_aux.append(item)
                # se actualizan los atributos del item si es que tienen
                if atri != None :
                        for atr in atri :
                            for val in valores_atr :   
                                if val.id_atributo == atr.id :                  
                                    ia= ItemAtributo(val.valor, item.id, atr.id)
                                    db_session.add(ia)
                                    db_session.commit()   
                # --------------------------------------------------------------------------------------------------
                #  # si el item poseia alguna relacion,n
                #---------------------------------------------------------------------------------------------------
            
                #items padres y sus relaciones
                list_item_padres = db_session.query(Item).from_statement(" select * from item where id in ( select r.id_item  from item i, relacion r "+
                                                            " where i.id = r.id_item_duenho and r.id_item_duenho= "+str(i.id)+" and r.estado = 'A' ) ")

                list_relac_padres = db_session.query(Relacion).from_statement("select * from relacion where id in  ( select r.id  from item i, relacion r "+ 
                                                               " where i.id = r.id_item_duenho and r.id_item_duenho=  "+str(i.id)+" and r.estado = 'A') ")
                #item hijos y sus relaciones
                list_item_hijos = db_session.query(Item).from_statement(" select * from item where id in ( select r.id_item_duenho   from item i, relacion r "+
                                                            " where i.id = r.id_item and r.id_item = "+str(i.id)+" and r.estado = 'A' ) ")
    
                list_relac_hijos = db_session.query(Relacion).from_statement("select * from relacion where id in  ( select r.id  from item i, relacion r "+
                                                                 " where i.id = r.id_item  and r.id_item= "+str(i.id)+" and r.estado = 'A') ")
                # cambios en items hijos
                if list_item_hijos != None   :                   
                        for rel_hijo in list_relac_hijos :
                            rel_hijo.estado= 'E'
                            db_session.merge(rel_hijo)
                            db_session.commit() 
                            relacion= Relacion(rel_hijo.fecha_creacion, today, rel_hijo.id_tipo_relacion, item.id, rel_hijo.id_item_duenho, 'A')
                            db_session.add(relacion)
                            db_session.commit() 
                 
                # cambios en items padres
                if list_item_padres != None     :                       
                        for rel_padre in list_relac_padres:
                            rel_padre.estado= 'E'
                            db_session.merge(rel_padre)
                            db_session.commit() 
                            relacion= Relacion(rel_padre.fecha_creacion, today, rel_padre.id_tipo_relacion, rel_padre.id_item, item.id,  'A')
                            db_session.add(relacion)
                            db_session.commit() 
           
            #se guarda la linea base junto con los item pertenecientes al mismo          
            for it in list_aux:
                lbit= LbItem(linea.id, it.id)
                db_session.add(lbit)
                db_session.commit()
            flash('La Linea Base se modifico con Exito','info')   
            return redirect('/lineaBase/administrarlineabase')
        except DatabaseError, e:
            if e.args[0].find('duplicate key value violates unique')!=-1:
                    flash('Clave unica violada' ,'error')
            else:
                    flash('Error en la Base de Datos' + e.args[0],'error')
            return render_template('lineaBase/editarlineabase.html', form=form, itemslb= itemslb)
    else:
        flash_errors(form)
    return render_template('lineaBase/editarlineabase.html', form=form, itemslb= itemslb)
    

@app.route('/lineaBase/buscarlineabase', methods=['GET', 'POST'])
def buscarlineabase():
    """"Funcion para buscar una linea Base"""
    valor = request.args['patron']
    parametro = request.args['parametro']
    ##init_db(db_session)
    if valor == "" : 
        administrarlineabase()
    p = db_session.query(LineaBase).from_statement("SELECT * FROM linea_base where "+parametro+" ilike '%"+valor+"%' ").all()
    return render_template('lineaBase/administrarlineabase.html', lineas = p)
    valor = request.args['patron']
    l= db_session.query(LineaBase).filter_by(descripcion=valor)
    if l == None:
        return 'no existe concordancia'
    return render_template('lineaBase/administrarlineabase.html', lineas = l)
 
   
@app.route('/lineaBase/liberarlineabase', methods=['GET', 'POST'])
def liberarlineabase():  
    """funcion que permite la liberacion de lineas base"""  
    today = datetime.date.today()
    ##init_db(db_session)   
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
        form.estado.data = 'No Valido'
    elif estado == 'L':
        form.estado.data = 'Liberado'
        
    form.fecha_creacion.data=  request.args.get('fecha_crea') 
     
    idfase = item_aux.id_fase
    if verificarPermiso(idfase, "LIBERAR LINEA BASE") == False:
            flash('No posee los Permisos suficientes para realizar esta Operacion','info')
            return redirect('/lineaBase/administrarlineabase') 
   
    versol=  db_session.query(SolicitudItem).join(SolicitudCambio , SolicitudCambio.id == SolicitudItem.id_solicitud).join(LbItem, LbItem.id_item == SolicitudItem.id_item).filter(LbItem.id_linea_base == id_linea).filter(SolicitudCambio.id_usuario ==session['user_id'] ).first()
    if versol == None:
            flash('Debe realizar una Solicitud de Cambio para Proceder','info')
            return redirect('/lineaBase/administrarlineabase')    
    else :
        versol=   db_session.query(SolicitudItem).join(SolicitudCambio , SolicitudCambio.id == SolicitudItem.id_solicitud).join(LbItem, LbItem.id_item == SolicitudItem.id_item).filter(LbItem.id_linea_base == id_linea).filter(SolicitudCambio.id_usuario ==session['user_id'] ).filter(SolicitudCambio.estado=='A').first()
        if versol == None:
            flash('La Solicitud de Cambio no ha sido Aprobada','info')
            return redirect('/lineaBase/administrarlineabase')       
         
         
    if request.method == 'POST' and form.validate():        
        try:   
            #se cambia el estado de los items a ser agregados
            itemslb=  db_session.query(Item).join(LbItem, Item.id== LbItem.id_item).filter(LbItem.id_linea_base== id_linea ).filter(Item.estado=='B').all()   
            liberarOn(itemslb, id_linea)                           
                               
            flash('La Linea Base fue liberada. Todos sus Item se encuentran Aprobados!','info')    
            return redirect('/lineaBase/administrarlineabase')
        except DatabaseError, e:
            if e.args[0].find('duplicate key value violates unique')!=-1:
                    flash('Clave unica violada' ,'error')
            else:
                    flash('Error en la Base de Datos' + e.args[0],'error')
            return render_template('lineaBase/liberarlineabase.html', form=form, itemslb= itemslb )
    else:
        flash_errors(form)
    return render_template('lineaBase/liberarlineabase.html', form=form, itemslb= itemslb )
    
    
 
def liberarOn(itemslb, id_linea):
    list_aux=[]
    list_aux2=[] 
    today = datetime.date.today()
                       
    linea = db_session.query(LineaBase).filter_by(id= id_linea).first() 
    for i in itemslb :
        #items padres y sus relaciones
        list_item_padres = db_session.query(Item).from_statement(" select * from item where id in ( select r.id_item  from item i, relacion r "+
                                                            " where i.id = r.id_item_duenho and r.id_item_duenho= "+str(i.id)+" and r.estado = 'A' ) ")

        list_relac_padres = db_session.query(Relacion).from_statement("select * from relacion where id in  ( select r.id  from item i, relacion r "+ 
                                                               " where i.id = r.id_item_duenho and r.id_item_duenho=  "+str(i.id)+" and r.estado = 'A') ")
                #item hijos y sus relaciones
        list_item_hijos = db_session.query(Item).from_statement(" select * from item where id in ( select r.id_item_duenho   from item i, relacion r "+
                                                            " where i.id = r.id_item and r.id_item = "+str(i.id)+" and r.estado = 'A' ) ")
    
        list_relac_hijos = db_session.query(Relacion).from_statement("select * from relacion where id in  ( select r.id  from item i, relacion r "+
                                                                 " where i.id = r.id_item  and r.id_item= "+str(i.id)+" and r.estado = 'A') ")
        
        i_ult= db_session.query(Item).from_statement(" Select * from item it where  it.codigo = '"+str(i.codigo)+"' AND it.version =  ( select max(i.version) from item i where i.codigo= '"+str(i.codigo)+"')").first()
        if i_ult.version == i.version :
                atri = db_session.query(Atributo).from_statement(" select at.* from tipo_item ti , titem_atributo ta, atributo at "+
                                                        " where ti.id = ta.id_tipo_item and at.id = ta.id_atributo and ti.id=  " +str(i.id_tipo_item) )
    
                valores_atr = db_session.query(ItemAtributo).from_statement(" select ia.* from item_atributo ia where ia.id_item= " +str(i.id) )
                 
                #i = db_session.query(Item).filter_by(id=it).first()    
                item = Item(i.codigo, i.nombre, i.descripcion, 'A', i.complejidad, today, i.costo, 
                    session['user_id']  , i.version + 1 , i.id_fase , i.id_tipo_item , i.archivo)            
                db_session.add(item) 
                db_session.commit()
                list_aux.append(i) #sale 
                list_aux2.append(item)#liberado 
                # se actualizan los atributos del item si es que tienen
                if atri != None :
                        for atr in atri :
                            for val in valores_atr :   
                                if val.id_atributo == atr.id :                  
                                    ia= ItemAtributo(val.valor, item.id, atr.id)
                                    db_session.add(ia)
                                    db_session.commit()  
                                    
                item_solicitud= db_session.query(SolicitudItem).filter_by(id_item= i.id).first()
                if item_solicitud != None:
                    item_solicitud.id_item= item.id
                    db_session.merge(item_solicitud)
                    db_session.commit()
                # --------------------------------------------------------------------------------------------------
                #  # si el item poseia alguna relacion
                #---------------------------------------------------------------------------------------------------
            
              
                
                # cambios en items hijos
                if list_item_hijos != None   :   
                    for hijo in list_item_hijos : 
                        linea= db_session.query(LbItem).join(LineaBase, LineaBase.id==LbItem.id_linea_base).filter(LbItem.id_item==hijo.id).filter(LineaBase.estado=='V').first()
                        if linea != None:
                            cambiar_estado(hijo, linea.id_linea_base)         
                        else:
                           
                            atri = db_session.query(Atributo).from_statement(" select at.* from tipo_item ti , titem_atributo ta, atributo at "+
                                                        " where ti.id = ta.id_tipo_item and at.id = ta.id_atributo and ti.id=  " +str(hijo.id_tipo_item) )
    
                            valores_atr = db_session.query(ItemAtributo).from_statement(" select ia.* from item_atributo ia where ia.id_item= " +str(hijo.id) )
                            
                            hijo_ult= db_session.query(Item).from_statement(" Select * from item it where  it.codigo = '"+str(hijo.codigo)+"' AND it.version =  ( select max(i.version) from item i where i.codigo= '"+str(hijo.codigo)+"')").first()
                            
                            if hijo_ult.version != hijo.version and hijo_ult.estado == 'V': 
                                    hijo2= hijo_ult
                            else :    
                                    item2 = Item(hijo.codigo, hijo.nombre, hijo.descripcion, 'V', hijo.complejidad, today, hijo.costo, 
                                            session['user_id']  , hijo.version +1 , hijo.id_fase , hijo.id_tipo_item , hijo.archivo)            
                                    db_session.add(item2)
                                    db_session.commit()  
                                    # se actualizan los atributos del item si es que tienen
                                    if atri != None :
                                        for atr in atri :
                                            for val in valores_atr :   
                                                if val.id_atributo == atr.id :                  
                                                    ia= ItemAtributo(val.valor, item2.id, atr.id)
                                                    db_session.add(ia)
                                                    db_session.commit()      
                                                                 
                                    for rel_hijo in list_relac_hijos :  
                                        rel_hijo.estado= 'E'
                                        db_session.merge(rel_hijo)
                                        db_session.commit() 
                                          
                                        rel_exis = db_session.query(Relacion).filter_by(id_item= item.id).filter_by(id_item_duenho= item2.id).first()
                                        if rel_exis == None:                                     
                                            relacion= Relacion(rel_hijo.fecha_creacion, today, rel_hijo.id_tipo_relacion, item.id, item2.id, 'A')                                        
                                            db_session.add(relacion)
                                            db_session.commit() 
                                            
                                
                # cambios en items padres
                if list_item_padres != None     :                     
                        for rel_padre in list_relac_padres:
                            rel_padre.estado= 'E'
                            db_session.merge(rel_padre)
                            db_session.commit() 
                            padre= db_session.query(Item).filter_by(id= rel_padre.id_item).first()
                            padre_ult= db_session.query(Item).from_statement(" Select * from item it where  it.codigo = '"+str(padre.codigo)+"' AND it.version =  ( select max(i.version) from item i where i.codigo = '"+str(padre.codigo)+"' )").first()                             
                            padre2 = rel_padre.id_item                         
                            if padre_ult.version != padre.version :
                                padre2 = padre_ult
                            
                            rel_exis = db_session.query(Relacion).filter_by(id_item= padre2).filter_by(id_item_duenho= item.id).first()
                            if rel_exis == None:      
                                relacion= Relacion(rel_padre.fecha_creacion, today, rel_padre.id_tipo_relacion, padre2, item.id, 'A')
                                db_session.add(relacion)
                                db_session.commit()  
    
   
    linea = db_session.query(LineaBase).filter_by(id= id_linea).first()        
    linea.estado='L'            
    linea.fecha_ruptura = today
    db_session.merge(linea)
    db_session.commit()    
            
    #se guarda lb_item  junto con los item de la lb liberada          
    for it in list_aux2:
        lbit= LbItem(linea.id, it.id)
        db_session.add(lbit)
        db_session.commit()
            
    #se elimina el id de los item de lb_item de los item antes de ser liberados         
    for it in list_aux:
        lin = db_session.query(LbItem).filter_by(id_item=it.id).first()  
        db_session.delete(lin) 
        db_session.commit()
                 
                 
    
def cambiar_estado(i, id_linea):
                list_aux=[]
                list_aux2=[]
                today = datetime.date.today()
                lb = db_session.query(LineaBase).filter_by(id= id_linea).first() 
                
                atri = db_session.query(Atributo).from_statement(" select at.* from tipo_item ti , titem_atributo ta, atributo at "+
                                                        " where ti.id = ta.id_tipo_item and at.id = ta.id_atributo and ti.id=  " +str(i.id_tipo_item) )
    
                valores_atr = db_session.query(ItemAtributo).from_statement(" select ia.* from item_atributo ia where ia.id_item= " +str(i.id) )
                
                item = Item(i.codigo, i.nombre, i.descripcion, 'V', i.complejidad, today, i.costo, 
                    session['user_id']  , i.version + 1 , i.id_fase , i.id_tipo_item , i.archivo)            
                db_session.add(item)
                db_session.commit()
                list_aux.append(i) #sale
                list_aux2.append(item)#liberado
                # se actualizan los atributos del item si es que tienen
                if atri != None :
                        for atr in atri :
                            for val in valores_atr :   
                                if val.id_atributo == atr.id :                  
                                    ia= ItemAtributo(val.valor, item.id, atr.id)
                                    db_session.add(ia)
                                    db_session.commit()   
                
                #items padres y sus relaciones
                list_item_padres = db_session.query(Item).from_statement(" select * from item where id in ( select r.id_item  from item i, relacion r "+
                                                            " where i.id = r.id_item_duenho and r.id_item_duenho= "+str(i.id)+"  ) ")

                list_relac_padres = db_session.query(Relacion).from_statement("select * from relacion where id in  ( select r.id  from item i, relacion r "+ 
                                                               " where i.id = r.id_item_duenho and r.id_item_duenho=  "+str(i.id)+"  ) ")
                #item hijos y sus relaciones
                list_item_hijos = db_session.query(Item).from_statement(" select * from item where id in ( select r.id_item_duenho   from item i, relacion r "+
                                                            " where i.id = r.id_item and r.id_item = "+str(i.id)+"  ) ")
    
                list_relac_hijos = db_session.query(Relacion).from_statement("select * from relacion where id in  ( select r.id  from item i, relacion r "+
                                                                 " where i.id = r.id_item  and r.id_item= "+str(i.id)+" ) ")
                
                # cambios en items hijos
                if list_item_hijos != None   :   
                    for hijo in list_item_hijos : 
                            lin= db_session.query(LbItem).join(LineaBase, LineaBase.id==LbItem.id_linea_base).filter(LbItem.id_item==hijo.id).filter(LineaBase.estado=='V').first()
                            if lin != None:
                                cambiar_estado(hijo, lin.id_linea_base)
                            else:    
                                atri = db_session.query(Atributo).from_statement(" select at.* from tipo_item ti , titem_atributo ta, atributo at "+
                                                        " where ti.id = ta.id_tipo_item and at.id = ta.id_atributo and ti.id=  " +str(hijo.id_tipo_item) )
    
                                valores_atr = db_session.query(ItemAtributo).from_statement(" select ia.* from item_atributo ia where ia.id_item= " +str(hijo.id) )
                                
                                item2 = Item(hijo.codigo, hijo.nombre, hijo.descripcion, 'V', hijo.complejidad, today, hijo.costo, 
                                         session['user_id']  , hijo.version +1 , hijo.id_fase , hijo.id_tipo_item , hijo.archivo)            
                                db_session.add(item2)
                                db_session.commit()  
                                # se actualizan los atributos del item si es que tienen
                                if atri != None :
                                    for atr in atri :
                                        for val in valores_atr :   
                                            if val.id_atributo == atr.id :                  
                                                ia= ItemAtributo(val.valor, item2.id, atr.id)
                                                db_session.add(ia)
                                                db_session.commit()                   
                                for rel_hijo in list_relac_hijos :
                                    rel_hijo.estado= 'E'
                                    db_session.merge(rel_hijo)
                                    db_session.commit() 
                                    rel_exis = db_session.query(Relacion).filter_by(id_item= item.id).filter_by(id_item_duenho= item2.id).first()
                                    if rel_exis == None: 
                                        relacion= Relacion(rel_hijo.fecha_creacion, today, rel_hijo.id_tipo_relacion, item.id, item2.id, 'A')
                                        db_session.add(relacion)
                                        db_session.commit() 
                          
                 
                # cambios en items padres
                if list_item_padres != None     :                     
                    for rel_padre in list_relac_padres:
                            rel_padre.estado= 'E' 
                            db_session.merge(rel_padre) 
                            db_session.commit() 
                            it_padre= db_session.query(Item).filter_by(id= rel_padre.id_item).first()                            
                            padre_ult= db_session.query(Item).from_statement(" Select * from item it where  it.codigo = '"+str(it_padre.codigo)+"' AND it.version =  ( select max(i.version) from item i where i.codigo= '"+str(it_padre.codigo)+"'  )").first()
                                                      
                            si= 'S'
                            if padre_ult.version != it_padre.version :
                                relacion= Relacion(rel_padre.fecha_creacion, today, rel_padre.id_tipo_relacion, padre_ult.id, item.id, 'A')
                                db_session.add(relacion)
                                db_session.commit() 
                                si='N'
                                
                            rel_exis = db_session.query(Relacion).filter_by(id_item= rel_padre.id_item).filter_by(id_item_duenho= item.id).first()
                            if rel_exis == None and si=='S':     
                                relacion= Relacion(rel_padre.fecha_creacion, today, rel_padre.id_tipo_relacion, rel_padre.id_item, item.id, 'A')
                                db_session.add(relacion)
                                db_session.commit() 
                            
                lb = db_session.query(LineaBase).filter_by(id= id_linea).first()      
                lb.estado='N'            
                lb.fecha_ruptura = today
                db_session.merge(lb)
                db_session.commit()     
            
                #se guarda lb_item  junto con los item de la lb NO VALIDA          
                for it in list_aux2:
                    lbit= LbItem(lb.id, it.id)
                    db_session.add(lbit)
                    db_session.commit()
            
                #se elimina el id de los item de lb_item de los item antes de ser liberados         
                for it in list_aux:
                    lin = db_session.query(LbItem).filter_by(id_item=it.id).first()  
                    db_session.delete(lin)
                    db_session.commit()
                
                 
    
        
@app.route('/lineaBase/componerlineabase', methods=['GET', 'POST'])
def componerlineabase():  
    """funcion que permite componer una lineas base liberada"""  
    today = datetime.date.today()
    ##init_db(db_session)   
    lin = db_session.query(LineaBase).filter_by(id=request.args.get('id_linea')).first()  
   
    if  request.args.get('id_linea') == None:
        id_linea= request.form.get('id')
    else:
        id_linea=request.args.get('id_linea')
        
    estado= request.args.get('estado_linea')    
    form = LineaBaseModifFormulario(request.form,lin) 
    
    linea = db_session.query(LineaBase).filter_by(id= form.id.data).first()
     
    itemslb=  db_session.query(Item).join(LbItem, Item.id== LbItem.id_item).filter(LbItem.id_linea_base== id_linea ).filter(Item.estado=='A').all()
    item_aux= db_session.query(Item).join(LbItem, Item.id== LbItem.id_item).filter(LbItem.id_linea_base== id_linea).first()   
     
    if itemslb != None:
        permitir =True
    else  :
        permitir = False        
   
    if estado == 'V':
        form.estado.data = 'Valido'
    elif estado == 'N':
        form.estado.data = 'No Valido'
    elif estado == 'L':
        form.estado.data = 'Liberado'
        
    form.fecha_creacion.data=  request.args.get('fecha_crea')  
    idfase = item_aux.id_fase
    if verificarPermiso(idfase, "COMPONER LINEA BASE") == False:
            flash('No posee los Permisos suficientes para realizar esta Operacion','info')
            return redirect('/lineaBase/administrarlineabase') 
        
    if request.method == 'POST' and form.validate():        
        try:             
            list_aux=[]
            list_aux2=[]
            #se cambia el estado de los items a ser agregados
            itemslb2=  db_session.query(Item).join(LbItem, Item.id== LbItem.id_item).filter(LbItem.id_linea_base== id_linea ).filter(Item.estado=='A').first()   
           
            itemslb=  db_session.query(Item).join(LbItem, Item.id== LbItem.id_item).filter(LbItem.id_linea_base== id_linea ).filter(Item.estado=='A').all()
    
            if itemslb2 == None:
                flash('Los Item deben estar Aprobados para componer la Linea Base','info')
                return redirect('/lineaBase/administrarlineabase')
             
            for i in itemslb :
                atri = db_session.query(Atributo).from_statement(" select at.* from tipo_item ti , titem_atributo ta, atributo at "+
                                                        " where ti.id = ta.id_tipo_item and at.id = ta.id_atributo and ti.id=  " +str(i.id_tipo_item) )
    
                valores_atr = db_session.query(ItemAtributo).from_statement(" select ia.* from item_atributo ia where ia.id_item= " +str(i.id) )
                 
                #i = db_session.query(Item).filter_by(id=it).first()    
                item = Item(i.codigo, i.nombre, i.descripcion, 'B', i.complejidad, today, i.costo, 
                    session['user_id']  , i.version + 1 , i.id_fase , i.id_tipo_item , i.archivo)            
                db_session.add(item)
                db_session.commit()
                list_aux.append(i) #sale
                list_aux2.append(item)#liberado
                # se actualizan los atributos del item si es que tienen
                if atri != None :
                        for atr in atri :
                            for val in valores_atr :   
                                if val.id_atributo == atr.id :                  
                                    ia= ItemAtributo(val.valor, item.id, atr.id)
                                    db_session.add(ia)
                                    db_session.commit()  
                # --------------------------------------------------------------------------------------------------
                #  # si el item poseia alguna relacion
                #---------------------------------------------------------------------------------------------------
            
                #items padres y sus relaciones
                list_item_padres = db_session.query(Item).from_statement(" select * from item where id in ( select r.id_item  from item i, relacion r "+
                                                            " where i.id = r.id_item_duenho and r.id_item_duenho= "+str(i.id)+" and r.estado = 'A' ) ")

                list_relac_padres = db_session.query(Relacion).from_statement("select * from relacion where id in  ( select r.id  from item i, relacion r "+ 
                                                               " where i.id = r.id_item_duenho and r.id_item_duenho=  "+str(i.id)+" and r.estado = 'A') ")
                #item hijos y sus relaciones
                list_item_hijos = db_session.query(Item).from_statement(" select * from item where id in ( select r.id_item_duenho   from item i, relacion r "+
                                                            " where i.id = r.id_item and r.id_item = "+str(i.id)+" and r.estado = 'A' ) ")
    
                list_relac_hijos = db_session.query(Relacion).from_statement("select * from relacion where id in  ( select r.id  from item i, relacion r "+
                                                                 " where i.id = r.id_item  and r.id_item= "+str(i.id)+" and r.estado = 'A') ")
                # cambios en items hijos
                if list_item_hijos != None   :                 
                        for rel_hijo in list_relac_hijos :
                            rel_hijo.estado= 'E'
                            db_session.merge(rel_hijo)
                            db_session.commit() 
                            relacion= Relacion(rel_hijo.fecha_creacion, today, rel_hijo.id_tipo_relacion, item.id, rel_hijo.id_item_duenho, 'A')
                            db_session.add(relacion)
                            db_session.commit() 
                 
                # cambios en items padres
                if list_item_padres != None     :                       
                        for rel_padre in list_relac_padres:
                            rel_padre.estado= 'E'
                            db_session.merge(rel_padre)
                            db_session.commit() 
                            relacion= Relacion(rel_padre.fecha_creacion, today, rel_padre.id_tipo_relacion, rel_padre.id_item, item.id, 'A')
                            db_session.add(relacion)
                            db_session.commit() 
            
            
            linea.estado='V'           
            db_session.merge(linea)
            db_session.commit()   
            
            #se guarda lb_item  junto con los item de la lb liberada          
            for it in list_aux2:
                lbit= LbItem(linea.id, it.id)
                db_session.add(lbit)
                db_session.commit()
            
            #se elimina el id de los item de lb_item de los item antes de ser liberados         
            for it in list_aux:
                lin = db_session.query(LbItem).filter_by(id_item=it.id).first()  
                db_session.delete(lin)
                db_session.commit()
                               
            flash('La Linea Base fue compuesta!','info')    
            return redirect('/lineaBase/administrarlineabase')
        except DatabaseError, e:
            flash('Error en la Base de Datos' + e.args[0],'error')
            return render_template('lineaBase/componerlineabase.html', form=form, itemslb= itemslb ,permitir = permitir)
    else:
        flash_errors(form)
    return render_template('lineaBase/componerlineabase.html', form=form, itemslb= itemslb, permitir= permitir )
    
    
@app.route('/lineaBase/administrarlineabase')
def administrarlineabase():
    """Funcion que lista todas las lineas Bases"""
    #init_db(db_session)
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


    
