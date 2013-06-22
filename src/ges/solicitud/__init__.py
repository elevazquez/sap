from loginC import app

from util.database import init_db, engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import DatabaseError
from sqlalchemy import func, Integer
from flask import Flask, render_template, request, redirect, url_for, flash, session 
from adm.mod.Proyecto import Proyecto
from adm.mod.Usuario import Usuario
from des.mod.Fase import Fase
from ges.mod.SolicitudCambio import SolicitudCambio
from ges.mod.SolicitudItem import SolicitudItem
from des.mod.Item import Item
from ges.mod.ResolucionMiembros import ResolucionMiembros
from ges.solicitud.SolicitudFormulario import SolicitudFormulario
from ges.solicitud.ReporteFormulario import ReporteFormulario
from ges.solicitud.SolicitudReporte import SolicitudReporte
from flask_login import current_user
from flask import Response 
import flask, flask.views
import os
import datetime
from des.item.ReporteHistorialFormulario import ReporteHistorialFormulario
from des.item.HistorialReporte import HistorialReporte
from des.item.ListaItemFormulario import ListaItemFormulario
from des.item.ListaReporte import ListaReporte
from geraldo.generators import PDFGenerator

cur_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
class SolicitudControlador(flask.views.MethodView):
    def get(self):
        return flask.render_template('solicitud.html')
    
def flash_errors(form):
    """Funcion para capturar errores del Formulario"""
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ),'error')

@app.route('/solicitud/nuevasolicitud', methods=['GET', 'POST'])
def nuevasolicitud():
    """ Funcion para agregar registros a la tabla Solicitud""" 
    today = datetime.date.today()
    form = SolicitudFormulario(request.form)
#    init_db(db_session)
    pro = db_session.query(Proyecto).filter_by(id=session['pry']).first()
    if pro.estado != 'P' :
        flash('No se pueden agregar Solicitudes a un Proyecto que no se encuentre En Progreso','info')
        return render_template('solicitud/administrarsolicitud.html')
    form.estado.data = 'Nueva'
    form.id_proyecto.data = pro.nombre
    form.id_usuario.data = current_user.usuario
    form.fecha.data = today
    form.cant_votos.data = 0
    #id_fase = request.args.get('id_fase')
    #if (id_fase!=None):
     #   session['faseid'] = id_fase
    items = db_session.query(Item).from_statement("Select it.*  from item it, "+ 
                        " (Select  i.codigo cod, max(i.version) vermax from item i, fase f  where i.id_fase = f.id "+
                        " and f.id_proyecto = "+str(session['pry'])+ " group by codigo order by 1 ) s "+
                        " where it.codigo = cod and it.version= vermax and it.estado = 'B' " + 
                        " and it.id not in(select id_item from solicitud_item where id_solicitud in (select id from solicitud_cambio " +
                        " where id_proyecto = "+str(session['pry'])+" and (estado='N' or estado ='E'))) order by it.codigo ")
    if request.method == 'POST' and form.validate():
 #       init_db(db_session)
        try:
            multiselect= request.form.getlist('selectitem')  
            list_aux=[]
            
            for it in multiselect :
                i = db_session.query(Item).filter_by(id=it).first()    
                list_aux.append(i)
                #id_fase= i.id_fase            
            
            if list_aux == None or list_aux == []:
                flash('Debe seleccionar un item','info')
                return render_template('solicitud/administrarsolicitud.html')         
            
            solicitud = SolicitudCambio(form.descripcion.data, 'N', today, 0, current_user.id, pro.id )
            db_session.add(solicitud)
            db_session.commit()
            
            #se guarda la solicitud junto con los item pertenecientes al mismo          
            for it in list_aux:
                solit= SolicitudItem(solicitud.id, it.id)
                db_session.add(solit)
                db_session.commit()

            flash('La solicitud ha sido registrada con exito','info')
            return redirect('/solicitud/administrarsolicitud')
        except DatabaseError, e:
            if e.args[0].find('duplicate key value violates unique')!=-1:
                flash('Clave unica violada por favor ingrese otro NUMERO de Solicitud' ,'error')
            else:
                flash('Error en la Base de Datos' + e.args[0],'error')
            return render_template('solicitud/nuevasolicitud.html', items= items, form= form)
    else:
        flash_errors(form)  
    return render_template('solicitud/nuevasolicitud.html', form= form ,items= items)

@app.route('/solicitud/editarsolicitud', methods=['GET', 'POST'])
def editarsolicitud():
    """ Funcion para editar registros de la tabla Solicitud""" 
#    init_db(db_session)
    today = datetime.date.today()
    pro = db_session.query(Proyecto).filter_by(id=session['pry']).first()
    if  request.args.get('id') == None:
        id_sol= request.form.get('id')
    else:
        id_sol=request.args.get('id')
    s = db_session.query(SolicitudCambio).filter_by(id=id_sol).filter_by(id_proyecto=session['pry']).first()
    itemssol=  db_session.query(Item).from_statement("select * from item where id in(select id_item from solicitud_item where id_solicitud="+str(id_sol)+")")  
    form = SolicitudFormulario(request.form,s)
    solicitud = db_session.query(SolicitudCambio).filter_by(id=id_sol).filter_by(id_proyecto=session['pry']).first()  
    form.fecha.data = today
    form.id_proyecto.data = pro.nombre
    form.id_usuario.data = current_user.usuario
    form.cant_votos.data = 0
    if pro.estado != 'P' :
        flash('No se pueden editar Solicitudes a un Proyecto que no se encuentre En Progreso','info')
        return render_template('solicitud/administrarsolicitud.html')
    if solicitud.estado != 'N' :
        flash('No se pueden modificar Solicitudes que hayan sido enviadas para su Aprobacion','info')
        return render_template('solicitud/administrarsolicitud.html')
    if solicitud.estado=='N':
        form.estado.data='Nueva'
    if request.method == 'POST' and form.validate():
        try:
            form.populate_obj(solicitud)
            if form.estado.data=='Nueva':
                solicitud.estado='N'
            solicitud.id_proyecto=pro.id
            solicitud.id_usuario=current_user.id
            db_session.merge(solicitud)
            db_session.commit()
            return redirect('/solicitud/administrarsolicitud')
        except DatabaseError, e:
            flash('Error en la Base de Datos' + e.args[0],'error')
            return render_template('solicitud/editarsolicitud.html', form=form, items=itemssol)
    else:
        flash_errors(form) 
    return render_template('solicitud/editarsolicitud.html', form=form, items=itemssol)

@app.route('/solicitud/enviarsolicitud', methods=['GET', 'POST'])
def enviarsolicitud():
    """ Funcion para enviar la Solicitud""" 
#    init_db(db_session)
    pro = db_session.query(Proyecto).filter_by(id=session['pry']).first()
    solicitud = db_session.query(SolicitudCambio).filter_by(id=request.args.get('id')).filter_by(id_proyecto=pro.id).first()  
    if pro.estado != 'P' :
        flash('No se pueden enviar Solicitudes a un Proyecto que no se encuentre En Progreso','info')
        return render_template('solicitud/administrarsolicitud.html')
    if solicitud.estado != 'N' :
        flash('No se pueden enviar Solicitudes que ya hayan sido enviadas para su Aprobacion','info')
        return render_template('solicitud/administrarsolicitud.html')
    solicitud.estado='E'
    try:
        db_session.merge(solicitud)
        db_session.commit()
        return redirect('/solicitud/administrarsolicitud')
    except DatabaseError, e:
        flash('Error en la Base de Datos' + e.args[0],'info')
        return render_template('/solicitud/administrarsolicitud.html')

@app.route('/solicitud/eliminarsolicitud', methods=['GET', 'POST'])
def eliminarsolicitud():
    """ Funcion para eliminar registros de la tabla Solicitud""" 
#    init_db(db_session)
    if  request.args.get('id') == None:
        id_sol= request.form.get('id')
    else:
        id_sol=request.args.get('id')
    s = db_session.query(SolicitudCambio).filter_by(id=id_sol).filter_by(id_proyecto=session['pry']).first()
    pro = db_session.query(Proyecto).filter_by(id=session['pry']).first()
    if pro.estado != 'P' :
        flash('No se pueden eliminar Solicitudes a un Proyecto que no se encuentre En Progreso','info')
        return render_template('solicitud/administrarsolicitud.html')  
    if s.estado != 'N' :
        flash('No se pueden eliminar Solicitudes que hayan sido enviadas para su Aprobacion','info')
        return render_template('solicitud/administrarsolicitud.html')
    try:
#        init_db(db_session)
        solicitud = db_session.query(SolicitudCambio).filter_by(id=id_sol).filter_by(id_proyecto=session['pry']).first()  
        itemssol=  db_session.query(Item).from_statement("select * from item where id in(select id_item from solicitud_item where id_solicitud='"+str(solicitud.id)+"')")
        #itemssol=  db_session.query(Item).join(SolicitudItem, Item.id== SolicitudItem.id_item).filter(SolicitudItem.id_solicitud== solicitud.id ).all()   
#        list_aux=[]
#        for it in itemssol :
#            i = db_session.query(Item).filter_by(id=it).first()    
#            list_aux.append(i)
#                
        #se elimina el id de los item de la sol          
        for it in itemssol:
            s = db_session.query(SolicitudItem).filter_by(id_item=it.id).first()  
            db_session.delete(s)
            db_session.commit()

        db_session.delete(solicitud)
        db_session.commit()
        return redirect('/solicitud/administrarsolicitud')
    except DatabaseError, e:
            flash('Error en la Base de Datos' + e.args[0],'info')
            return render_template('/solicitud/administrarsolicitud.html')
    
@app.route('/solicitud/buscarsolicitud', methods=['GET', 'POST'])
def buscarsolicitud():
    """ Funcion para buscar registros de la tabla Solicitud""" 
    valor = request.args['patron']
    parametro = request.args['parametro']
#    init_db(db_session)
    if valor == "" : 
        p = db_session.query(SolicitudCambio).filter_by(id_proyecto=session['pry']).filter_by(id_usuario=current_user.id).order_by(SolicitudCambio.descripcion)
    elif parametro == 'fecha' :
        p = db_session.query(SolicitudCambio).from_statement("SELECT * FROM solicitud_cambio where to_char("+parametro+", 'YYYY-mm-dd') ilike '%"+valor+"%' and id_proyecto='"+session['pry']+"' and id_usuario='"+str(current_user.id)+"'").all()
    else:
        p = db_session.query(SolicitudCambio).from_statement("SELECT * FROM solicitud_cambio where "+parametro+" ilike '%"+valor+"%' and id_proyecto='"+session['pry']+"' and id_usuario='"+str(current_user.id)+"'").all()
    return render_template('solicitud/administrarsolicitud.html', solicituds = p)

@app.route('/solicitud/administrarsolicitud')
def administrarsolicitud():
    """ Funcion para listar registros de la tabla Solicitud""" 
#    init_db(db_session)
    solicituds = db_session.query(SolicitudCambio).filter_by(id_proyecto=session['pry']).filter_by(id_usuario=current_user.id).order_by(SolicitudCambio.descripcion)
    return render_template('solicitud/administrarsolicitud.html', solicituds = solicituds)

@app.route('/solicitud/buscarfase', methods=['GET', 'POST'])
def buscarfase():
    """ Funcion para buscar registros de la tabla Fase""" 
    valor = request.args['patron']
    parametro = request.args['parametro']
#    init_db(db_session)
    if valor == "" : 
        p = db_session.query(Fase).filter_by(id_proyecto=session['pry']).order_by(Fase.nro_orden)
    elif parametro == 'nro_orden' :
        p = db_session.query(Fase).from_statement("SELECT * FROM fase where to_char("+parametro+", '99999') ilike '%"+valor+"%' and id_proyecto='"+session['pry']+"'").all()
    elif parametro == 'id_proyecto':
        p = db_session.query(Fase).from_statement("SELECT * FROM fase where id_proyecto='"+session['pry']+"' and "+parametro+" in (SELECT id FROM proyecto where nombre ilike '%"+valor+"%')").all()
    elif parametro == 'fecha_inicio' or parametro == 'fecha_fin':
        p = db_session.query(Fase).from_statement("SELECT * FROM fase where to_char("+parametro+", 'YYYY-mm-dd') ilike '%"+valor+"%' and id_proyecto='"+session['pry']+"'").all()
    else:
        p = db_session.query(Fase).from_statement("SELECT * FROM fase where "+parametro+" ilike '%"+valor+"%' and id_proyecto='"+session['pry']+"'").all()
    return render_template('solicitud/listarfase.html', fases2 = p)

@app.route('/solicitud/buscaritem', methods=['GET', 'POST'])
def buscaritem():
    """Funcion que permite realizar busqueda de items"""
    valor = request.args['patron']
    parametro = request.args['parametro']
    #init_db(db_session)
    if valor == "" : 
            listaritem()
    else:
        i = db_session.query(Item).from_statement("Select it.*  from item it,  "+ 
                        " (Select  i.codigo cod, max(i.version) vermax from item i, fase f  where i.id_fase = f.id "+
                        " and f.id_proyecto = "+str(session['pry'])+ " group by codigo order by 1 ) s "+
                        " where it.codigo = cod and it.version= vermax and it.estado = 'B' and lower( it."+parametro+" )  ilike lower( '%"+valor+"%' ) "+
                        " and it.id not in(select id_item from solicitud_item where id_solicitud in (select id from solicitud_cambio " +
                        " where id_proyecto = "+str(session['pry'])+" and (estado='N' or estado ='E'))) order by it.codigo ").all()
    return render_template('solicitud/listaritem.html', items = i)    
    valor = request.args['patron']
    #r = db_session.query(Item).filter_by(nombre=valor)
    r = db_session.query(Item).from_statement("Select it.*  from item it,  "+ 
                        " (Select  i.codigo cod, max(i.version) vermax from item i, fase f  where i.id_fase = f.id "+
                        " and f.id_proyecto = "+str(session['pry'])+ " group by codigo order by 1 ) s "+
                        " where it.codigo = cod and it.version= vermax and it.estado = 'B' and lower( it.nombre )  ilike lower( '%"+valor+"%' ) "+
                        " and it.id not in(select id_item from solicitud_item where id_solicitud in (select id from solicitud_cambio " +
                        " where id_proyecto = "+str(session['pry'])+" and (estado='N' or estado ='E'))) order by it.codigo ").all()
    if r == None:
        return 'no existe concordancia'
    return render_template('solicitud/listaritem.html', items = r)

@app.route('/solicitud/listaritem')
def listaritem():
    """Lista los items, su ultima version """
    #init_db(db_session)
    item = db_session.query(Item).from_statement("Select it.*  from item it, "+ 
                        " (Select  i.codigo cod, max(i.version) vermax from item i, fase f  where i.id_fase = f.id "+
                        " and f.id_proyecto = "+str(session['pry'])+ " group by codigo order by 1 ) s "+
                        " where it.codigo = cod and it.version= vermax and it.estado = 'B' " + 
                        " and it.id not in(select id_item from solicitud_item where id_solicitud in (select id from solicitud_cambio " +
                        " where id_proyecto = "+str(session['pry']) +" and (estado='N' or estado ='E'))) order by it.codigo ")
    return render_template('solicitud/listaritem.html', items = item)

@app.route('/solicitud/agregaritemssol', methods=['GET', 'POST'])
def agregaritemssol():   
    """ Funcion que agrega a una lista los items seleccionados """ 
    #init_db(db_session)
    selecteditem=  request.args.get('id_item')    
    items = db_session.query(Item).from_statement("Select it.*  from item it, "+ 
                        " (Select  i.codigo cod, max(i.version) vermax from item i, fase f  where i.id_fase = f.id "+
                        " and f.id_proyecto = "+str(session['pry'])+ " group by codigo order by 1 ) s "+
                        " where it.codigo = cod and it.version= vermax and it.estado = 'B' " + 
                        " and it.id not in(select id_item from solicitud_item where id_solicitud in (select id from solicitud_cambio " +
                        " where id_proyecto = "+str(session['pry'])+" and (estado='N' or estado ='E'))) order by it.codigo ")
    return render_template('solicitud/listaitem.html', items = items)  

@app.route('/solicitud/agregaritemsol', methods=['GET', 'POST'])
def agregaritemsol():
    """ Funcion para asignar Items a una solicitud""" 
    #init_db(db_session)   
    if  request.args.get('id_sol') == None:
        id_sol= request.form.get('id')
    else:
        id_sol=request.args.get('id_sol')

    sol = db_session.query(SolicitudCambio).filter_by(id=id_sol).first()
    if sol.estado != 'N' :
        flash('No se pueden agregar Items a Solicitudes que hayan sido enviadas para su Aprobacion','info')
        return render_template('solicitud/administrarsolicitud.html')         
    form = SolicitudFormulario(request.form,sol) 
    solicitud = db_session.query(SolicitudCambio).filter_by(id=sol.id).first() 
    itemssol=  db_session.query(Item).join(SolicitudItem, Item.id== SolicitudItem.id_item).filter(SolicitudItem.id_solicitud== id_sol ).filter(Item.estado=='B').all()   
    item_aux= db_session.query(Item).join(SolicitudItem, Item.id== SolicitudItem.id_item).filter(SolicitudItem.id_solicitud== id_sol).first()    
    form.estado.data = 'Nueva'
    itemsdisp = db_session.query(Item).from_statement("Select it.*  from item it, "+ 
                        " (Select  i.codigo cod, max(i.version) vermax from item i, fase f  where i.id_fase = f.id "+
                        " and f.id_proyecto = "+str(session['pry'])+"  group by codigo order by 1 ) s "+
                        " where it.codigo = cod and it.version= vermax and (it.estado = 'B')  and it.id not in (select id_item from solicitud_item where id_solicitud in (select id from solicitud_cambio " +
                        " where id_proyecto = "+str(session['pry'])+" and (estado='N' or estado ='E')) ) order by it.codigo " )
    if request.method == 'POST' and form.validate(): 
        items=request.form.getlist('selectitem')
        try:
            list_aux=[]
            for it in items :
                i = db_session.query(Item).filter_by(id=it).first()    
                list_aux.append(i)

            if list_aux == None or list_aux == []:
                flash('Debe seleccionar un item','info')
                return render_template('solicitud/administrarsolicitud.html')         
                    
            #se guarda la sol junto con los item pertenecientes al mismo          
            for it in list_aux:
                solit= SolicitudItem(solicitud.id, it.id)
                db_session.add(solit)
                db_session.commit()
     
            flash('Se agrego el Item con Exito','info')   
            return redirect('/solicitud/administrarsolicitud')
        except DatabaseError, e:
            flash('Error en la Base de Datos' + e.args[0],'error')
            return render_template('solicitud/agregaritemsol.html', form=form,  items= itemsdisp)  
    else:
        flash_errors(form)    
    return render_template('solicitud/agregaritemsol.html', form=form,  items= itemsdisp)  

@app.route('/solicitud/quitaritemsol', methods=['GET', 'POST'])
def quitaritemsol():
    """ Funcion para quitar Items de una sol""" 
    #init_db(db_session)   
    if  request.args.get('id_sol') == None:
        id_sol= request.form.get('id')
    else:
        id_sol=request.args.get('id_sol')    
    sol = db_session.query(SolicitudCambio).filter_by(id=id_sol).first()  
    if sol.estado != 'N' :
        flash('No se pueden eliminar Items a Solicitudes que hayan sido enviadas para su Aprobacion','info')
        return render_template('solicitud/administrarsolicitud.html')     
    form = SolicitudFormulario(request.form,sol) 
    #solicitud = db_session.query(SolicitudCambio).filter_by(id= sol.id).first() 
    #itemssol=  db_session.query(SolicitudItem).join(Item, SolicitudItem.id_item== Item.id).filter(SolicitudItem.id_solicitud== sol.id ).all()   
    #itemssol=  db_session.query(SolicitudItem).from_statement("select * from item where id in(select id_item from solicitud_item where id_solicitud='"+str(sol.id)+"')")
    itemssol=  db_session.query(Item).join(SolicitudItem, Item.id== SolicitudItem.id_item).filter(SolicitudItem.id_solicitud== sol.id ).all()   
    if request.method == 'POST' and form.validate(): 
        items=request.form.getlist('selectitem')
        try:
            list_aux=[]
            if len(itemssol) == len(items):
                flash('La Solicitud no puede quedarse sin Items','info')   
                return redirect('/solicitud/administrarsolicitud')
            for it in items :
                i = db_session.query(Item).filter_by(id=it).first()    
#                item = Item(i.codigo, i.nombre, i.descripcion, 'A', i.complejidad, today, i.costo, 
#                  session['user_id']  , i.version +1 , i.id_fase , i.id_tipo_item , i.archivo)            
#                db_session.add(item)
#                db_session.commit()
                list_aux.append(i)
                
            #se elimina el id de los item de la sol          
            for it in list_aux:
                s = db_session.query(SolicitudItem).filter_by(id_item=it.id).first()  
                db_session.delete(s)
                db_session.commit()
                 
            flash('Se quito el Item con Exito','info')   
            return redirect('/solicitud/administrarsolicitud')
        except DatabaseError, e:
            flash('Error en la Base de Datos' + e.args[0],'error')
            return render_template('solicitud/quitaritemsol.html', form=form,  items=itemssol)
    else:
        flash_errors(form)    
    return render_template('solicitud/quitaritemsol.html', form=form,  items=itemssol)  

@app.route('/solicitud/versolicitud', methods=['GET', 'POST'])
def versolicitud():
    """ Funcion para consultar registros de la tabla Solicitud""" 
#    init_db(db_session)
    pro = db_session.query(Proyecto).filter_by(id=session['pry']).first()
    if  request.args.get('id') == None:
        id_sol= request.form.get('id')
    else:
        id_sol=request.args.get('id')
    s = db_session.query(SolicitudCambio).filter_by(id=id_sol).filter_by(id_proyecto=session['pry']).first()
    itemssol=  db_session.query(Item).from_statement("select * from item where id in(select id_item from solicitud_item where id_solicitud="+str(id_sol)+")")  
    res = db_session.query(ResolucionMiembros).filter_by(id_solicitud_cambio=s.id).all()
    form = SolicitudFormulario(request.form,s)
    solicitud = db_session.query(SolicitudCambio).filter_by(id=id_sol).filter_by(id_proyecto=session['pry']).first()  
    form.id_proyecto.data = pro.nombre
    form.id_usuario.data = current_user.usuario
    if solicitud.estado=='N':
        form.estado.data='Nueva'
    elif solicitud.estado=='E':
        form.estado.data='Enviada'
    elif solicitud.estado=='A':
        form.estado.data='Aprobada'
    elif solicitud.estado=='R':
        form.estado.data='Rechazada'
    return render_template('solicitud/versolicitud.html', form=form, items=itemssol, res=res)

@app.route('/solicitud/reportesol', methods=['GET', 'POST'])
def reportesol():   
    """ Funcion que imprime el reporte de la sol """
    today = datetime.date.today()
    form = ReporteFormulario(request.form)
    form.fecha.data = today
    usuarios = db_session.query(Usuario).order_by(Usuario.nombre).all()
        
    if  request.method == 'POST' and form.validate():
        # sql = db_session.query(SolicitudCambio).filter_by(id_proyecto=session['pry'])
        multiselect= request.form.getlist('selectitem')  
        list_aux=[]
        f = None
        if multiselect != None and multiselect != [] :
            for fa in multiselect : 
                f = db_session.query(Usuario).filter_by(id=fa).first()    
                list_aux.append(f)
            if list_aux != None and list_aux != [] :
                f = list_aux[0]
        p = db_session.query(Proyecto).filter_by(id=session['pry']).first()
        if (f==None) :
            sql = db_session.query(SolicitudCambio).from_statement("select sc.id, sc.descripcion, sc.fecha, u.nombre as id_usuario, " +
                                                                   " (CASE WHEN sc.estado='N' THEN 'Nueva' WHEN sc.estado='E' THEN 'Enviada' WHEN sc.estado='A' THEN 'Aprobada' WHEN sc.estado='R' " + 
                                                                   " THEN 'Rechazada' END) as estado, rm.voto as cant_votos from usuario u, solicitud_cambio sc left join resolucion_miembros rm " + 
                                                                   " on sc.id = rm.id_solicitud_cambio and rm.id_usuario = "+str(p.id_usuario_lider)+" where sc.id_proyecto = "+str(session['pry'])+" and sc.id_usuario = u.id order by sc.id ") 
            a = sql.first()
            if (a == None) :
                flash('No se encuentran registros para el reporte','info')   
                return redirect('/solicitud/administrarreportes')
            reporte = SolicitudReporte(queryset=sql.all())
            reporte.generate_by(PDFGenerator, filename=os.path.join(cur_dir, cur_dir + '/static/reportes/Solicitudes.pdf'))
        else :
            sql = db_session.query(SolicitudCambio).from_statement("select sc.id, sc.descripcion, sc.fecha, u.nombre as id_usuario, " +
                                                                   " (CASE WHEN sc.estado='N' THEN 'Nueva' WHEN sc.estado='E' THEN 'Enviada' WHEN sc.estado='A' THEN 'Aprobada' WHEN sc.estado='R' " + 
                                                                   " THEN 'Rechazada' END) as estado, rm.voto as cant_votos from usuario u, solicitud_cambio sc left join resolucion_miembros rm " + 
                                                                   " on sc.id = rm.id_solicitud_cambio and rm.id_usuario = "+str(p.id_usuario_lider)+" where sc.id_proyecto = "+str(session['pry'])+
                                                                   " and sc.id_usuario = u.id and u.id= "+str(f.id)+"order by sc.id ") 
            a = sql.first()
            if (a == None) :
                flash('No se encuentran registros para el reporte','info')   
                return redirect('/solicitud/administrarreportes')
            reporte = SolicitudReporte(queryset=sql.all())
            reporte.generate_by(PDFGenerator, filename=os.path.join(cur_dir, cur_dir + '/static/reportes/Solicitudes.pdf'))
        filename=os.path.join(cur_dir, cur_dir + '/static/reportes/Solicitudes.pdf')
        results = open(filename ,'rb').read()
        generator = (cell for row in results
                    for cell in row) 
        return Response(generator,
                       mimetype='application/pdf',
                       headers={"Content-Disposition":
                                    "attachment;filename={0}".format('ReporteSolicitud.pdf')}) 
        #return render_template('solicitud/solicitud.html')
    else:
        flash_errors(form) 
    return render_template('solicitud/reportesolicitud.html', form=form, usuarios=usuarios)

@app.route('/solicitud/reportehistorial', methods=['GET', 'POST'])
def reportehistorial():   
    """ Funcion que imprime el reporte del historial """
    form = ReporteHistorialFormulario(request.form)
    items = db_session.query(Item).from_statement("Select it.*  from item it, "+ 
                        " (Select  i.codigo cod, max(i.version) vermax from item i, fase f  where i.id_fase = f.id "+
                        " and f.id_proyecto = "+str(session['pry'])+ " group by codigo order by 1 ) s "+
                        " where it.codigo = cod and it.version= vermax order by it.codigo ")
    if  request.method == 'POST' and form.validate():
        multiselect= request.form.getlist('selectitem')  
        list_aux=[]
        for it in multiselect : 
            i = db_session.query(Item).filter_by(id=it).first()    
            list_aux.append(i)
        if list_aux == None or list_aux == []:
            flash('Debe seleccionar un item','info')
            return render_template('solicitud/administrarsolicitud.html')
        i = list_aux[0]
        sql = db_session.query(Item).from_statement("select i.id, f.descripcion as id_fase, ti.descripcion as id_tipo_item, " +
        " i.codigo, i.version, i.descripcion, (CASE WHEN i.estado='P' THEN 'En Progreso' WHEN i.estado='R' THEN 'Resuelto' WHEN " +  
        " i.estado='A' THEN 'Aprobado' WHEN i.estado='Z' THEN 'Rechazado' WHEN i.estado='E' THEN 'Eliminado' " + 
        " WHEN i.estado='V' THEN 'Revision' WHEN i.estado='B' THEN 'Bloqueado' END) as estado, "
        " i.costo, i.complejidad from item i, fase f, tipo_item ti where i.codigo = '"+ str(i.codigo) +
        "' and f.id = i.id_fase and ti.id = i.id_tipo_item order by version ")
        a = sql.first()
        if (a == None) :
            flash('No se encuentran registros para el reporte','info')   
            return redirect('/solicitud/administrarreportes')
        reporte = HistorialReporte(queryset= sql)
        reporte.generate_by(PDFGenerator, filename=os.path.join(cur_dir, cur_dir + '/static/reportes/HistorialItem.pdf'))
        filename=os.path.join(cur_dir, cur_dir + '/static/reportes/HistorialItem.pdf')
        results = open(filename ,'rb').read()
        generator = (cell for row in results
                    for cell in row) 
        return Response(generator,
                       mimetype='application/pdf',
                       headers={"Content-Disposition":
                                    "attachment;filename={0}".format('ReportehistorialItem.pdf')}) 
        #return render_template('item/historial.html')
    else:
        flash_errors(form) 
    return render_template('item/reportehistorial.html', form=form, items=items)

@app.route('/solicitud/reportelista', methods=['GET', 'POST'])
def reportelista():   
    """ Funcion que imprime el reporte la lista de items """
    today = datetime.date.today()
    form = ListaItemFormulario(request.form)
    form.fecha.data = today
    fases = db_session.query(Fase).filter_by(id_proyecto=session['pry']).order_by(Fase.nro_orden)
    if  request.method == 'POST' and form.validate():
        multiselect= request.form.getlist('selectitem')  
        list_aux=[]
        f = None
        if multiselect != None and multiselect != [] :
            for fa in multiselect : 
                f = db_session.query(Fase).filter_by(id=fa).first()    
                list_aux.append(f)
            if list_aux != None and list_aux != [] :
                f = list_aux[0]
        if (f==None) :
            sql = db_session.query(Item).from_statement("Select it.id_fase, fa.descripcion as nombre, it.id, it.descripcion, it.version, it.complejidad from item it, fase fa," +  
            " (Select  i.codigo cod, max(i.version) vermax from item i, fase f  where i.id_fase = f.id and f.id_proyecto = "+str(session['pry'])+ " group by codigo order by 1 ) s " +
            " where it.codigo = cod and it.version= vermax and it.id_fase = fa.id order by it.id_fase, it.codigo ")
            a = sql.first()
            if (a == None) :
                flash('No se encuentran registros para el reporte','info')   
                return redirect('/solicitud/administrarreportes')
            reporte = ListaReporte(queryset= sql)
            reporte.generate_by(PDFGenerator, filename=os.path.join(cur_dir, cur_dir + '/static/reportes/ListaItem.pdf'))
        else :
            sql = db_session.query(Item).from_statement("Select it.id_fase, fa.descripcion as nombre, it.id, it.descripcion, it.version, it.complejidad from item it, fase fa," +  
            " (Select  i.codigo cod, max(i.version) vermax from item i, fase f  where i.id_fase = f.id and f.id_proyecto = "+str(session['pry'])+ " group by codigo order by 1 ) s " +
            " where it.codigo = cod and it.version= vermax and it.id_fase = fa.id and it.id_fase="+str(f.id)+" order by it.id_fase, it.codigo ")
            a = sql.first()
            if (a == None) :
                flash('No se encuentran registros para el reporte','info')   
                return redirect('/solicitud/administrarreportes')
            reporte = ListaReporte(queryset= sql)
            reporte.generate_by(PDFGenerator, filename=os.path.join(cur_dir, cur_dir + '/static/reportes/ListaItem.pdf'))
        filename=os.path.join(cur_dir, cur_dir + '/static/reportes/ListaItem.pdf')
        results = open(filename ,'rb').read()
        generator = (cell for row in results
                    for cell in row) 
        return Response(generator,
                       mimetype='application/pdf',
                       headers={"Content-Disposition":
                                    "attachment;filename={0}".format('ReporteListaItem.pdf')}) 
        #return render_template('item/ritem.html')
    else:
        flash_errors(form) 
    return render_template('item/reporteitem.html', form=form, fases=fases)

@app.route('/solicitud/administrarreportes', methods=['GET', 'POST'])
def administrarreportes():   
    return render_template('reportes/administrarreportes.html')

@app.errorhandler(404)
def page_not_found(error):
    """Lanza un mensaje de error en caso de que la pagina solicitada no exista"""
    return 'Esta Pagina no existe', 404

@app.after_request
def shutdown_session(response):
    """Cierra la sesion de la conexion con la base de datos"""
    db_session.remove()
    return response