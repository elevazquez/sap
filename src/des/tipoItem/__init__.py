from loginC import app
from flask import session

from util.database import init_db, engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import Flask, render_template, request, redirect, url_for, flash 
from des.mod.TipoItem import TipoItem
from des.mod.Item import Item
from flask_login import current_user
from sqlalchemy.exc import DatabaseError
from des.tipoItem.TipoItemFormulario import TipoItemFormulario  
from des.mod.TItemAtributo import TItemAtributo
from des.mod.Atributo import Atributo
from des.mod.Fase import Fase
import flask, flask.views
from wtforms import widgets
import os
from UserPermission import UserPermission, UserRol

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
class TipoItemControlador(flask.views.MethodView):
    def get(self):
        return flask.render_template('tipoItem.html')
    
def flash_errors(form):
    """funcion que captura los errores de Formulario"""
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ),'error')
                
@app.route('/tipoItem/nuevotipoItem', methods=['GET', 'POST'])
def nuevotipoItem():
    """ Funcion para agregar registros a la tabla de Tipo de Item""" 
    if not current_user.is_authenticated():
        flash('Debe loguearse primeramente!!!!', 'loggin')
        return render_template('index.html')
    
    permission =UserPermission('LIDER PROYECTO', int(session['pry']))
    if permission.can()==False:
        flash('No posee los permisos suficientes para realizar la operacion', 'info')
        return render_template('index.html') 
    
    form = TipoItemFormulario(request.form)
    #form.id_fase.choices= [(f.id, f.nombre) for f in db_session.query(Fase).filter_by(id_proyecto=session['pry']).filter_by(estado='I').order_by(Fase.nombre).all()]
    form.id_fase.choices= [(f.id, f.nombre) for f in db_session.query(Fase).from_statement("select * from fase where id_proyecto="+str(session['pry'])+" and (estado='I' or estado='P') order by nombre ").all()] 
    form.lista_atributo.choices = [(f.id, f.nombre) for f in db_session.query(Atributo).order_by(Atributo.nombre).all()]
    if request.method == 'POST' and form.validate():        
        try:
            #verifica si la fase esta en un estado inicial la cambia en progreso 
            fase_selected = db_session.query(Fase).filter_by(id=form.id_fase.data).first()
            if fase_selected.estado == "I" :
                fase_selected.estado = "P"
                db_session.merge(fase_selected)
                db_session.commit()     
            
            tipo = TipoItem( form.codigo.data, form.nombre.data, form.descripcion.data, 
                    form.id_fase.data)
            db_session.add(tipo)
            db_session.commit()
            
            #almacena los atributos del tipo Item
            lista= form.lista_atributo.data
            for atr in lista:
                att = TItemAtributo(tipo.id,atr)
                db_session.add(att)
                db_session.commit()
            flash('El Tipo de Item ha sido registrado con exito','info')
            return redirect('/tipoItem/administrartipoItem') 
        except DatabaseError, e:
            if e.args[0].find('duplicate key value violates unique')!=-1:
                flash('Clave unica violada por favor ingrese otro CODIGO de Tipo de Item' ,'error')
            else:
                flash('Error en la Base de Datos' + e.args[0],'error')
            return render_template('tipoItem/nuevotipoItem.html', form=form)
    else:
        flash_errors(form) 
        return render_template('tipoItem/nuevotipoItem.html', form=form)

@app.route('/tipoItem/editartipoItem', methods=['GET', 'POST'])
def editartipoItem():
    """ Funcion para editar registros de la tabla de Tipo de Item""" 
    if not current_user.is_authenticated():
        flash('Debe loguearse primeramente!!!!', 'loggin')
        return render_template('index.html')
    
    permission =UserPermission('LIDER PROYECTO', int(session['pry']))
    if permission.can()==False:
        flash('No posee los permisos suficientes para realizar la operacion', 'info')
        return render_template('index.html') 
     
    ti = db_session.query(TipoItem).filter_by(codigo=request.args.get('codigo')).first() 
    form = TipoItemFormulario(request.form,ti)  
    tipoItem = db_session.query(TipoItem).filter_by(codigo=form.codigo.data).first()
    form.id_fase.choices= [(f.id, f.nombre) for f in db_session.query(Fase).from_statement("select * from fase where id_proyecto="+str(session['pry'])+" and (estado='I' or estado='P') order by nombre ").all()] 
    fa = tipoItem.id_fase
    
    atributos= db_session.query(Atributo).from_statement("Select a.* from atributo a , tipo_item ti, titem_atributo ta where ta.id_atributo= a.id and ta.id_tipo_item = ti.id and ti.id = '"+tipoItem.id.__repr__()+"'").all()
    form.lista_atributo.choices = [(f.id, f.nombre) for f in atributos ]
    
    items= db_session.query(Item).filter_by(id_tipo_item=tipoItem.id).first()
    #se verifica si el tipo de item esta siendo utilizado, en tal caso no podra ser editado
    if items !=  None :
        flash('El Tipo de Item no puede ser editado, ya que esta siendo utilizado por algun Item!','info')
        return render_template('tipoItem/administrartipoItem.html')
    if request.method == 'POST' and form.validate():
        items= db_session.query(Item).filter_by(id_tipo_item= tipoItem.id).first()
        #se verifica si el tipo de item esta siendo utilizado, en tal caso no podra ser editado 
        if items !=  None :
            flash('El Tipo de Item no puede ser modificado, ya que esta siendo utilizado por algun item!','error')
            return render_template('tipoItem/editartipoItem.html', form=form)
        try:          
            form.populate_obj(tipoItem)
            db_session.merge(tipoItem)
            db_session.commit()
            flash('El tipo item ha sido editado con exito','info')
            return redirect('/tipoItem/administrartipoItem')
        except DatabaseError, e:
            flash('Error en la Base de Datos' + e.args[0],'error')
            return render_template('tipoItem/editartipoItem.html', form=form)
    else:
        flash_errors(form)
        return render_template('tipoItem/editartipoItem.html', form=form)
    
@app.route('/tipoItem/eliminartipoItem', methods=['GET', 'POST'])
def eliminartipoItem():
    """ Funcion para eliminar registros de la tabla de Tipo de Item"""
    if not current_user.is_authenticated():
        flash('Debe loguearse primeramente!!!!', 'loggin')
        return render_template('index.html')
    
    permission =UserPermission('LIDER PROYECTO', int(session['pry']))
    if permission.can()==False:
        flash('No posee los permisos suficientes para realizar la operacion', 'info')
        return render_template('index.html')  
    
    try:
        cod = request.args.get('cod')
        tipoItem = db_session.query(TipoItem).filter_by(codigo=cod).first()  
        items= db_session.query(Item).filter_by(id_tipo_item=tipoItem.id).first()
        cant = db_session.query(TItemAtributo).filter_by(id_tipo_item=tipoItem.id).count()
        cnt = 0
        #se verifica si el tipo de item esta siendo utilizado, en tal caso no podra ser eliminado 
        if items !=  None :
            flash('El Tipo de Item no puede ser eliminado, ya que esta siendo utilizado por algun Item!','info')
            return render_template('tipoItem/administrartipoItem.html')
        while cnt < cant :
            cnt = cnt + 1
            tt = db_session.query(TItemAtributo).filter_by(id_tipo_item=tipoItem.id).first()  
            db_session.delete(tt)
            db_session.commit()
        db_session.delete(tipoItem)
        db_session.commit()
        flash('El tipo item ha sido eliminado con exito','info')
        return redirect('/tipoItem/administrartipoItem')
    except DatabaseError, e:
            flash('Error en la Base de Datos' + e.args[0],'info')
            return render_template('tipoItem/administrartipoItem.html')
    
@app.route('/tipoItem/buscartipoItem', methods=['GET', 'POST'])
def buscartipoItem():
    """ Funcion para buscar registros de la tabla de Tipo de Item""" 
    if not current_user.is_authenticated():
        flash('Debe loguearse primeramente!!!!', 'loggin')
        return render_template('index.html')
    
    permission =UserPermission('LIDER PROYECTO', int(session['pry']))
    if permission.can()==False:
        flash('No posee los permisos suficientes para realizar la operacion', 'info')
        return render_template('index.html')  
    
    valor = request.args['patron']
    parametro = request.args['parametro']
    #init_db(db_session)
    if valor == "" : 
        administrartipoItem()
    if parametro == 'id_fase':
        ti = db_session.query(TipoItem).from_statement("SELECT * FROM tipo_item where "+parametro+" in (SELECT id FROM fase where nombre ilike '%"+valor+"%' and id_proyecto='"+session['pry']+"')").all()
    else:
        ti = db_session.query(TipoItem).from_statement("SELECT * FROM tipo_item where "+parametro+" ilike '%"+valor+"%'").all()
    return render_template('tipoItem/administrartipoItem.html', tipoItems = ti)    
    
    valor = request.args['patron']
    #init_db(db_session)
    r = db_session.query(TipoItem).filter_by(nombre=valor)
    if r == None:
        return 'no existe concordancia'
    return render_template('tipoItem/administrartipoItem.html', tipoItems = r)

@app.route('/tipoItem/buscartipoItem2', methods=['GET', 'POST'])
def buscartipoItem2():
    """ Funcion para buscar registros de la tabla de Tipo de Item""" 
    if not current_user.is_authenticated():
        flash('Debe loguearse primeramente!!!!', 'loggin')
        return render_template('index.html')
    
    permission =UserPermission('LIDER PROYECTO', int(session['pry']))
    if permission.can()==False:
        flash('No posee los permisos suficientes para realizar la operacion', 'info')
        return render_template('index.html')  
    
    valor = request.args['patron']
    parametro = request.args['parametro']
    #init_db(db_session)
    if valor == "" : 
        administrartipoItem()
    if parametro == 'id_fase':
        ti = db_session.query(TipoItem).from_statement("SELECT * FROM tipo_item where "+parametro+" in (SELECT id FROM fase where nombre ilike '%"+valor+"%' )").all()
    else:
        ti = db_session.query(TipoItem).from_statement("SELECT * FROM tipo_item where "+parametro+" ilike '%"+valor+"%'").all()
    return render_template('tipoItem/listartipoItem.html', tipoItems2 = ti)    
    
    valor = request.args['patron']
    #init_db(db_session)
    r = db_session.query(TipoItem).filter_by(nombre=valor)
    if r == None:
        return 'no existe concordancia'
    return render_template('tipoItem/listartipoItem.html', tipoItems2 = r)

@app.route('/tipoItem/administrartipoItem')
def administrartipoItem():
    """ Funcion para listar registros de la tabla de Tipo de Item""" 
    if not current_user.is_authenticated():
        flash('Debe loguearse primeramente!!!!', 'loggin')
        return render_template('index.html')
    
    permission = UserPermission('LIDER PROYECTO', int(session['pry']))
    if permission.can()==False:
        flash('No posee los permisos suficientes para realizar la operacion', 'permiso')
        return render_template('index.html') 

    tipoItems = db_session.query(TipoItem).order_by(TipoItem.nombre)
    return render_template('tipoItem/administrartipoItem.html', tipoItems = tipoItems)

@app.route('/tipoItem/listartipoItem')
def listartipoItem():
    """ Funcion para listar registros de la tabla de Tipo de Item""" 
    if not current_user.is_authenticated():
        flash('Debe loguearse primeramente!!!!', 'loggin')
        return render_template('index.html')
    
    permission =UserPermission('LIDER PROYECTO', int(session['pry']))
    if permission.can()==False:
        flash('No posee los permisos suficientes para realizar la operacion', 'info')
        return render_template('index.html')  
    
    tipoItems2 = db_session.query(TipoItem).order_by(TipoItem.nombre)
    return render_template('tipoItem/listartipoItem.html', tipoItems2 = tipoItems2)

@app.route('/tipoItem/listaatt', methods=['GET', 'POST'])
def listaatt():   
    """ Funcion que lista los atributos posibles a formar parte de un Tipo Item"""     
    if not current_user.is_authenticated():
        flash('Debe loguearse primeramente!!!!', 'loggin')
        return render_template('index.html')
    
    permission =UserPermission('LIDER PROYECTO', int(session['pry']))
    if permission.can()==False:
        flash('No posee los permisos suficientes para realizar la operacion', 'info')
        return render_template('index.html')  
    
    atts = db_session.query(Atributo).from_statement(" select * from atributo " )
    return render_template('tipoItem/listaatt.html', atts = atts)  

@app.route('/lineaBase/agregaritems', methods=['GET', 'POST'])
def agregaritems():   
    """ Funcion que agrega Atributos a un Tipo Item"""
    if not current_user.is_authenticated():
        flash('Debe loguearse primeramente!!!!', 'loggin')
        return render_template('index.html')
    
    permission =UserPermission('LIDER PROYECTO', int(session['pry']))
    if permission.can()==False:
        flash('No posee los permisos suficientes para realizar la operacion', 'info')
        return render_template('tipoItem/administrartipoItem.html') 
    
    selectedatt=  request.args.get('ti')    
    atts = db_session.query(Atributo).from_statement(" select * from atributo  " )
    return render_template('tipoItem/listaatt.html', atts = atts)  

@app.route('/tipoItem/importartipoItem', methods=['GET', 'POST'])
def importartipoItem():
    """ Funcion para importar registros a la tabla de Tipo de Item"""
    if not current_user.is_authenticated():
        flash('Debe loguearse primeramente!!!!', 'loggin')
        return render_template('index.html')
    
    permission =UserPermission('LIDER PROYECTO', int(session['pry']))
    if permission.can()==False:
        flash('No posee los permisos suficientes para realizar la operacion', 'info')
        return render_template('tipoItem/administrartipoItem.html')  
    #init_db(db_session)   
    ti = db_session.query(TipoItem).filter_by(codigo=request.args.get('codigo')).first() 
    form = TipoItemFormulario(request.form,ti)  
    tipoItem = db_session.query(TipoItem).filter_by(codigo=form.codigo.data).first()
    fase_selected= db_session.query(Fase).filter_by(id=form.id_fase.data).first()  
    #form.id_fase.data= fase_selected.nombre
    #atributos= db_session.query(Atributo).from_statement("Select a.* from atributo a , tipo_item ti, titem_atributo ta where ta.id_atributo= a.id and ta.id_tipo_item = ti.id and ti.id = '"+session['tip']+"'").all()
    atributos= db_session.query(Atributo).from_statement("Select a.* from atributo a").all()
    form.lista_atributo.choices = [(f.id, f.nombre) for f in atributos ]
    if request.method == 'POST' and form.validate():        
        try:
            """verifica si la fase esta en un estado inicial la cambia en progreso"""   
            fase_selected = db_session.query(Fase).filter_by(id=form.id_fase.data).first()
            if fase_selected.estado == "I" :
                fase_selected.estado = "P"
                db_session.merge(fase_selected)
                db_session.commit()     
                  
            tipo = TipoItem( form.codigo.data, form.nombre.data, form.descripcion.data, 
                    form.id_fase.data)
            db_session.add(tipo)
            db_session.commit()
        
            """almacena los atributos del tipo Item"""
            lista= form.lista_atributo.data
            for atr in lista:
                att = TItemAtributo(tipo.id,atr)
                db_session.add(att)
                db_session.commit()
            flash('El Tipo de Item ha sido importado con exito','info')
            return redirect('/tipoItem/administrartipoItem') 
        except DatabaseError, e:
            if e.args[0].find('duplicate key value violates unique')!=-1:
                flash('Clave unica violada por favor ingrese otro CODIGO de Tipo de Item' ,'error')
            else:
                flash('Error en la Base de Datos' + e.args[0],'error')
            return render_template('tipoItem/importartipoItem.html', form=form)
    else:
        flash_errors(form) 
        return render_template('tipoItem/importartipoItem.html', form=form)

@app.errorhandler(404)
def page_not_found(error):
    """Lanza un mensaje de error en caso de que la pagina solicitada no exista"""
    return 'Esta Pagina no existe', 404

@app.after_request
def shutdown_session(response):
    """Cierra la sesion de la conexion con la base de datos"""
    db_session.remove()
    return response
