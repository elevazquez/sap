from flask import Flask, views, current_app, request, session, flash, redirect, url_for, render_template
import os
from flask_principal import Principal, identity_changed, Identity, AnonymousIdentity
from flask_login import LoginManager, login_user, logout_user, login_required
from com.py.sap.util.database import init_db,engine
from sqlalchemy.orm import scoped_session, sessionmaker
from wtforms import Form
from com.py.sap.adm.mod.Usuario import Usuario
from com.py.sap.adm.mod.UsuarioRol import UsuarioRol

app = Flask(__name__)
app.secret_key="sap"

#load the extension
principal = Principal(app)

#===============================================================================
# El login manager contiene el codigo que permite que la aplicacion y Flasklogin trabajen juntos,
# tal como cargar el usuario desde un id, donde enviar los suarios cuando ellos necesiten
# iniciar sesion, y similares.
#===============================================================================
login_manager = LoginManager()
# configurarlo para la aplicacion
login_manager.setup_app(app)

from com.py.sap.adm.rol import *
from com.py.sap.adm.permiso import *
from com.py.sap.adm.proyecto import *
from com.py.sap.des.fase import *
from com.py.sap.adm.usuario import *
from com.py.sap.des.atributo import *
from com.py.sap.des.tipoItem import *
from com.py.sap.des.item import *

def get_resource_as_string(name, charset='utf-8'):
    with app.open_resource(name) as f:
        return f.read().decode(charset)

app.jinja_env.globals['get_resource_as_string'] = get_resource_as_string

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))


#===============================================================================
# Este callback se utiliza para recargar el objeto usuario apartir del 
# ID del usuario almacenado en la sesion.
#===============================================================================
@login_manager.user_loader
def load_user(userid):
    # Return an instance of the User model
    return db_session.query(Usuario).get(userid)

""" Pagina Principal -Login"""
class Main(views.MethodView):
    """ funciones get y post para verificar el login"""
    def get(self):
        return render_template('index.html')
    
    def post(self):
        init_db(db_session)
        if 'logout' in request.form :
            session.pop('username', None)
            return redirect(url_for('index'))
         
        required =['username','passwd']
        for r  in required:
            if r not in request.form:
                flash("Error: {0} es Requerido.".format(r))
                return redirect(url_for('index'))
        username = request.form['username']
        passwd = request.form['passwd'] 
        
        user = db_session.query(Usuario).filter_by(usuario=username,password= passwd ).first() 
        if user == None :
            flash("Usuario o Password Incorrecto", "success")
        else:
            #Keep the user info in the session using Flask-Login
            login_user(user)
            #Tell Flask-Principal the identity changed
            identity_changed.send(current_app._get_current_object(),
                                 identity=Identity(user.id))
            
            is_administrador(user.id)
            session['pry'] = 1
            #===================================================================
            # session['username'] = username
            #===================================================================
        return redirect(url_for('index'))

""" funcion llamada cuando el usuario cierra sesion"""
# el decorator indica que la vista requiere que los usuarios esten logueados
@app.route('/logout')
@login_required
def logout():  
    # Remove the user information from the session
    logout_user()

    #Remove session keys set by Flask-Principal
    for key in ('identity.name', 'identity.auth_type'):
        session.pop(key, None)
    #Tell Flask-Principal the user is anonymous
    identity_changed.send(current_app._get_current_object(),
                         identity=AnonymousIdentity())

    session.pop('is_administrador', None)
    return redirect(url_for('index'))

def is_administrador(userid):
    roles = db_session.query(UsuarioRol).filter_by(id_usuario=userid).all()
    isadmin = False
    for rol in roles:
        if isadmin == False:
            if rol.rol.codigo == 'administrador' :
                session['is_administrador'] = True
                isadmin=True
            else:
                session['is_administrador'] = False
        
app.add_url_rule('/',
                 view_func= Main.as_view('index'),
                 methods=["GET","POST"])


if __name__ == "__main__":
    app.run(debug=True)