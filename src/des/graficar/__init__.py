from UserPermission import UserPermission
from adm.mod.Permiso import Permiso
from adm.mod.Recurso import Recurso
from adm.mod.Usuario import Usuario
from des.mod.Atributo import Atributo
from adm.mod.Proyecto import Proyecto
from des.mod.Fase import Fase
from des.mod.Item import Item
from des.mod.LbItem import LbItem
from flask import Response
from des.mod.TItemAtributo import TItemAtributo 
from des.mod.TipoItem import TipoItem
from flask import Flask, request, redirect, url_for, flash, session, \
    render_template
import flask.views
from ges.mod.LineaBase import LineaBase
from ges.mod.Relacion import Relacion
from ges.mod.TipoRelacion import TipoRelacion
from loginC import app
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import scoped_session, sessionmaker
from util.database import init_db, engine
import pydot
import os


cur_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

class Graficar(flask.views.MethodView):
    def get(self):
        return flask.render_template('graficar.html')
    
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ), 'error')


@app.route('/diagramarSistema', methods=['GET', 'POST'])
def diagramarSistema():
    """ Funcion que se encarga de construir el grafo"""   
    nodos_explorados=[]
    aristas_exploradas= []    
    grafo = pydot.Dot(graph_type='digraph', rankdir="LR", label= "GRAFICO DEL SISTEMA SAP ")
    
    cluster_f1=pydot.Cluster('Fase_1',label='Fase_1', fillcolor= color(1))
    cluster_f2= pydot.Cluster('Fase_2',label='Fase_2',fillcolor= color(2))
    cluster_f3= pydot.Cluster('Fase_3',label='Fase_3',fillcolor= color(3))
    cluster_f4= pydot.Cluster('Fase_4',label='Fase_4',fillcolor= color(4)) 
    fases= db_session.query(Fase).from_statement("select * from fase where id_proyecto = "+str(session['pry'])+" order by nro_orden").all()        
    
    nodos_explorados=[]
    aristas_exploradas= []
    for fase in fases:        
        items_fase = db_session.query(Item).from_statement("Select it.*  from item it, " + 
                        " (Select  i.codigo cod, max(i.version) vermax from item i, fase f  where i.id_fase = f.id " + 
                        " and f.id_proyecto = " + str(session['pry']) + "  group by codigo order by 1 ) s " + 
                        " where it.codigo = cod and it.version= vermax and it.estado != 'E' and it.id_fase= "+str(fase.id))
        
        for nodo in items_fase:                
                nodos_explorados.append(nodo) 
                nombre_nodo = nodo.codigo    
                col= color(nodo.itemfase.nro_orden)               
                n = pydot.Node(nombre_nodo, style="filled", fillcolor = col)   
                #recorrer hijos
                if obtenerItemsHijoSucesor(nodo.id) != None:
                    for arista in obtenerRelacionesHijoSucesor(nodo.id):
                        if arista not in aristas_exploradas:                            
                            aristas_exploradas.append(arista)
                            nombre_a = arista.relacionitem_duenho.codigo 
                            col = color(arista.relacionitem_duenho.itemfase.nro_orden)                                        
                            n_a = pydot.Node(nombre_a, style="filled", fillcolor = col)
                            nodos_explorados.append(arista.relacionitem_duenho)
                            grafo.add_edge(pydot.Edge(n,n_a))
            
                #recorrer padres
                if obtenerItemsPadreAncestro(nodo.id)!=None:         
                    for aristaPadre in obtenerRelacionesPadreAncestro(nodo.id):
                        if aristaPadre not in aristas_exploradas :
                            aristas_exploradas.append(aristaPadre)
                            nombre_b = aristaPadre.relacionitem.codigo 
                            col = color(aristaPadre.relacionitem.itemfase.nro_orden)            
                            n_b = pydot.Node(nombre_b, style="filled", fillcolor = col)
                            nodos_explorados.append(aristaPadre.relacionitem)
                            grafo.add_edge(pydot.Edge(n_b,n ))
    
    
    for fase in fases:        
        items_fase = db_session.query(Item).from_statement("Select it.*  from item it, " + 
                        " (Select  i.codigo cod, max(i.version) vermax from item i, fase f  where i.id_fase = f.id " + 
                        " and f.id_proyecto = " + str(session['pry']) + "  group by codigo order by 1 ) s " + 
                        " where it.codigo = cod and it.version= vermax and it.estado != 'E' and it.id_fase= "+str(fase.id) )        
        for nodo in items_fase:              
                print nodo
                print nodo.itemfase.nro_orden
                col= color(nodo.itemfase.nro_orden)              
                nombre_nodo = nodo.codigo         
                if nodo.itemfase.nro_orden== 1 :         
                    cluster_f1.add_node(pydot.Node(nombre_nodo, style="filled", fillcolor = col))
                elif  nodo.itemfase.nro_orden== 2 :   
                    cluster_f2.add_node(pydot.Node(nombre_nodo, style="filled", fillcolor = col))
                elif nodo.itemfase.nro_orden == 3:
                    cluster_f3.add_node(pydot.Node(nombre_nodo, style="filled", fillcolor = col))
                else:   
                    cluster_f4.add_node(pydot.Node(nombre_nodo, style="filled", fillcolor = col))    
                    

    grafo.add_subgraph(cluster_f1)
    grafo.add_subgraph(cluster_f2)
    grafo.add_subgraph(cluster_f3)
    grafo.add_subgraph(cluster_f4)
  
    filename=os.path.join(cur_dir, cur_dir + '/static/graficos/grafo.png')
    grafo.write_png(filename)
    results = open(filename ,'rb').read()
    generator = (cell for row in results
                    for cell in row) 
    
    return Response(generator,
                       mimetype='image/png',
                       headers={"Content-Disposition":
                                    "attachment;filename={0}".format('grafo.png')}) 


 
@app.route('/graficar/hacer_grafo', methods=['GET', 'POST'])
def hacer_grafo():     
    return render_template('/graficar/hacer_grafo.html')
   
  
def color(orden):
    """
    Determina el color que debe tener un item para la representacion grafica
    del costo de impacto basado en el orden de la fase a la que pertenece.
    """
    colores = ["lightgrey", "pink", "green", "yellow", "orange", "purple", \
               "blue", "gray", "brown"]
    if cantidadFase() > len(colores):
        return colores[0]
    else:
        return colores[int(orden) -1]    


def obtenerItem(id_item):
    item = db_session.query(Item).filter_by(id=id_item).first()
    return item
    

def obtenerItemsHijoSucesor(id_item):     
    """obtiene la lista actualizada de los item hijo/sucesores dado un item """
    list_item_hijos = db_session.query(Item).from_statement(" select * from item where id in ( select r.id_item_duenho   from item i, relacion r "+
                                                            " where i.id = r.id_item and r.id_item = "+str(id_item)+" and r.estado = 'A' ) ")
    return list_item_hijos


def obtenerRelacionesHijoSucesor(id_item):
    """"obtiene la lista actualizada de las relaciones hijo/sucesor dado un item"""
    list_relac_hijos = db_session.query(Relacion).from_statement("select * from relacion where id in  ( select r.id  from item i, relacion r "+
                                                                 " where i.id = r.id_item  and r.id_item= "+str(id_item)+" and r.estado = 'A') ")
    return list_relac_hijos           


def obtenerItemsPadreAncestro(id_item):    
    """"Obtiene la lista de items actualizada de padres/ancestros dado un item"""
    list_item_padres = db_session.query(Item).from_statement(" select * from item where id in ( select r.id_item  from item i, relacion r "+
                                                            " where i.id = r.id_item_duenho and r.id_item_duenho= "+str(id_item)+" and r.estado = 'A' ) ")
    return list_item_padres 


def obtenerRelacionesPadreAncestro(id_item):
    """Obtiene la lista de relaciones padre/ancestro actualizada dado un item"""
    list_relac_padres = db_session.query(Relacion).from_statement("select * from relacion where id in  ( select r.id  from item i, relacion r "+ 
                                                           " where i.id = r.id_item_duenho and r.id_item_duenho=  "+str(id_item)+" and r.estado = 'A') ")
    return list_relac_padres


def cantidadFase():
    """Proporciona la cantidad de fases del proyecto"""    
    fase= db_session.query(Fase).filter_by(id_proyecto= session['pry'] ).all()
    count= 0
    for  f in fase :
        count= count+1
    return count    
    
          
                
 