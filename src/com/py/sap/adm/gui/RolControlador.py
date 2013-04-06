from com.py.sap.util.database import init_db,engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import Flask
from com.py.sap.adm.mod.Rol import Rol
app = Flask (__name__)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
# other misc functions
@app.route('/rol')
def add(rol=None):
    print 'antes del init'
    init_db(db_session)
    print 'despues del init'
    db_session.add(Rol('administ', 'adminlocalhost'))
    print 'despues del add'
    db_session.commit()
    print 'despues del commit'
    return 'rol creado'

@app.route('/fil')
def filter1():
    print 'antes del init'
    init_db(db_session)
    print 'despues del init'
    r = db_session.query(Rol).filter_by(codigo='admin').first()
    return '%d, %s, %s' %(r.id, r.codigo, r.descripcion)
    

@app.route('/')
def hello_world():
    add(None)
    return "Hello World!"
 
# url  routing
@app.errorhandler(404)
def page_not_found(error):
    return 'This page does not exist', 404
 
@app.after_request
def shutdown_session(response):
    db_session.remove()
    return response
