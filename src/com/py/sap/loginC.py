import flask, flask.views
import os
from com.py.sap.util.database import init_db,engine
from sqlalchemy.orm import scoped_session, sessionmaker
from com.py.sap.adm.mod.Usuario import Usuario
from wtforms import Form

app = flask.Flask(__name__)
app.secret_key="sap"

from com.py.sap.adm.rol import *

def get_resource_as_string(name, charset='utf-8'):
    with app.open_resource(name) as f:
        return f.read().decode(charset)

app.jinja_env.globals['get_resource_as_string'] = get_resource_as_string

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
""" Pagina Principal -Login"""
class Main(flask.views.MethodView):
    """ funciones get y post para verificar el login"""
    def get(self):
        return flask.render_template('index.html')
    
    def post(self):
        init_db(db_session)
        if 'logout' in flask.request.form :
            flask.session.pop('username', None)
            return flask.redirect(flask.url_for('index'))
         
        required =['username','passwd']
        for r  in required:
            if r not in flask.request.form:
                flask.flash("Error: {0} es Requerido.".format(r))
                return flask.redirect(flask.url_for('index'))
        username = flask.request.form['username']
        passwd = flask.request.form['passwd'] 
  
        if db_session.query(Usuario).filter_by(usuario=username,password= passwd ).first() == None :
            flash("Usuario o Password Incorrecto", "success")
        else:
            flask.session['username'] = username
        return flask.redirect(flask.url_for('index'))


""" funcion llamada cuando el usuario cierra sesion"""
@app.route('/logout')
def logout():  
        flask.session.pop('username', None)
        return flask.redirect(flask.url_for('index'))
      
        
app.add_url_rule('/',
                 view_func= Main.as_view('index'),
                 methods=["GET","POST"])


if __name__ == "__main__":
         app.run(debug=True)