import flask, flask.views
import os
from com.py.sap.util.database import init_db,engine
from sqlalchemy.orm import scoped_session, sessionmaker
from com.py.sap.adm.mod.Usuario import Usuario

app = flask.Flask(__name__)
app.secret_key="sap"
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
#users = {'raquel':'raquel'} flask.render_template('index.html')

class Main(flask.views.MethodView):
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
            flask.flash("Usuario o Password Incorrecto")
        else:
            flask.session['username'] = username
        return flask.redirect(flask.url_for('index'))



@app.route('/logout')
def logout():  
        flask.session.pop('username', None)
        return flask.redirect(flask.url_for('index'))

@app.route('/administrarRol')
def administrarRol():  
        return flask.render_template('administrarRol.html')
        
app.add_url_rule('/',
                 view_func= Main.as_view('index'),
                 methods=["GET","POST"])


app.debug = True
app.run()