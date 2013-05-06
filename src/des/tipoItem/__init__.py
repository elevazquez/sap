from loginC import app
from flask import session

from util.database import init_db, engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import Flask, render_template, request, redirect, url_for, flash 
from des.mod.TipoItem import TipoItem
from des.mod.Item import Item
from sqlalchemy.exc import DatabaseError
from des.tipoItem.TipoItemFormulario import TipoItemFormulario 
from des.tipoItem.TipoItemFormularioEd import TipoItemFormularioEd 
from des.mod.TItemAtributo import TItemAtributo
from des.mod.Atributo import Atributo
from des.mod.Fase import Fase
import flask, flask.views
from wtforms import widgets
import os

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
class TipoItemControlador(flask.views.MethodView):
    def get(self):
        return flask.render_template('tipoItem.html')
    
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ),'error')
                
""" Funcion para agregar registros a la tabla de Tipo de Item""" 
@app.route('/tipoItem/nuevotipoItem', methods=['GET', 'POST'])
def nuevotipoItem():
    form = TipoItemFormulario(request.form) 
    init_db(db_session)
    form.fase.choices= [(f.id, f.nombre) for f in db_session.query(Fase).filter_by(id_proyecto=session['pry']).order_by(Fase.nombre).all()]
    form.lista_atributo.choices = [(f.id, f.nombre) for f in db_session.query(Atributo).order_by(Atributo.nombre).all()]
    if request.method == 'POST' and form.validate():        
        try:
            """verifica si la fase esta en un estado inicial la cambia en progreso"""   
            fase_selected = db_session.query(Fase).filter_by(id=form.fase.data).first()
            if fase_selected.estado == "I" :
                fase_selected.estado = "P"
                db_session.merge(fase_selected)
                db_session.commit()     
                  
            tipo = TipoItem( form.codigo.data, form.nombre.data, form.descripcion.data, 
                    form.fase.data)
            db_session.add(tipo)
            db_session.commit()
            
            """almacena los atributos del tipo Item"""
            lista= form.lista_atributo.data
            for atr in lista:
                att = TItemAtributo(tipo.id,atr)
                db_session.add(att)
                db_session.commit()
            flash('El Tipo de Item ha sido registrado con exito','info')
            return redirect('/tipoItem/administrartipoItem') 
        except DatabaseError, e:
                flash('Error en la Base de Datos' + e.args[0],'error')
                return render_template('tipoItem/nuevotipoItem.html', form=form)
    else:
        flash_errors(form) 
        return render_template('tipoItem/nuevotipoItem.html', form=form)

@app.route('/tipoItem/editartipoItem', methods=['GET', 'POST'])
def editartipoItem():
    init_db(db_session)   
    ti = db_session.query(TipoItem).filter_by(codigo=request.args.get('codigo')).first() 
    form = TipoItemFormularioEd(request.form,ti)  
    tipoItem = db_session.query(TipoItem).filter_by(codigo=form.codigo.data).first()
    fase_selected= db_session.query(Fase).filter_by(id=tipoItem.id_fase ).first()       
    #form.id_fase.data= fase_selected.nombre
    atributos= db_session.query(Atributo).from_statement("Select a.* from atributo a , tipo_item ti, titem_atributo ta where ta.id_atributo= a.id and ta.id_tipo_item = ti.id and ti.id = '"+tipoItem.id.__repr__()+"'").all()
    form.lista_atributo.choices = [(f.id, f.nombre) for f in atributos ]
    if request.method == 'POST' and form.validate():
       items= db_session.query(Item).filter_by(id_tipo_item= tipoItem.id).first()
       #se verifica si el tipo de item esta siendo utilizado, en tal caso no podra ser editado 
       if items !=  None :
          flash('El Tipo de Item no puede ser modificado, ya que esta siendo utilizado por algun recurso!','error')
          return render_template('tipoItem/editartipoItem.html', form=form)
       try:          
          form.populate_obj(tipoItem)
          tipoItem.id_fase = fase_selected.id          
          db_session.merge(tipoItem)
          db_session.commit()
          return redirect('/tipoItem/administrartipoItem')
       except DatabaseError, e:
          flash('Error en la Base de Datos' + e.args[0],'error')
          return render_template('tipoItem/editartipoItem.html', form=form)
    else:
        flash_errors(form)
        return render_template('tipoItem/editartipoItem.html', form=form)
    


@app.route('/tipoItem/eliminartipoItem', methods=['GET', 'POST'])
def eliminartipoItem():
    try:
        cod = request.args.get('cod')
        init_db(db_session)
        tipoItem = db_session.query(TipoItem).filter_by(codigo=cod).first()  
        items= db_session.query(Item).filter_by(id_tipo_item=tipoItem.id).first()
        cant = db_session.query(TItemAtributo).filter_by(id_tipo_item=tipoItem.id).count()
        cnt = 0
       #se verifica si el tipo de item esta siendo utilizado, en tal caso no podra ser editado 
        if items !=  None :
          flash('El Tipo de Item no puede ser eliminado, ya que esta siendo utilizado por algun recurso!','info')
          return render_template('tipoItem/administrartipoItem.html')
        while cnt < cant :
            cnt = cnt + 1
            tt = db_session.query(TItemAtributo).filter_by(id_tipo_item=tipoItem.id).first()  
            db_session.delete(tt)
            db_session.commit()
        db_session.delete(tipoItem)
        db_session.commit()
        return redirect('/tipoItem/administrartipoItem')
    except DatabaseError, e:
            flash('Error en la Base de Datos' + e.args[0],'info')
            return render_template('tipoItem/administrartipoItem.html')
    
@app.route('/tipoItem/buscartipoItem', methods=['GET', 'POST'])
def buscartipoItem():
    valor = request.args['patron']
    parametro = request.args['parametro']
    init_db(db_session)
    if valor == "" : 
        administrartipoItem()
    if parametro == 'id_fase':
        ti = db_session.query(TipoItem).from_statement("SELECT t.* FROM tipo_item t, fase f where lower(f.nombre)  ilike lower('%"+valor+"%') and t.id_fase= f.id").all()
    else:
        ti = db_session.query(TipoItem).from_statement("SELECT * FROM tipo_item where "+parametro+" ilike '%"+valor+"%'").all()
    return render_template('tipoItem/administrartipoItem.html', tipoItems = ti)    
    
    valor = request.args['patron']
    init_db(db_session)
    r = db_session.query(TipoItem).filter_by(nombre=valor)
    if r == None:
        return 'no existe concordancia'
    return render_template('tipoItem/administrartipoItem.html', tipoItems = r)

@app.route('/tipoItem/administrartipoItem')
def administrartipoItem():
    init_db(db_session)
    tipoItems = db_session.query(TipoItem).order_by(TipoItem.nombre)
    return render_template('tipoItem/administrartipoItem.html', tipoItems = tipoItems)


@app.route('/tipoItem/listartipoItem')
def listartipoItem():
    init_db(db_session)
    tipoItems2 = db_session.query(TipoItem).order_by(TipoItem.nombre)
    return render_template('tipoItem/listartipoItem.html', tipoItems2 = tipoItems2)

""" Funcion para importar registros a la tabla de Tipo de Item""" 
@app.route('/tipoItem/importartipoItem', methods=['GET', 'POST'])
def importartipoItem():
    init_db(db_session)   
    ti = db_session.query(TipoItem).filter_by(codigo=request.args.get('codigo')).first() 
    form = TipoItemFormulario(request.form,ti)  
    tipoItem = db_session.query(TipoItem).filter_by(codigo=form.codigo.data).first()
    fase_selected= db_session.query(Fase).filter_by(id=form.fase.data).first()  
    #form.id_fase.data= fase_selected.nombre
    #atributos= db_session.query(Atributo).from_statement("Select a.* from atributo a , tipo_item ti, titem_atributo ta where ta.id_atributo= a.id and ta.id_tipo_item = ti.id and ti.id = '"+session['tip']+"'").all()
    atributos= db_session.query(Atributo).from_statement("Select a.* from atributo a").all()
    form.lista_atributo.choices = [(f.id, f.nombre) for f in atributos ]
    if request.method == 'POST' and form.validate():        
        try:
            """verifica si la fase esta en un estado inicial la cambia en progreso"""   
            fase_selected = db_session.query(Fase).filter_by(id=form.fase.data).first()
            if fase_selected.estado == "I" :
                fase_selected.estado = "P"
                db_session.merge(fase_selected)
                db_session.commit()     
                  
            tipo = TipoItem( form.codigo.data, form.nombre.data, form.descripcion.data, 
                    form.fase.data)
            db_session.add(tipo)
            db_session.commit()
            
            """almacena los atributos del tipo Item"""
            lista= form.lista_atributo.data
            for atr in lista:
                att = TItemAtributo(tipo.id,atr)
                db_session.add(att)
                db_session.commit()
            flash('El Tipo de Item ha sido importado con exito','info')
            return redirect('/tipoItem/importartipoItem') 
        except DatabaseError, e:
                flash('Error en la Base de Datos' + e.args[0],'error')
                return render_template('tipoItem/importartipoItem.html', form=form)
    else:
        flash_errors(form) 
        return render_template('tipoItem/importartipoItem.html', form=form)

"""Lanza un mensaje de error en caso de que la pagina solicitada no exista"""
@app.errorhandler(404)
def page_not_found(error):
    return 'Esta Pagina no existe', 404

"""Cierra la sesion de la conexion con la base de datos"""
@app.after_request
def shutdown_session(response):
    db_session.remove()
    return response
