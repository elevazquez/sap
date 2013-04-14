from com.py.sap.util.database import init_db,engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import Flask
#from com.py.sap.adm.mod.Rol import Rol
from com.py.sap.adm.mod.Rol import Rol
from com.py.sap.adm.mod.Proyecto import Proyecto
from com.py.sap.adm.mod.Usuario import Usuario

app = Flask (__name__)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
"""# other misc functions
@app.route('/rol')
def add(rol=None):
    print 'antes del init'
    init_db(db_session)
    print 'despues del init'
    db_session.add(Rol('administr', 'adminlocalhost'))
    print 'despues del add'
    db_session.commit()
    print 'despues del commit'
    return 'rol creado'
"""
# other misc functions
@app.route('/rolp')
def addr(rolp=None):
    init_db(db_session)
#    rel = db_session.query(Rel).filter_by(descripcion='rel').first()
#    print '%d, %s' %(rel.id, rel.descripcion)
#   db_session.add(Rol('cod', 'lider', rel.id))
    db_session.commit()
    return 'rol creado'

@app.route('/p')
def con():
    init_db(db_session)
#    rel = db_session.query(Rel).filter_by(descripcion='rel').first()
#    print '%d, %s' %(rel.id, rel.descripcion)
#    db_session.add(Rol('cod', 'lider', rel))
    db_session.commit()
    return 'rol creado'

@app.route('/cons')
def cons():
    init_db(db_session)
#    rel = db_session.query(Rel).filter_by(descripcion='rel').first()
    rol = db_session.query(Rol).filter_by(codigo='cod').first()
    #print "Resultado %d, %s" %(rel.rels.all().first().id , rol.rels.all().first().descripcion)
    print '%s' %(rol.Rel.descripcion)
    return 'ok'

@app.route('/pry')
def pry():
    init_db(db_session)
    u = db_session.query(Usuario).filter_by(nombre='lila').first()
    db_session.add(Proyecto('nombre', 'descripcion', 'N', 4, '05/08/1988', '05/08/1988', '05/08/1988', u))
    db_session.commit()
    return 'Pry creado'
    
"""
@app.route('/fil')
def filter1():
    print 'antes del init'
    init_db(db_session)
    print 'despues del init'
    r = db_session.query(Rol).filter_by(codigo='admin').first()
    return '%d, %s, %s' %(r.id, r.codigo, r.descripcion)
"""    
@app.route('/')
def hello_world():
    return "Hello World!"
 
# url  routing
@app.errorhandler(404)
def page_not_found(error):
    return 'This page does not exist', 404
 
@app.after_request
def shutdown_session(response):
    db_session.remove()
    return response
 
if __name__ == '__main__':
    app.run()