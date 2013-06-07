from loginC import app

from util.database import init_db, engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import Flask,  request, redirect, url_for, flash, session, render_template
from des.mod.Item import Item
from des.item.ItemFormulario import ItemFormulario
from des.item.ItemEditarFormulario import ItemEditarFormulario 
from des.item.ItemModFormulario import ItemModFormulario
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
from adm.mod.Permiso import Permiso
from ges.mod.SolicitudItem import SolicitudItem
from ges.mod.SolicitudCambio import SolicitudCambio
import flask, flask.views
from sqlalchemy.exc import DatabaseError
from UserPermission import UserPermission
import os
import datetime


UPLOAD_FOLDER = '/path/to/the/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#fase_global= None;
#tipo_global = None; 
estado_global= None;
#id_item_global= None;

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
    ##init_db(db_session)    
    fases = db_session.query(Fase).from_statement(" select * from fase where id_proyecto = "+str(session['pry'])+" and estado != 'A' order by nro_orden " )
    return render_template('item/listafase.html', fases = fases)  
    
 
    
@app.route('/item/listatipoitem', methods=['GET', 'POST'])
def listatipoitem():   
    """ Funcion que lista los tipo de items posibles del item a crear""" 
    # #init_db(db_session)
    var = "INSERTAR ITEM F" + str(request.args.get('id_fase'))
    permission = UserPermission(var, int(request.args.get('id_fase')))
    if permission.can() == False:
            flash('No Posee los permisos suficientes para Agregar un Item','info')
            return redirect('/item/administraritem') 
    tipo = db_session.query(TipoItem).from_statement(" select * from tipo_item where id_fase = "+request.args.get('id_fase')+" order by codigo " )
    #global fase_global
    #fase_global = request.args.get('id_fase')
    return render_template('item/listatipoitem.html', tipos = tipo)  
  

@app.route('/item/nuevoitem', methods=['GET', 'POST'])
def nuevoitem():
    """ Funcion para agregar registros a la tabla de Item"""
    today = datetime.date.today()  
    atributo = db_session.query(Atributo).join(TItemAtributo , TItemAtributo.id_atributo == Atributo.id).join(TipoItem, TipoItem.id == TItemAtributo.id_tipo_item).filter(TipoItem.id == request.args.get('id_tipo')).all()
    form = ItemFormulario(request.form)
    ##init_db(db_session)
    form.usuario.data = session['user_id']     
    if  request.args.get('id_tipo') == None:
        id_tipog= request.form.get('id_tipo_f')
    else:
        id_tipog=request.args.get('id_tipo')
        
    if  request.args.get('fase') == None:
        id_faseg= request.form.get('id_fase_f')
    else:
        id_faseg=request.args.get('fase')
        
    form.version.data= 1    
    form.fecha.data= today 
    form.id_tipo_f.data=id_tipog
    form.id_fase_f.data=id_faseg
    # if request.method != 'POST':   
    #     global tipo_global
    #    tipo_global=  request.args.get('id_tipo') 
        
    if request.method == 'POST' and form.validate():
        try:
            atributo = db_session.query(Atributo).join(TItemAtributo , TItemAtributo.id_atributo == Atributo.id).join(TipoItem, TipoItem.id == TItemAtributo.id_tipo_item).filter(TipoItem.id == id_tipog).all()
                
            #f=open(form.archivo.data ,'rb')
            #fb= f.read()
            #arch = request.FILES[form.archivo.name].read()
            # open(os.path.join(UPLOAD_PATH, form.archivo.data), 'w').write(arch)
           
            # f = open(form.archivo.file, 'rb')
            #binary = f.read()
            #############file = request.files['file']
            #mypic = open(form.archivo.data, 'rb').read()
            #curs.execute("insert into blobs (file) values (%s)",    
            #archivo=file(form.archivo.data,'rb').read()  
            #---------------------------------
            file = request.form.get('archivo')
            item = Item(form.codigo.data, form.nombre.data, form.descripcion.data, 
                    form.estado.data, form.complejidad.data, form.fecha.data, form.costo.data, 
                    form.usuario.data , form.version.data, id_faseg , id_tipog,  file )
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
                        valor =  request.form.get(atr.nombre)                                            
                        ia= ItemAtributo(valor, item.id, atr.id)
                        db_session.add(ia)
                        db_session.commit()
            except DatabaseError, e:
                flash('Error en la Base de Datos' + e.args[0],'error')
                return render_template('item/nuevoitem.html', form=form, att=atributo)                      
            
            #session.pop('tipo_global',None)
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
    ##init_db(db_session)
   
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
    # #init_db(db_session)      
    i = db_session.query(Item).filter_by(codigo=request.args.get('codigo')).filter_by(id=request.args.get('id')).first() 
       
    if  request.args.get('id') == None:
        id_itemg= request.form.get('id')
    else:
        id_itemg=request.args.get('id')
       
    if  request.args.get('tipo') == None:
        id_tipog= request.form.get('id_tipo_f')
    else:
        id_tipog=request.args.get('tipo')
  
    if  request.args.get('fase') == None:
        id_faseg= request.form.get('id_fase_f')
    else:
        id_faseg=request.args.get('fase')
      
    form = ItemModFormulario(request.form,i)    
    item = db_session.query(Item).filter_by(nombre=form.nombre.data).filter_by(id=id_itemg).first()  
    form.usuario.data = session['user_id']  
    form.fecha.data= today    
    # atributo=  db_session.query(Atributo).join(TItemAtributo, Atributo.id== TItemAtributo.id_atributo).filter(TipoItem.id == id_tipog ).all() 
    atributo = db_session.query(Atributo).from_statement(" select at.* from tipo_item ti , titem_atributo ta, atributo at "+
                                                        " where ti.id = ta.id_tipo_item and at.id = ta.id_atributo and ti.id=  " +str(id_tipog) )
    
    valoresatr = db_session.query(ItemAtributo).from_statement(" select ia.* from item_atributo ia where ia.id_item= " +str(id_itemg) )
    form.estado.choices = [('I', 'Abierto'), ('P', 'En Progreso'), ('R', 'Resuelto'), ('A', 'Aprobado'), 
                                          ('Z', 'Rechazado'), ('V', 'Revision')  ]     
    #estado= request.args.get('es')    
   
    if request.method != 'POST':   
        fase_selected= db_session.query(Fase).filter_by(id=id_faseg).first()      
        tipo_selected= db_session.query(TipoItem).filter_by(id= id_tipog ).first()
        form.fase.data= fase_selected.nombre  
        form.tipo_item.data= tipo_selected.nombre
        form.id_fase_f.data= id_faseg
        form.id_tipo_f.data = id_tipog
        form.version.data= form.version.data + 1 #modifica la version        
         
    #verificaciones
      
    verlb= db_session.query(LbItem).join(LineaBase, LineaBase.id==LbItem.id_linea_base).filter(LbItem.id_item==id_itemg).filter(LineaBase.estado =='V').first() 
    if verlb != None :
        flash('El Item se encuentra en una Linea Base debe Liberarla para continuar','info')
        return redirect('/item/administraritem')     
    
    verlb= db_session.query(LbItem).join(LineaBase, LineaBase.id==LbItem.id_linea_base).filter(LbItem.id_item==id_itemg).filter(LineaBase.estado =='L').first() 
    if verlb != None:
        versol=  db_session.query(SolicitudItem).join(SolicitudCambio , SolicitudCambio.id == SolicitudItem.id_solicitud).filter(SolicitudItem.id_item == id_itemg).first()
        if versol == None:
            flash('Debe realizar una Solicitud de Cambio para Proceder','info')
            return redirect('/item/administraritem')      
        else :
            versol=  db_session.query(SolicitudItem).join(SolicitudCambio , SolicitudCambio.id == SolicitudItem.id_solicitud).filter(SolicitudItem.id_item == id_itemg).filter(SolicitudCambio.estado=='A').first()
            if versol == None:
                flash('La Solicitud de Cambio no ha sido Aprobada','info')
                return redirect('/item/administraritem')     
         
    
    if item.estado == 'E' :
        flash('El Item no puede ser modificado, ya que esta Eliminado!','info')
        return redirect('/item/administraritem')     

    if request.method == 'POST' and form.validate():
        # #init_db(db_session)
        try:     
            # verifica permisos de modificacion
            if form.estado.data== 'P' or form.estado.data =='R' :
                var = "MODIFICACION ITEM F" + str(id_faseg)
                permission = UserPermission(var, int(id_faseg))
                if permission.can() == False:
                        flash('No posee los Permisos suficientes para realizar el cambio de estado','error')
                        return render_template('item/editaritem.html', form=form, att=atributo, vals=valoresatr)
                 
            if form.estado.data=='A' or form.estado.data =='Z':
                var = "APROBACION ITEM F" + str(id_faseg)
                permission = UserPermission(var, int(id_faseg))
                if permission.can() == False:
                        flash('No posee los Permisos suficientes para realizar el cambio de estado','error')
                        return render_template('item/editaritem.html', form=form, att=atributo, vals=valoresatr)
            
           
            # --------------------------------------------------------------------------------------------------
            #  # si el item posee alguna relacion, se cambia el estado de sus relaciones directas a Revision
            #---------------------------------------------------------------------------------------------------
           
            #items padres y sus relaciones
            list_item_padres = db_session.query(Item).from_statement(" select * from item where id in ( select r.id_item  from item i, relacion r "+
                                                            " where i.id = r.id_item_duenho and r.id_item_duenho= "+str(id_itemg)+" and  r.estado= 'A' ) ")

            list_relac_padres = db_session.query(Relacion).from_statement("select * from relacion where id in  ( select r.id  from item i, relacion r "+ 
                                                               " where i.id = r.id_item_duenho and r.id_item_duenho=  "+str(id_itemg)+" and  r.estado= 'A' ) ")
            #item hijos y sus relaciones
            list_item_hijos = db_session.query(Item).from_statement(" select * from item where id in ( select r.id_item_duenho   from item i, relacion r "+
                                                            " where i.id = r.id_item and r.id_item = "+str(id_itemg)+"  and  r.estado= 'A' )")
    
            list_relac_hijos = db_session.query(Relacion).from_statement("select * from relacion where id in  ( select r.id  from item i, relacion r "+
                                                                 " where i.id = r.id_item  and r.id_item= "+str(id_itemg)+" and  r.estado= 'A' )")
           
            
            #no puede ser aprobado si no tiene un acceso directo a su padre de la fase anterior
            #el padre debe ser aprobado primero
            if form.estado.data =='A': 
                for padre in list_item_padres :
                    print "padre "+str(padre)+ "  " 
                    if padre.estado != 'A' and padre.estado != 'B':
                        flash('El padre/ansestro del Item no esta Aprobado..','info')
                        return redirect('/item/administraritem')  
                if  list_item_padres == None : 
                    print "noo"
                    verfase= db_session.query(Fase).filter_by(id_proyecto= session['pry']).filter_by(id=id_faseg ).first()
                    primerafase= db_session.query(Fase).from_statement("select f2.* from fase f2 where f2.nro_orden = (select min(f.nro_orden) from fase f)").first()
                    
                    if verfase.nro_orden != primerafase.nro_orden : 
                        flash('El Item no posee un padre/ansestro..','info')
                        return redirect('/item/administraritem')  
                   
                              
            
            item = Item(form.codigo.data, form.nombre.data, form.descripcion.data, 
                    form.estado.data, form.complejidad.data, form.fecha.data, form.costo.data, 
                    form.usuario.data , form.version.data, id_faseg , id_tipog , None)
            
            db_session.add(item)
            db_session.commit()
          
            if atributo != None :
                for atr in atributo:
                    valor =  request.form.get(atr.nombre)                  
                    ia= ItemAtributo(valor, item.id, atr.id)
                    db_session.add(ia)
                    db_session.commit()
            
           
            
            # cambios en items hijos
            if list_item_hijos != None   :            
                for hijo in list_item_hijos : 
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
                        relacion= Relacion(rel_hijo.fecha_creacion, today, rel_hijo.id_tipo_relacion, item.id, item2.id, 'A')
                        db_session.add(relacion)
                        db_session.commit() 
                
            # cambios en items padres
            if list_item_padres != None     :
                for padre in list_item_padres :
#                    atri2 = db_session.query(Atributo).from_statement(" select at.* from tipo_item ti , titem_atributo ta, atributo at "+
#                                                        " where ti.id = ta.id_tipo_item and at.id = ta.id_atributo and ti.id=  " +str(padre.id_tipo_item) )
#    
#                    valores_atr2 = db_session.query(ItemAtributo).from_statement(" select ia.* from item_atributo ia where ia.id_item= " +str(padre.id) )
#                    item3 = Item(padre.codigo, padre.nombre, padre.descripcion, 'V', padre.complejidad, today, padre.costo, 
#                    session['user_id']  , padre.version +1 , padre.id_fase , padre.id_tipo_item , padre.archivo)            
#                    db_session.add(item3)
#                    db_session.commit()  
#                    # se actualizan los atributos del item si es que tienen
#                    if atri2 != None :
#                        for atr in atri2 :
#                            for val in valores_atr2 :   
#                                if val.id_atributo == atr.id :                  
#                                    ia= ItemAtributo(val.valor, item3.id, atr.id)
#                                    db_session.add(ia)
#                                    db_session.commit()   
                    for rel_padre in list_relac_padres:
                        rel_padre.estado= 'E'
                        db_session.merge(rel_padre)
                        db_session.commit() 
                        relacion= Relacion(rel_padre.fecha_creacion, today, rel_padre.id_tipo_relacion, padre.id, item.id,  'A')
                        db_session.add(relacion)
                        db_session.commit() 
            #se modifica en la lb            
            linea= db_session.query(LbItem).join(LineaBase, LineaBase.id==LbItem.id_linea_base).filter(LbItem.id_item==id_itemg).first() 
            
            if linea != None:
                lb= db_session.query(LineaBase).filterby(id= linea.id_linea_base)
                db_session.delete(linea)
                db_session.commit()
                lin = LbItem(linea.id_linea_base, item.id)
                db_session.add(lin)
                db_session.commit() 
                # si el item pasa a revision su lb pasa a un estado no valido
                if item.estado=='V':
                    lb.estado='N'
                    db_session.merge(lb)
                    db_session.commit() 
                    
                
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
        var = "ELIMINAR ITEM F" + str(request.args.get('fase'))
        permission = UserPermission(var, int(request.args.get('fase')))
        if permission.can() == False:
            flash('No posee los permisos suficientes para realizar la Operacion','info')
            return render_template('item/administraritem.html')
    
        #verificaciones      
        verlb= db_session.query(LbItem).join(LineaBase, LineaBase.id==LbItem.id_linea_base).filter(LbItem.id_item==request.args.get('id')).filter(LineaBase.estado =='V').first() 
        if verlb != None :
            flash('El Item se encuentra en una Linea Base debe Liberarla para continuar','info')
            return redirect('/item/administraritem')     
    
        verlb= db_session.query(LbItem).join(LineaBase, LineaBase.id==LbItem.id_linea_base).filter(LbItem.id_item==request.args.get('id')).filter(LineaBase.estado =='L').first() 
        if verlb != None:
            versol=  db_session.query(SolicitudItem).join(SolicitudCambio , SolicitudCambio.id == SolicitudItem.id_solicitud).filter(SolicitudItem.id_item == request.args.get('id')).first()
            if versol == None:
                flash('Debe realizar una Solicitud de Cambio para Proceder','info')
                return redirect('/item/administraritem')      
            else :
                versol=  db_session.query(SolicitudItem).join(SolicitudCambio , SolicitudCambio.id == SolicitudItem.id_solicitud).filter(SolicitudItem.id_item == request.args.get('id')).filter(SolicitudCambio.estado=='A').first()
                if versol == None:
                    flash('La Solicitud de Cambio no ha sido Aprobada','info')
                    return redirect('/item/administraritem')    
                
        id_item = request.args.get('id')
    #    #init_db(db_session)
        item = db_session.query(Item).filter_by(id= id_item).first()
        atributo = db_session.query(Atributo).from_statement(" select a.* from tipo_item ti , titem_atributo ta, atributo a "+
                                                        " where ti.id = ta.id_tipo_item and a.id = ta.id_atributo and ti.id=  " +str(request.args.get('tipo')) )
    
        valoresatr = db_session.query(ItemAtributo).from_statement(" select ia.* from item_atributo ia where ia.id_item= " +str(request.args.get('id')) )
        # --------------------------------------------------------------------------------------------------
        #  se obtienen las relaciones del item, si hubieran para su posterior eliminacion
        #---------------------------------------------------------------------------------------------------
            
        #items padres y sus relaciones
        list_item_padres = db_session.query(Item).from_statement(" select * from item where id in ( select r.id_item  from item i, relacion r "+
                                                           " where i.id = r.id_item_duenho and r.id_item_duenho= "+str(id_item)+" and  r.estado= 'A' )  ")

        list_relac_padres = db_session.query(Relacion).from_statement("select * from relacion where id in  ( select r.id  from item i, relacion r "+ 
                                                               " where i.id = r.id_item_duenho and r.id_item_duenho=  "+str(id_item)+" and  r.estado= 'A' ) ")
        #item hijos y sus relaciones
        list_item_hijos = db_session.query(Item).from_statement(" select * from item where id in ( select r.id_item_duenho   from item i, relacion r "+
                                                            " where i.id = r.id_item and r.id_item = "+str(id_item)+" and  r.estado= 'A' ) ")
    
        list_relac_hijos = db_session.query(Relacion).from_statement("select * from relacion where id in  ( select r.id  from item i, relacion r "+
                                                                 " where i.id = r.id_item  and r.id_item= "+str(id_item)+" and  r.estado= 'A' ) ")
           
        
        if item.estado == 'A' :
            items = Item(item.codigo, item.nombre, item.descripcion, 
                     'P' , item.complejidad, today, item.costo, 
                    session['user_id']  , item.version +1 , item.id_fase , item.id_tipo_item, None )       
            ##init_db(db_session)
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
            # cambios en items hijos
            if list_item_hijos != None   :            
                for hijo in list_item_hijos : 
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
                        relacion= Relacion(rel_hijo.fecha_creacion, today, rel_hijo.id_tipo_relacion, item.id, item2.id, 'A')
                        db_session.add(relacion)
                        db_session.commit() 
                 
            # cambios en items padres
            if list_item_padres != None     :
                for padre in list_item_padres :
#                    atri2 = db_session.query(Atributo).from_statement(" select at.* from tipo_item ti , titem_atributo ta, atributo at "+
#                                                        " where ti.id = ta.id_tipo_item and at.id = ta.id_atributo and ti.id=  " +str(padre.id_tipo_item) )
#    
#                    valores_atr2 = db_session.query(ItemAtributo).from_statement(" select ia.* from item_atributo ia where ia.id_item= " +str(padre.id) )
#                    item3 = Item(padre.codigo, padre.nombre, padre.descripcion, 'V', padre.complejidad, today, padre.costo, 
#                    session['user_id']  , padre.version +1 , padre.id_fase , padre.id_tipo_item , padre.archivo)            
#                    db_session.add(item3)
#                    db_session.commit()  
#                    # se actualizan los atributos del item si es que tienen
#                    if atri2 != None :
#                        for atr in atri2 :
#                            for val in valores_atr2 :   
#                                if val.id_atributo == atr.id :                  
#                                    ia= ItemAtributo(val.valor, item3.id, atr.id)
#                                    db_session.add(ia)
#                                    db_session.commit()   
                    for rel_padre in list_relac_padres:
                        rel_padre.estado= 'E'
                        db_session.merge(rel_padre)
                        db_session.commit() 
                        relacion= Relacion(rel_padre.fecha_creacion, today, rel_padre.id_tipo_relacion, padre.id, item.id,  'A')
                        db_session.add(relacion)
                        db_session.commit()    
            flash('El Item ha sufrido el cambio de estado Aprobado a En Progreso. Puede proceder con la Eliminacion','info')
            return redirect('/item/administraritem')      
                    
            
        items = Item(item.codigo, item.nombre, item.descripcion, 
                    'E', item.complejidad, today, item.costo, 
                    session['user_id']  , item.version+1 , item.id_fase , item.id_tipo_item , None)
        
        #init_db(db_session)
        db_session.add(items)
        db_session.commit() 
        if atributo != None:
            for atr in atributo:
                for val in valoresatr: 
                    if atr.id == val.id_atributo :                   
                        ia= ItemAtributo(val.valor, items.id, atr.id)
                        db_session.add(ia)
                        db_session.commit()  
        # cambios en items hijos
        if list_item_hijos != None   :            
                for hijo in list_item_hijos : 
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
                            relacion = db_session.query(Relacion).filter_by(id=rel_hijo.id).first()
                            relacion.estado='E'
                            db_session.merge(relacion)
                            db_session.commit()
                       
                 
        # cambios en items padres
        if list_item_padres != None     :
#                for padre in list_item_padres :
#                    atri2 = db_session.query(Atributo).from_statement(" select at.* from tipo_item ti , titem_atributo ta, atributo at "+
#                                                        " where ti.id = ta.id_tipo_item and at.id = ta.id_atributo and ti.id=  " +str(padre.id_tipo_item) )
#    
#                    valores_atr2 = db_session.query(ItemAtributo).from_statement(" select ia.* from item_atributo ia where ia.id_item= " +str(padre.id) )
#                    item3 = Item(padre.codigo, padre.nombre, padre.descripcion, 'V', padre.complejidad, today, padre.costo, 
#                    session['user_id']  , padre.version +1 , padre.id_fase , padre.id_tipo_item , padre.archivo)            
#                    db_session.add(item3)
#                    db_session.commit()  
#                    # se actualizan los atributos del item si es que tienen
#                    if atri2 != None :
#                        for atr in atri2 :
#                            for val in valores_atr2 :   
#                                if val.id_atributo == atr.id :                  
#                                    ia= ItemAtributo(val.valor, item3.id, atr.id)
#                                    db_session.add(ia)
#                                    db_session.commit()   
                    for rel_padre in list_relac_padres:
                            relacion = db_session.query(Relacion).filter_by(id=rel_padre.id).first()
                            relacion.estado='E'
                            db_session.merge(relacion)
                            db_session.commit()
        #se elimina el item de la lb
        linea= db_session.query(LbItem).join(LineaBase, LineaBase.id==LbItem.id_linea_base).filter(LbItem.id_item==id_item).first() 
        if linea != None:
            db_session.delete(linea)
            db_session.commit()
        flash('El Item se ha Eliminado con Exito','info')
        return redirect('/item/administraritem')   
    except DatabaseError, e:
            flash('Error en la Base de Datos' + e.args[0],'error')
            return render_template('item/administraritem.html')
     

   
@app.route('/item/listarreversionitem', methods=['GET', 'POST'])
def listarreversionitem():   
    """funcion que lista los item a escoger para la reversion"""  
    ##init_db(db_session)
    item2 = db_session.query(Item).from_statement(" select * from item where codigo = '"+str(request.args.get('cod'))+"' and id != "+str(request.args.get('id'))+" order by version " )
    return render_template('item/listarreversionitem.html', items2 = item2)  
    
     
   
@app.route('/item/reversionaritem', methods=['GET', 'POST'])
def reversionaritem():  
    """funcion que permite la reversion de items"""  
    today = datetime.date.today()
    ##init_db(db_session)      
   
    i = db_session.query(Item).filter_by(codigo=request.args.get('cod')).filter_by(id=request.args.get('id')).first() 
    if  request.args.get('id') == None:
        id_itemg= request.form.get('id')
    else:
        id_itemg=request.args.get('id')
        
    if  request.args.get('tipo') == None:
        id_tipog= request.form.get('id_tipo_f')
    else:
        id_tipog=request.args.get('tipo')
    
    if  request.args.get('fase') == None:
        id_faseg= request.form.get('id_fase_f')
    else:
        id_faseg=request.args.get('fase')
     
    var = "MODIFICACION ITEM F" + str(id_faseg)
    permission = UserPermission(var, int(id_faseg))
    if permission.can() == False:
            flash('No posee los Permisos suficientes para realizar esta Operacion','error')
            return redirect('/item/administraritem')   
    
    #verificaciones      
    verlb= db_session.query(LbItem).join(LineaBase, LineaBase.id==LbItem.id_linea_base).filter(LbItem.id_item==id_itemg).filter(LineaBase.estado =='V').first() 
    if verlb != None :
        flash('El Item se encuentra en una Linea Base debe Liberarla para continuar','info')
        return redirect('/item/administraritem')     
    
    verlb= db_session.query(LbItem).join(LineaBase, LineaBase.id==LbItem.id_linea_base).filter(LbItem.id_item==id_itemg).filter(LineaBase.estado =='L').first() 
    if verlb != None:
        versol=  db_session.query(SolicitudItem).join(SolicitudCambio , SolicitudCambio.id == SolicitudItem.id_solicitud).filter(SolicitudItem.id_item == id_itemg).first()
        if versol == None:
            flash('Debe realizar una Solicitud de Cambio para Proceder','info')
            return redirect('/item/administraritem')      
        else :
            versol=  db_session.query(SolicitudItem).join(SolicitudCambio , SolicitudCambio.id == SolicitudItem.id_solicitud).filter(SolicitudItem.id_item == id_itemg).filter(SolicitudCambio.estado=='A').first()
            if versol == None:
                flash('La Solicitud de Cambio no ha sido Aprobada','info')
                return redirect('/item/administraritem')     
         
                   
    form = ItemEditarFormulario(request.form,i)             
    item = db_session.query(Item).filter_by(nombre=form.nombre.data).filter_by(id=id_itemg).first()  
    form.usuario.data = session['user_id']       
    estado= request.args.get('es')  
    if request.method != 'POST':        
        fase_selected= db_session.query(Fase).filter_by(id=id_faseg).first()      
        tipo_selected= db_session.query(TipoItem).filter_by(id= id_tipog ).first()
        form.fase.data= fase_selected.nombre  
        form.tipo_item.data= tipo_selected.nombre
        form.id_fase_f.data= id_faseg
        form.id_tipo_f.data = id_tipog
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
        
    #atributo=  db_session.query(Atributo).join(TItemAtributo, Atributo.id== TItemAtributo.id_atributo).filter(TipoItem.id == id_tipog ).all() 
    atributo = db_session.query(Atributo).from_statement(" select at.* from tipo_item ti , titem_atributo ta, atributo at "+
                                                        " where ti.id = ta.id_tipo_item and at.id = ta.id_atributo and ti.id=  " +str(id_tipog) )
   
    valoresatr = db_session.query(ItemAtributo).from_statement(" select ia.* from item_atributo ia where ia.id_item= " +str(id_itemg) )
   
                    
    if request.method == 'POST' and form.validate():
        # #init_db(db_session)
        try:            
            
            maxversionitem = db_session.query(Item).from_statement("select *  from item where codigo = '"+form.codigo.data+"' and version = ( "+ 
                                                                    " select max(version) from item i where i.codigo = '"+form.codigo.data+"' )" ).first()
            
            item_aux = Item(form.codigo.data, form.nombre.data, form.descripcion.data, 
                    'V', form.complejidad.data, today, form.costo.data, 
                     session['user_id']  , maxversionitem.version + 1 , id_faseg , id_tipog, item.archivo)            
            db_session.add(item_aux)
            db_session.commit()
            if atributo != None:
                for atr in atributo:
                    for val in valoresatr:
                        if atr.id == val.id_atributo:
                            #valor =  request.form.get(atr.nomre)               
                            ia= ItemAtributo(val.valor, item_aux.id, atr.id)
                            db_session.add(ia)
                            db_session.commit()
                     
            
            # --------------------------------------------------------------------------------------------------
            #  # si el item poseia alguna relacion,estas se recuperan y se cambia el estado de sus relaciones directas a Revision
            #---------------------------------------------------------------------------------------------------
            
            #items padres y sus relaciones
            list_item_padres = db_session.query(Item).from_statement(" select * from item where id in ( select r.id_item  from item i, relacion r "+
                                                            " where i.id = r.id_item_duenho and r.id_item_duenho= "+str(maxversionitem.id)+" ) ")

            list_relac_padres = db_session.query(Relacion).from_statement("select * from relacion where id in  ( select r.id  from item i, relacion r "+ 
                                                               " where i.id = r.id_item_duenho and r.id_item_duenho=  "+str(maxversionitem.id)+") ")
            #item hijos y sus relaciones
            list_item_hijos = db_session.query(Item).from_statement(" select * from item where id in ( select r.id_item_duenho   from item i, relacion r "+
                                                            " where i.id = r.id_item and r.id_item = "+str(id_itemg)+" ) ")
    
            list_relac_hijos = db_session.query(Relacion).from_statement("select * from relacion where id in  ( select r.id  from item i, relacion r "+
                                                                 " where i.id = r.id_item  and r.id_item= "+str(id_itemg)+") ")
            # cambios en items hijos
            if list_item_hijos != None   :            
                for hijo in list_item_hijos : 
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
                        relacion= Relacion(rel_hijo.fecha_creacion, today, rel_hijo.id_tipo_relacion, item_aux.id, item2.id, 'A')
                        db_session.add(relacion)
                        db_session.commit() 
                 
            # cambios en items padres
            if list_item_padres != None     :
                for padre in list_item_padres :
#                    atri2 = db_session.query(Atributo).from_statement(" select at.* from tipo_item ti , titem_atributo ta, atributo at "+
#                                                        " where ti.id = ta.id_tipo_item and at.id = ta.id_atributo and ti.id=  " +str(padre.id_tipo_item) )
#    
#                    valores_atr2 = db_session.query(ItemAtributo).from_statement(" select ia.* from item_atributo ia where ia.id_item= " +str(padre.id) )
#                    item3 = Item(padre.codigo, padre.nombre, padre.descripcion, 'V', padre.complejidad, today, padre.costo, 
#                    session['user_id']  , padre.version +1 , padre.id_fase , padre.id_tipo_item , padre.archivo)            
#                    db_session.add(item3)
#                    db_session.commit()  
#                    # se actualizan los atributos del item si es que tienen
#                    if atri2 != None :
#                        for atr in atri2 :
#                            for val in valores_atr2 :   
#                                if val.id_atributo == atr.id :                  
#                                    ia= ItemAtributo(val.valor, item3.id, atr.id)
#                                    db_session.add(ia)
#                                    db_session.commit()   
                    for rel_padre in list_relac_padres:
                        rel_padre.estado= 'E'
                        db_session.merge(rel_padre)
                        db_session.commit() 
                        relacion= Relacion(rel_padre.fecha_creacion, today, rel_padre.id_tipo_relacion, padre.id, item_aux.id,  'A')
                        db_session.add(relacion)
                        db_session.commit() 
           
            #se modifica en la lb            
            linea= db_session.query(LbItem).join(LineaBase, LineaBase.id==LbItem.id_linea_base).filter(LbItem.id_item==id_itemg).first() 
            if linea != None:
                db_session.delete(linea)
                db_session.commit()
                lin = LbItem(linea.id_linea_base, item.id)
                db_session.add(lin)
                db_session.commit() 
            
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
    ##init_db(db_session)
    item2 = db_session.query(Item).from_statement(" select i.* from item i where i.estado = 'E' and version = (Select max(i2.version) from item i2 where i2.codigo = i.codigo ) order by i.codigo " )
    return render_template('item/listarreviviritem.html', items2 = item2)  
    
    
@app.route('/item/reviviritem', methods=['GET', 'POST'])
def reviviritem():   
    """funcion que permite revivir un item"""
    today = datetime.date.today()
    ##init_db(db_session)      
                     
    i = db_session.query(Item).filter_by(codigo=request.args.get('cod')).filter_by(id=request.args.get('id')).first() 
    if  request.args.get('id') == None:
        id_itemg= request.form.get('id')
    else:
        id_itemg=request.args.get('id')
        
    if  request.args.get('tipo') == None:
        id_tipog= request.form.get('id_tipo_f')
    else:
        id_tipog=request.args.get('tipo')
    
    if  request.args.get('fase') == None:
        id_faseg= request.form.get('id_fase_f')
    else:
        id_faseg=request.args.get('fase')
        
    var = "MODIFICACION ITEM F" + str(id_faseg)
    permission = UserPermission(var, int(id_faseg) )
    if permission.can() == False:
            flash('No posee los Permisos suficientes para realizar esta Operacion','error')
            return redirect('/item/administraritem') 
    form = ItemEditarFormulario(request.form,i)   
              
    item = db_session.query(Item).filter_by(nombre=form.nombre.data).filter_by(id=id_itemg).first()  
    form.usuario.data = session['user_id']  
    estado= request.args.get('es')
           
    if request.method != 'POST':        
        fase_selected= db_session.query(Fase).filter_by(id=id_faseg).first()      
        tipo_selected= db_session.query(TipoItem).filter_by(id= id_tipog ).first()
        form.fase.data= fase_selected.nombre  
        form.tipo_item.data= tipo_selected.nombre
        form.id_fase_f.data= id_faseg
        form.id_tipo_f.data = id_tipog
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
     
    #atributo=  db_session.query(Atributo).join(TItemAtributo, Atributo.id== TItemAtributo.id_atributo).filter(TipoItem.id == id_tipog ).all() 
    atributo = db_session.query(Atributo).from_statement(" select at.* from tipo_item ti , titem_atributo ta, atributo at "+
                                                        " where ti.id = ta.id_tipo_item and at.id = ta.id_atributo and ti.id=  " +str(id_tipog) )
    
    valoresatr = db_session.query(ItemAtributo).from_statement(" select ia.* from item_atributo ia where ia.id_item= " +str(id_itemg) )
   
    #verifica si puede ser modificado:
   
    if request.method == 'POST' and form.validate():
        ##init_db(db_session)
        try:   
            maxversionitem = db_session.query(Item).from_statement("select *  from item where codigo = '"+form.codigo.data+"' and version = ( "+ 
                                                                    " select max(version) from item i where i.codigo = '"+form.codigo.data+"' )" ).first()
            
            #se obtiene la version previa a la eliminacion del item
            item_aux = db_session.query(Item).from_statement("select * from item where codigo= '"+form.codigo.data+"' and version = "+str(form.version.data)+"-1 " ).first()
            #se cambia el estado del item a Revision y re reversiona el item
            item2 = Item(item_aux.codigo, item_aux.nombre, item_aux.descripcion, 
                    'V', item_aux.complejidad, today, item_aux.costo, 
                     session['user_id']  , maxversionitem.version + 1 , id_faseg , id_tipog, item_aux.archivo )
            db_session.add(item2)
            db_session.commit()
            if atributo != None:
                for atr in atributo:
                    for val in valoresatr:
                        if atr.id == val.id_atributo:
                            #valor =  request.form.get(atr.nombre)                   
                            ia= ItemAtributo(val.valor, item2.id, atr.id)
                            db_session.add(ia)
                            db_session.commit()
            session.pop('estado_global',None)
            # --------------------------------------------------------------------------------------------------
            #  se verifica si el item poseia alguna relacion antes de eliminarse para recuperar la misma
            #---------------------------------------------------------------------------------------------------
            
            #items padres y sus relaciones
            list_item_padres = db_session.query(Item).from_statement(" select * from item where id in ( select r.id_item  from item i, relacion r "+
                                                            " where i.id = r.id_item_duenho and r.id_item_duenho= "+str(maxversionitem.id)+" and r.estado = 'E' ) ")

            list_relac_padres = db_session.query(Relacion).from_statement("select * from relacion where id in  ( select r.id  from item i, relacion r "+ 
                                                               " where i.id = r.id_item_duenho and r.id_item_duenho=  "+str(maxversionitem.id)+" and r.estado = 'E' ) ")
            #item hijos y sus relaciones
            list_item_hijos = db_session.query(Item).from_statement(" select * from item where id in ( select r.id_item_duenho   from item i, relacion r "+
                                                            " where i.id = r.id_item and r.id_item = "+str(item_aux.id)+" and r.estado = 'E' ) ")
    
            list_relac_hijos = db_session.query(Relacion).from_statement("select * from relacion where id in  ( select r.id  from item i, relacion r "+
                                                                 " where i.id = r.id_item  and r.id_item= "+str(item_aux.id)+" and r.estado = 'E') ")
          
            posee_cliclo = False
            if list_relac_padres != None and list_relac_hijos !=None:
                for rel_padre in list_relac_padres:
                    for rel_hijo in list_relac_hijos :
                        if rel_padre.id == rel_hijo.id :
                            posee_cliclo= True;
                            
                       
            if posee_cliclo == False:
                #cambios en items hijos
                if list_item_hijos != None   :            
                    for hijo in list_item_hijos : 
                        atri = db_session.query(Atributo).from_statement(" select at.* from tipo_item ti , titem_atributo ta, atributo at "+
                                                        " where ti.id = ta.id_tipo_item and at.id = ta.id_atributo and ti.id=  " +str(hijo.id_tipo_item) )
    
                        valores_atr = db_session.query(ItemAtributo).from_statement(" select ia.* from item_atributo ia where ia.id_item= " +str(hijo.id) )
                        item1 = Item(hijo.codigo, hijo.nombre, hijo.descripcion, 'V', hijo.complejidad, today, hijo.costo, 
                                session['user_id']  , hijo.version +1 , hijo.id_fase , hijo.id_tipo_item , hijo.archivo)            
                        db_session.add(item1)
                        db_session.commit()  
                        # se actualizan los atributos del item si es que tienen
                        if atri != None :
                            for atr in atri :
                                for val in valores_atr :   
                                    if val.id_atributo == atr.id :                  
                                        ia= ItemAtributo(val.valor, item1.id, atr.id)
                                        db_session.add(ia)
                                        db_session.commit()   
                        for rel_hijo in list_relac_hijos :
                            rel_hijo.estado= 'E'
                            db_session.merge(rel_hijo)
                            db_session.commit() 
                            relacion= Relacion(rel_hijo.fecha_creacion, today, rel_hijo.id_tipo_relacion, item2.id, item1.id, 'A')
                            db_session.add(relacion)
                            db_session.commit() 
                 
                # cambios en items padres
                if list_item_padres != None     :
                    for padre in list_item_padres :
#                        atri2 = db_session.query(Atributo).from_statement(" select at.* from tipo_item ti , titem_atributo ta, atributo at "+
#                                                        " where ti.id = ta.id_tipo_item and at.id = ta.id_atributo and ti.id=  " +str(padre.id_tipo_item) )
#    
#                        valores_atr2 = db_session.query(ItemAtributo).from_statement(" select ia.* from item_atributo ia where ia.id_item= " +str(padre.id) )
#                        item3 = Item(padre.codigo, padre.nombre, padre.descripcion, 'V', padre.complejidad, today, padre.costo, 
#                                     session['user_id']  , padre.version +1 , padre.id_fase , padre.id_tipo_item , padre.archivo)            
#                        db_session.add(item3)
#                        db_session.commit()  
#                        # se actualizan los atributos del item si es que tienen
#                        if atri2 != None :
#                            for atr in atri2 :
#                                for val in valores_atr2 :   
#                                    if val.id_atributo == atr.id :                  
#                                        ia= ItemAtributo(val.valor, item3.id, atr.id)
#                                        db_session.add(ia)
#                                        db_session.commit()   
                        for rel_padre in list_relac_padres:
                            rel_padre.estado= 'E'
                            db_session.merge(rel_padre)
                            db_session.commit() 
                            relacion= Relacion(rel_padre.fecha_creacion, today, rel_padre.id_tipo_relacion, maxversionitem.id, item2.id,  'A')
                            db_session.add(relacion)
                            db_session.commit() 
                
            else :          
                flash('El Item ha sido Revivido con Exito, pero no se han recuperado sus relaciones','info')
                return redirect('/item/administraritem')    
            
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
    ##init_db(db_session)
    item = db_session.query(Item).from_statement("Select it.*  from item it, "+ 
                        " (Select  i.codigo cod, max(i.version) vermax from item i, fase f  where i.id_fase = f.id "+
                        " and f.id_proyecto = "+str(session['pry'])+"  group by codigo order by 1 ) s "+
                        " where it.codigo = cod and it.version= vermax and it.estado != 'E'  " )
    
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

