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
from des.mod.Atributo import Atributo
from des.mod.TItemAtributo import TItemAtributo
from ges.mod.Relacion  import Relacion
from ges.mod.TipoRelacion import TipoRelacion
import flask, flask.views
from sqlalchemy.exc import DatabaseError
from UserPermission import *
import os
import datetime
import psycopg2 

UPLOAD_FOLDER = '/path/to/the/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
 
 
 
@app.route('/item/listafase', methods=['GET', 'POST'])
def listafase(): 
    """ Funcion que lista las fases en la cual se creara el item"""      
    init_db(db_session)
    fases = db_session.query(Fase).from_statement(" select * from fase where id_proyecto = "+str(session['pry'])+" and estado != 'A' order by nro_orden " )
    return render_template('item/listafase.html', fases = fases)  
    
 
    
@app.route('/item/listatipoitem', methods=['GET', 'POST'])
def listatipoitem():   
    """ Funcion que lista los tipo de items posibles del item a crear""" 
    init_db(db_session)
    tipo = db_session.query(TipoItem).from_statement(" select * from tipo_item where id_fase = "+request.args.get('id_fase')+" order by codigo " )
    global fase_global
    fase_global = request.args.get('id_fase')
    return render_template('item/listatipoitem.html', tipos = tipo)  
    
                   
 
@app.route('/item/nuevoitem', methods=['GET', 'POST'])
def nuevoitem():
    """ Funcion para agregar registros a la tabla de Item"""
    today = datetime.date.today()
    atributo = db_session.query(Atributo).join(TItemAtributo , TItemAtributo.id_atributo == Atributo.id).join(TipoItem, TipoItem.id == TItemAtributo.id_tipo_item).filter(TipoItem.id == request.args.get('id_tipo')).all()
    
    form = ItemFormulario(request.form)
    init_db(db_session)
    form.usuario.data = session['user_id']     
    
    form.version.data= 1    
    form.fecha.data= today   
    if request.method != 'POST':   
        global tipo_global
        tipo_global=  request.args.get('id_tipo') 
        
    if request.method == 'POST' and form.validate():
        try:
            atributo = db_session.query(Atributo).join(TItemAtributo , TItemAtributo.id_atributo == Atributo.id).join(TipoItem, TipoItem.id == TItemAtributo.id_tipo_item).filter(TipoItem.id == tipo_global).all()
    
            
            #f=open(form.archivo.data ,'rb')
            #fb= f.read()
            #arch = request.FILES[form.archivo.name].read()
            # open(os.path.join(UPLOAD_PATH, form.archivo.data), 'w').write(arch)
           
            # f = open(form.archivo.file, 'rb')
            #binary = f.read()
            file = request.files['file']
            #mypic = open(form.archivo.data, 'rb').read()
            #curs.execute("insert into blobs (file) values (%s)",
    
            #archivo=file(form.archivo.data,'rb').read()  
            item = Item(form.codigo.data, form.nombre.data, form.descripcion.data, 
                    form.estado.data, form.complejidad.data, form.fecha.data, form.costo.data, 
                    form.usuario.data , form.version.data, fase_global , tipo_global,  None )
            db_session.add(item)
            db_session.commit() 
            #psycopg2.Binary(form.archivo.data)  (psycopg2.Binary(file),) 
            
            #cambia el estado de la fase si este es inicial
            fase= db_session.query(Fase).filter_by(id=item.id_fase).first()  
            if fase.estado=='I':
                fase.estado='P'
                db_session.merge(fase)
                db_session.commit()   
            
            try:
                if atributo != None:
                    for atr in atributo:
                        valor =  request.form[atr.nombre]                                           
                        ia= ItemAtributo(valor, item.id, atr.id)
                        db_session.add(ia)
                        db_session.commit()
            except DatabaseError, e:
                flash('Error en la Base de Datos' + e.args[0],'error')
                return render_template('item/nuevoitem.html', form=form, att=atributo)                      
            
            session.pop('tipo_global',None)
            flash('El Item ha sido registrada con Exito','info')
            return redirect('/item/administraritem') 
        except DatabaseError, e:
                flash('Error en la Base de Datos' + e.args[0],'error')
                return render_template('item/nuevoitem.html', form=form, att=atributo)
    else:
        flash_errors(form) 
    return render_template('item/nuevoitem.html', form=form, att=atributo)



@app.route('/item/buscarItem', methods=['GET', 'POST'])
def buscarItem():
    """Funcion que permite realizar busqueda de items"""
    valor = request.args['patron']
    parametro = request.args['parametro']
    #init_db(db_session)
   
    if valor == "" : 
            administraritem()
    if parametro == 'id_fase' :
            i = db_session.query(Item).from_statement("Select it.*  from item it, fase fa ,"+ 
                        " (Select  i.codigo cod, max(i.version) vermax from item i, fase f  where i.id_fase = f.id "+
                        " and f.id_proyecto = "+str(session['pry'])+"  group by codigo order by 1 ) s "+
                        " where it.codigo = cod and it.version= vermax and it.estado != 'E' and it.id_fase = fa.id  and lower( fa.nombre)  ilike lower( '%"+valor+"%' ) order by it.codigo ").all()
    elif parametro == 'id_tipo_item':
            i = db_session.query(Item).from_statement("Select it.*  from item it, tipo_item ti, "+ 
                        " (Select  i.codigo cod, max(i.version) vermax from item i, fase f  where i.id_fase = f.id "+
                        " and f.id_proyecto = "+str(session['pry'])+"  group by codigo order by 1 ) s "+
                        " where it.codigo = cod and it.version= vermax and it.estado != 'E' and it.id_tipo_item = ti.id  and lower( ti.nombre)  ilike lower( '%"+valor+"%' ) order by it.codigo ").all()
    elif parametro == 'estado':
        if valor == 'Abierto':
            val= 'I'
        elif valor == 'En Progreso':
            val = 'P'
        elif valor == 'Resuelto':
            val= 'R'
        elif valor == 'Aprobado':
            val = 'A'
        elif valor == 'Eliminado':
            val = 'E'
        elif valor == 'Rechazado':
            val = 'Z'
        elif valor == 'Revision' :
            val = 'V'
        elif valor ==  'Bloqueado':
            val = 'B'
        i = db_session.query(Item).from_statement("Select it.*  from item it,  "+  
                        " (Select  i.codigo cod, max(i.version) vermax from item i, fase f  where i.id_fase = f.id "+
                        " and f.id_proyecto = "+str(session['pry'])+"  group by codigo order by 1 ) s "+
                        " where it.codigo = cod and it.version= vermax and it.estado != 'E' and it.estado ilike '%"+val+"%'  order by it.codigo ").all()


    else:
        i = db_session.query(Item).from_statement("Select it.*  from item it,  "+ 
                        " (Select  i.codigo cod, max(i.version) vermax from item i, fase f  where i.id_fase = f.id "+
                        " and f.id_proyecto = "+str(session['pry'])+"  group by codigo order by 1 ) s "+
                        " where it.codigo = cod and it.version= vermax and it.estado != 'E' and lower( it."+parametro+" )  ilike lower( '%"+valor+"%' ) order by it.codigo ").all()

    return render_template('item/administraritem.html', items = i)    
    valor = request.args['patron']
    #r = db_session.query(Item).filter_by(nombre=valor)
    r = db_session.query(Item).from_statement("Select it.*  from item it,  "+ 
                        " (Select  i.codigo cod, max(i.version) vermax from item i, fase f  where i.id_fase = f.id "+
                        " and f.id_proyecto = "+str(session['pry'])+"  group by codigo order by 1 ) s "+
                        " where it.codigo = cod and it.version= vermax and it.estado != 'E' and lower( it.nombre )  ilike lower( '%"+valor+"%' ) order by it.codigo  ").all()

    if r == None:
        return 'no existe concordancia'
    return render_template('item/administraritem.html', items = r)



@app.route('/item/editaritem', methods=['GET', 'POST'])
def editaritem():  
    """Funcion que permite editar un item""" 
    today = datetime.date.today()
    # init_db(db_session)      
    i = db_session.query(Item).filter_by(codigo=request.args.get('codigo')).filter_by(id=request.args.get('id')).first() 
    form = ItemEditarFormulario(request.form,i)             
    item = db_session.query(Item).filter_by(nombre=form.nombre.data).filter_by(id=request.args.get('id')).first()  
    form.usuario.data = session['user_id']  
    form.fecha.data= today     
    fase_selected= db_session.query(Fase).filter_by(id=request.args.get('fase')).first()      
    tipo_selected= db_session.query(TipoItem).filter_by(id= request.args.get('tipo') ).first()
    enlb= db_session.query(LbItem).filter_by(id_item=request.args.get('id')).first() 
    estado= request.args.get('es')    
    atributo = db_session.query(Atributo).from_statement(" select a.* from tipo_item ti , titem_atributo ta, atributo a "+
                                                        " where ti.id = ta.id_tipo_item and a.id = ta.id_atributo and ti.id=  " +str(request.args.get('tipo')) )
    
    valoresatr = db_session.query(ItemAtributo).from_statement(" select ia.* from item_atributo ia where ia.id_item= " +str(request.args.get('id')) )
             
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
        return render_template('item/editaritem.html', form=form, att=atributo, vals=valoresatr)
    
    if request.method == 'POST' and form.validate():
        init_db(db_session)
        try:   
            atributo = db_session.query(Atributo).from_statement(" select a.* from tipo_item ti , titem_atributo ta, atributo a "+
                                                        " where ti.id = ta.id_tipo_item and a.id = ta.id_atributo and ti.id=  " +str(tipo_global) )
    
            item = Item(form.codigo.data, form.nombre.data, form.descripcion.data, 
                    estado_global, form.complejidad.data, form.fecha.data, form.costo.data, 
                    form.usuario.data , form.version.data, fase_global , tipo_global , None)
            
            db_session.add(item)
            db_session.commit()
            if atributo != None:
                for atr in atributo:
                    valor =  request.form[atr.nombre]                  
                    ia= ItemAtributo(valor, item.id, atr.id)
                    db_session.add(ia)
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
            return render_template('item/editaritem.html', form=form, att=atributo, vals=valoresatr)
    else:
        flash_errors(form)
    return render_template('item/editaritem.html', form=form, att=atributo ,vals=valoresatr )



@app.route('/item/eliminaritem', methods=['GET', 'POST'])
def eliminaritem():
    """funcion que permite eliminar items"""
    today = datetime.date.today()
    try:
        id_item = request.args.get('id')
    #    init_db(db_session)
        item = db_session.query(Item).filter_by(id= id_item).first()
        atributo = db_session.query(Atributo).from_statement(" select a.* from tipo_item ti , titem_atributo ta, atributo a "+
                                                        " where ti.id = ta.id_tipo_item and a.id = ta.id_atributo and ti.id=  " +str(request.args.get('tipo')) )
    
        valoresatr = db_session.query(ItemAtributo).from_statement(" select ia.* from item_atributo ia where ia.id_item= " +str(request.args.get('id')) )
       
        if item.estado == 'A' :
            items = Item(item.codigo, item.nombre, item.descripcion, 
                     'P' , item.complejidad, today, item.costo, 
                    session['user_id']  , item.version +1 , item.id_fase , item.id_tipo_item, None )       
            #init_db(db_session)
            db_session.add(items)
            db_session.commit()
            item= items  
            if atributo != None:
                for atr in atributo:
                    for val in valoresatr:
                        if atr.id == val.id_atributo :                   
                            ia= ItemAtributo(val.valor, item.id, atr.id)
                            db_session.add(ia)
                            db_session.commit()               
            
        items = Item(item.codigo, item.nombre, item.descripcion, 
                    'E', item.complejidad, today, item.costo, 
                    session['user_id']  , item.version+1 , item.id_fase , item.id_tipo_item , None)
        
        init_db(db_session)
        db_session.add(items)
        db_session.commit() 
        if atributo != None:
            for atr in atributo:
                for val in valoresatr:
                    if atr.id == val.id_atributo :                   
                        ia= ItemAtributo(val.valor, items.id, atr.id)
                        db_session.add(ia)
                        db_session.commit()  
        return redirect('/item/administraritem')
    except DatabaseError, e:
            flash('Error en la Base de Datos' + e.args[0],'error')
            return render_template('item/administraritem.html')
     

   
@app.route('/item/listarreversionitem', methods=['GET', 'POST'])
def listarreversionitem():   
    """funcion que lista los item a escoger para la reversion"""  
    #init_db(db_session)
    item2 = db_session.query(Item).from_statement(" select * from item where codigo = '"+str(request.args.get('cod'))+"' and id != "+str(request.args.get('id'))+" order by version " )
    return render_template('item/listarreversionitem.html', items2 = item2)  
    
     
   
@app.route('/item/reversionaritem', methods=['GET', 'POST'])
def reversionaritem():  
    """funcion que permite la reversion de items"""  
    today = datetime.date.today()
    #init_db(db_session)      
    i = db_session.query(Item).filter_by(codigo=request.args.get('cod')).filter_by(id=request.args.get('id')).first() 
    atributo = db_session.query(Atributo).from_statement(" select a.* from tipo_item ti , titem_atributo ta, atributo a "+
                                                        " where ti.id = ta.id_tipo_item and a.id = ta.id_atributo and ti.id=  " +str(request.args.get('tipo')) )
    
    valoresatr = db_session.query(ItemAtributo).from_statement(" select ia.* from item_atributo ia where ia.id_item= " +str(request.args.get('id')) )
    
    form = ItemEditarFormulario(request.form,i)             
    item = db_session.query(Item).filter_by(nombre=form.nombre.data).filter_by(id=request.args.get('id')).first()  
    form.usuario.data = session['user_id']   
    fase_selected= db_session.query(Fase).filter_by(id=request.args.get('fase')).first()      
    tipo_selected= db_session.query(TipoItem).filter_by(id= request.args.get('tipo') ).first()
    estado= request.args.get('es')    
    enlb= db_session.query(LbItem).filter_by(id_item=request.args.get('id')).first() 
                
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
       # init_db(db_session)
        try:
            
            maxversionitem = db_session.query(Item.version).from_statement("select *  from item where codigo = '"+form.codigo.data+"' and version = ( "+ 
                                                                    " select max(version) from item i where i.codigo = '"+form.codigo.data+"' )" ).first()
            
            atributo = db_session.query(Atributo).from_statement(" select a.* from tipo_item ti , titem_atributo ta, atributo a "+
                                                        " where ti.id = ta.id_tipo_item and a.id = ta.id_atributo and ti.id=  " +str(tipo_global) )
    
            
            item_aux = Item(form.codigo.data, form.nombre.data, form.descripcion.data, 
                    'V', form.complejidad.data, today, form.costo.data, 
                     session['user_id']  , maxversionitem.version + 1 , fase_global , tipo_global, None )
            
            db_session.add(item_aux)
            db_session.commit()
            if atributo != None:
                for atr in atributo:
                    valor =  request.form[atr.nombre]                  
                    ia= ItemAtributo(valor, item_aux.id, atr.id)
                    db_session.add(ia)
                    db_session.commit()
            session.pop('fase_global',None)
            session.pop('tipo_global',None)
            session.pop('estado_global',None)
            
            flash('El Item ha sido Reversionado con Exito','info')
            return redirect('/item/administraritem')     
        except DatabaseError, e:
            flash('Error en la Base de Datos' + e.args[0],'error')
            return render_template('item/reversionaritem.html', form=form, att=atributo, vals=valoresatr)
    else:
        flash_errors(form)
    return render_template('item/reversionaritem.html', form=form, att=atributo, vals=valoresatr)
    


@app.route('/item/listarreviviritem', methods=['GET', 'POST'])
def listarreviviritem():   
    """funcion que lista los items a ser revividos"""
    #init_db(db_session)
    item2 = db_session.query(Item).from_statement(" select i.* from item i where i.estado = 'E' and version = (Select max(i2.version) from item i2 where i2.codigo = i.codigo ) order by i.codigo " )
    return render_template('item/listarreviviritem.html', items2 = item2)  
    
    

@app.route('/item/reviviritem', methods=['GET', 'POST'])
def reviviritem():   
    """funcion que permite revivir un item"""
    today = datetime.date.today()
    #init_db(db_session)      
    i = db_session.query(Item).filter_by(codigo=request.args.get('cod')).filter_by(id=request.args.get('id')).first() 
    form = ItemEditarFormulario(request.form,i)             
    item = db_session.query(Item).filter_by(nombre=form.nombre.data).filter_by(id=request.args.get('id')).first()  
    form.usuario.data = session['user_id']       
    fase_selected= db_session.query(Fase).filter_by(id=request.args.get('fase')).first()      
    tipo_selected= db_session.query(TipoItem).filter_by(id= request.args.get('tipo') ).first()
    estado= request.args.get('es')
    atributo = db_session.query(Atributo).from_statement(" select a.* from tipo_item ti , titem_atributo ta, atributo a "+
                                                        " where ti.id = ta.id_tipo_item and a.id = ta.id_atributo and ti.id=  " +str(request.args.get('tipo')) )
    
    valoresatr = db_session.query(ItemAtributo).from_statement(" select ia.* from item_atributo ia where ia.id_item= " +str(request.args.get('id')) )
                   
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
        #init_db(db_session)
        try:   
            item_aux = db_session.query(Item).from_statement("select * from item where codigo= '"+form.codigo.data+"' and version = "+str(form.version.data)+"-1 " ).first()
            atributo = db_session.query(Atributo).from_statement(" select a.* from tipo_item ti , titem_atributo ta, atributo a "+
                                                        " where ti.id = ta.id_tipo_item and a.id = ta.id_atributo and ti.id=  " +str(tipo_global) )
                
            item = Item(item_aux.codigo, item_aux.nombre, item_aux.descripcion, 
                    'R', item_aux.complejidad, today, item_aux.costo, 
                     session['user_id']  , form.version.data + 1 , fase_global , tipo_global, None )
            db_session.add(item)
            db_session.commit()
            if atributo != None:
                for atr in atributo:
                    valor =  request.form[atr.nombre]                  
                    ia= ItemAtributo(valor, item.id, atr.id)
                    db_session.add(ia)
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
            return render_template('item/reviviritem.html', form=form, att=atributo, vals=valoresatr)
    else:
        flash_errors(form)
    return render_template('item/reviviritem.html', form=form, att=atributo, vals=valoresatr)

       

@app.route('/item/administraritem')
def administraritem():
    """Lista los items, su ultima version """
    #init_db(db_session)
    item = db_session.query(Item).from_statement("Select it.*  from item it, "+ 
                        " (Select  i.codigo cod, max(i.version) vermax from item i, fase f  where i.id_fase = f.id "+
                        " and f.id_proyecto = "+str(session['pry'])+"  group by codigo order by 1 ) s "+
                        " where it.codigo = cod and it.version= vermax and it.estado != 'E' order by it.codigo " )
    
    return render_template('item/administraritem.html', items = item)



@app.errorhandler(404)
def page_not_found(error):
    """Lanza un mensaje de error en caso de que la pagina solicitada no exista"""
    return 'Esta Pagina no existe', 404


@app.after_request
def shutdown_session(response):
    """Cierra la sesion de la conexion con la base de datos"""
    db_session.remove()
    return response

