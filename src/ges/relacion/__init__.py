from loginC import app
from util.database import init_db, engine
from sqlalchemy import distinct, or_
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import Flask, render_template, request, redirect, url_for, flash, session
from ges.mod.Relacion import Relacion
from des.mod.Fase import Fase
from adm.mod.Proyecto import Proyecto
from des.mod.Item import Item
from ges.relacion.RelacionFormulario import RelacionFormulario
from ges.mod.TipoRelacion import TipoRelacion
import flask, flask.views
from UserPermission import *
import os
import datetime

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
class RelacionControlador(flask.views.MethodView):
    def get(self):
        return flask.render_template('relacion.html')

def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ),'error')
 
@app.route('/relacion/nuevarelacion', methods=['GET', 'POST'])
def nuevarelacion():
    """ Funcion para agregar registros a la tabla relacion"""
    #===========================================================================
    # permission = UserPermission('administrador')
    # if permission.can():
    #===========================================================================
    codItem = request.args.get('cod_item')
    codItem2 = request.args.get('cod_item2')
    #===========================================================================
    # Si no hay ningun item seleccionado muestra todos los items que pertenecen a 
    # un proyecto, caso contrario muestra todos los items de la misma fase o fase
    # Siguiente, recordar que el duenho de la relacion es el hijo/sucesor, es decir, en el
    # if se selecciona al hijo o sucesor
    #===========================================================================
    if codItem == None or codItem == '':
        if codItem2 == None or codItem == '':
            items = getItemByProyecto()
            if 'itemDuenho' in session:
                session.pop('itemDuenho', None)
        else:
            if 'itemDuenho' in session:
                #===============================================================
                # Obtiene los ordenes de fases a la que pertenece cada item
                #===============================================================
                fasePhaAnt = db_session.query(Fase).join(Item, Fase.id == Item.id_fase).filter(Item.id == codItem2).first()
                faseChiSuc = db_session.query(Fase).join(Item, Fase.id == Item.id_fase).filter(Item.id == session['itemDuenho']).first()
                #===============================================================
                # Verifica de que fases son para establecer el tipo de relacion
                #===============================================================
                if fasePhaAnt.nro_orden == faseChiSuc.nro_orden:
                    tipo = db_session.query(TipoRelacion.id).filter_by(codigo='Padre Hijo').first()
                else:
                    tipo = db_session.query(TipoRelacion.id).filter_by(codigo='Antecesor Sucesor').first()
                
                relacion = Relacion(datetime.date.today(), None, tipo, codItem2, session['itemDuenho'], 'A')
                db_session.add(relacion)
                db_session.commit()
                session.pop('itemDuenho',None)
                flash('La relacion ha sido registrado con exito','info')
                return redirect('/relacion/administrarrelacion')
    else:
        items = getItemByProyBefoActFase(codItem)
        if (len(items) > 0):
            session['itemDuenho'] = codItem
            item = db_session.query(Item).filter_by(id=codItem).first()
            return render_template('relacion/nuevarelacionpaso2.html', items = items, firstItem = item)
        else:
            flash('El item no tiene posibles antecesores o padres','info')
            return redirect('/relacion/administrarrelacion')
    return render_template('relacion/nuevarelacion.html', items = items)
    #===========================================================================
    # else:
    #    return 'sin relacions'
    #===========================================================================

@app.route('/relacion/editarrelacion', methods=['GET', 'POST'])
def editarrelacion():
    #init_db(db_session)
    p = db_session.query(Relacion).filter_by(codigo=request.args.get('cod')).first()
    form = RelacionFormulario(request.form,p)
    relacion = db_session.query(Relacion).filter_by(id=form.id.data).first()
    if request.method == 'POST' and form.validate():
        form.populate_obj(relacion)
        db_session.merge(relacion)
        db_session.commit()
        return redirect('/relacion/administrarrelacion')
    else:
        flash_errors(form)
    return render_template('relacion/editarrelacion.html', form=form)

@app.route('/relacion/eliminarrelacion', methods=['GET', 'POST'])
def eliminarrelacion():
    cod = request.args.get('codigo')
    #init_db(db_session)
    relacion = db_session.query(Relacion).filter_by(id=cod).first()
    relacion.estado='E'
    db_session.merge(relacion)
    db_session.commit()
    
    return redirect('/relacion/administrarrelacion')

@app.route('/relacion/buscarrelacion', methods=['GET', 'POST'])
def buscarrelacion():
    valor = request.args['patron']
    parametro = request.args['parametro']
    #init_db(db_session)
    if valor=='' or valor == None:
        return administrarrelacion()
    else:
        if parametro == 'fecha_creacion' or parametro == 'fecha_modificacion':
            consulta = selectRelacionUltimaVersionItem()
            relaciones = consulta.filter(Relacion.id.in_(db_session.query(Relacion.id).from_statement("SELECT * FROM relacion WHERE to_char("+parametro+", 'YYYY-mm-dd') ilike '%"+valor+"%'").all())).all()
            #relaciones = db_session.query(Relacion).from_statement("SELECT * FROM relacion WHERE to_char("+parametro+", 'YYYY-mm-dd') ilike '%"+valor+"%'").all()
        elif parametro == 'id_tipo_relacion':
            consulta = selectRelacionUltimaVersionItem()
            relaciones = consulta.filter(Relacion.id.in_(db_session.query(Relacion.id).from_statement("SELECT * FROM relacion WHERE relacion."+parametro+" IN (SELECT id FROM tipo_relacion WHERE tipo_relacion.codigo ILIKE '%"+valor+"%')").all())).all()
            #relaciones = db_session.query(Relacion).from_statement("SELECT * FROM relacion WHERE relacion."+parametro+" IN (SELECT id FROM tipo_relacion WHERE tipo_relacion.codigo ILIKE '%"+valor+"%')").all()
        elif parametro == 'id_item' or parametro == 'id_item_duenho':
            consulta = selectRelacionUltimaVersionItem()
            relaciones = consulta.filter(Relacion.id.in_(db_session.query(Relacion.id).from_statement("SELECT * FROM relacion WHERE "+parametro+" IN (SELECT id FROM item WHERE codigo ILIKE '%"+valor+"%')").all())).all()
            #relaciones = db_session.query(Relacion).from_statement("SELECT * FROM relacion WHERE "+parametro+" IN (SELECT id FROM item WHERE codigo ILIKE '%"+valor+"%')").all()
            #relaciones = db_session.query(Relacion).from_statement("SELECT * FROM relacion where to_char("+parametro+", '99999') ilike '%"+valor+"%'").all()
            #p = db_session.query(Relacion).from_statement("SELECT * FROM relacion where "+parametro+" = CAST("+valor+" AS Int)").all()
        else:
            return administrarrelacion()
    #p = db_session.query(Relacion).filter(Relacion.codigo.like('%'+valor+'%'))
        return render_template('relacion/administrarrelacion.html', relaciones = relaciones)

@app.route('/relacion/administrarrelacion')
def administrarrelacion():
    #init_db(db_session)
    relaciones = getRelUltiVerEnProg()
    return render_template('relacion/administrarrelacion.html', relaciones = relaciones)

@app.errorhandler(404)
def page_not_found(error):
    """Lanza un mensaje de error en caso de que la pagina solicitada no exista"""
    return 'Esta Pagina no existe', 404

@app.after_request
def shutdown_session(response):
    """Cierra la sesion de la conexion con la base de datos"""
    db_session.remove()
    return response

def getItemByProyecto():
    """ Obtiene los items de un proyecto, para lo cual obtiene el id del proyecto guardado en la session"""
    id_proy =  session['pry']
    items = db_session.query(Item).from_statement("Select it.id  from item it, "+ 
                        " (Select  i.codigo cod, max(i.version) vermax from item i, fase f  where i.id_fase = f.id "+
                        " and f.id_proyecto = "+str(id_proy)+"  group by codigo order by 1 ) s "+
                        " where it.codigo = cod and it.version= vermax and it.estado != 'E' " ).all()
    #items = db_session.query(Item).join(Fase, Fase.id == Item.id_fase).join(Proyecto, Proyecto.id == Fase.id_proyecto).filter(Proyecto.id == id_proy).all()
    return items

def getItemByProyBefoActFase(id_item):
    id_proy = session['pry']
    fase_actual = db_session.query(Fase).join(Item, Item.id_fase == Fase.id).filter(Item.id == id_item).first()
    #print(fase_actual)
    items = db_session.query(Item).join(Fase, Fase.id == Item.id_fase).join(Proyecto, Proyecto.id == Fase.id_proyecto).filter(Proyecto.id == id_proy).filter(Fase.nro_orden <= fase_actual.nro_orden).filter(~Item.id.in_(db_session.query(Relacion.id_item).from_statement("SELECT relacion.id_item from relacion where relacion.id_item_duenho = "+ id_item))).filter(~Item.id.in_(db_session.query(Relacion.id_item).from_statement("SELECT relacion.id_item_duenho from relacion where relacion.id_item = "+ id_item))).filter(Item.id != id_item).filter(Item.id.in_(db_session.query(Item.id).from_statement("Select it.id  from item it, (Select  i.codigo cod, max(i.version) vermax from item i, fase f  where i.id_fase = f.id and f.id_proyecto = "+str(id_proy)+"  group by codigo order by 1 ) s where it.codigo = cod and it.version= vermax and it.estado != 'E' " ))).all()
    #items = db_session.query(Item).join(Fase, Fase.id == Item.id_fase).join(Proyecto, Proyecto.id == Fase.id_proyecto).filter(Proyecto.id == id_proy).filter(Fase.id <= fase_actual).filter(~Item.id.in_(db_session.query(Relacion.id_item).from_statement("SELECT relacion.id_item from relacion where relacion.id_item_duenho = "+ id_item))).filter(~Item.id.in_(db_session.query(Relacion.id_item).from_statement("SELECT relacion.id_item_duenho from relacion where relacion.id_item = "+ id_item))).filter(Item.id != id_item).all()
    return items

def getRelUltiVerEnProg():    
    id_proy = session['pry']
    return db_session.query(Relacion).join(Item, or_(Item.id == Relacion.id_item_duenho, Item.id == Relacion.id_item)).join(Fase, Fase.id == Item.id_fase).join(Proyecto, Proyecto.id == Fase.id_proyecto).filter(Item.id.in_(db_session.query(Item.id).from_statement("Select it.id  from item it, "+ 
                        " (Select  i.codigo cod, max(i.version) vermax from item i, fase f  where i.id_fase = f.id "+
                        " and f.id_proyecto = "+str(id_proy)+"  group by codigo order by 1 ) s "+
                        " where it.codigo = cod and it.version= vermax and it.estado != 'E' " ).all())).filter(Proyecto.id == id_proy).filter(Relacion.estado == 'A').all()

def selectRelacionUltimaVersionItem():
    id_proy = session['pry']
    return db_session.query(Relacion).join(Item, or_(Item.id == Relacion.id_item_duenho, Item.id == Relacion.id_item)).join(Fase, Fase.id == Item.id_fase).join(Proyecto, Proyecto.id == Fase.id_proyecto).filter(Item.id.in_(db_session.query(Item.id).from_statement("Select it.id  from item it, "+ 
                        " (Select  i.codigo cod, max(i.version) vermax from item i, fase f  where i.id_fase = f.id "+
                        " and f.id_proyecto = "+str(id_proy)+"  group by codigo order by 1 ) s "+
                        " where it.codigo = cod and it.version= vermax and it.estado != 'E' " ).all())).filter(Proyecto.id == id_proy).filter(Relacion.estado == 'A')
                        

                
#===============================================================================
# 
# filter(Item.id.in_(db_session.query(Item.id).from_statement("Select it.id  from item it, "+ 
#                        " (Select  i.codigo cod, max(i.version) vermax from item i, fase f  where i.id_fase = f.id "+
#                        " and f.id_proyecto = "+str(id_proy)+"  group by codigo order by 1 ) s "+
#                        " where it.codigo = cod and it.version= vermax and it.estado != 'E' " ))).all()
#===============================================================================