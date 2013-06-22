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

@app.route('/diagramar', methods=['GET', 'POST'])
def diagramar():
    """ Funcion que se encarga de construir el grafo"""   
    #grafo = pydot.Dot(graph_type='digraph', size = "8, 16")
   
    graph = pydot.Dot(graph_type='digraph')
    for i in range(3):
        edge = pydot.Edge("king", "lord%d" % i)
        graph.add_edge(edge)

    vassal_num = 0
    for i in range(3):        
        for j in range(2):
            edge = pydot.Edge("lord%d" % i, "vassal%d" % vassal_num)
            graph.add_edge(edge)
            vassal_num += 1
            
    filename=os.path.join(cur_dir, cur_dir + '/static/graficos/grafo.png')
    graph.write_png(filename)
    results = open(filename ,'rb').read()
    generator = (cell for row in results
                    for cell in row) 
    return Response(generator,
                       mimetype='image/png',
                       headers={"Content-Disposition":
                                    "attachment;filename={0}".format('grafo.png')}) 
    #return render_template('/graficar/hacer_grafo.html')


@app.route('/graficar/hacer_grafo', methods=['GET', 'POST'])
def hacer_grafo(): 
    
    return render_template('/graficar/hacer_grafo.html')
   
   
#    results = a_bajar.archivo  
#    generator = (cell for row in results
#                    for cell in row) 
#    #flash(u'Bajando archivo: {0}'.format(a_bajar.nombre))
#    return Response(generator,
#                       mimetype=a_bajar.mime,
#                       headers={"Content-Disposition":
#                                    "attachment;filename={0}".format(a_bajar.nombre)}) 
#    
 
 