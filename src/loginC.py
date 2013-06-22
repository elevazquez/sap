from flask import Flask, views, current_app, request, session, flash, redirect, url_for, render_template
#import os
from flask_principal import Principal, identity_changed, Identity, AnonymousIdentity, identity_loaded, RoleNeed, UserNeed, ItemNeed
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from util.database import engine
from sqlalchemy.orm import scoped_session, sessionmaker
import md5
from adm.mod.UsuarioRol import UsuarioRol
from adm.mod.Usuario import Usuario
from ges.mod.SolicitudCambio import SolicitudCambio
from adm.mod.MiembrosComite import MiembrosComite

app = Flask(__name__)
app.secret_key="sap"
app.debug = True

from adm.usuario import *
from adm.rol import *
from adm.permiso import *
from adm.proyecto import *
from adm.miembrosComite import *
from des.fase import *
from des.atributo import *
from des.tipoItem import *
from des.item import *
from des.tipoAtributo import *
from ges.relacion import *
from ges.lineaBase import *
from ges.solicitud import *
from ges.solicitudavotar import *
from ges.calculoImpacto import *
from ges.calculoCosto import *
from adm.recurso import *
from des.graficar import *


#load the extension
principal = Principal(app)

#===============================================================================
# El login manager contiene el codigo que permite que la aplicacion y Flasklogin trabajen juntos,
# tal como cargar el usuario desde un id, donde enviar los usuarios cuando ellos necesiten
# iniciar sesion, y similares.
#===============================================================================
login_manager = LoginManager()
# configurarlo para la aplicacion
login_manager.setup_app(app)

def get_resource_as_string(name, charset='utf-8'):
    with app.open_resource(name) as f:
        return f.read().decode(charset)

app.jinja_env.globals['get_resource_as_string'] = get_resource_as_string
app.jinja_env.add_extension('jinja2.ext.do')

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

#===============================================================================
# Se define la carga de la identidad del usuario y los roles del usuario 
# para las cuestiones de permisos y roles
#===============================================================================
@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    # Set the identity user object
    identity.user = current_user
    
    # Add the UserNeed to the identity
    if hasattr(current_user, 'id'):
        identity.provides.add(UserNeed(current_user.id))
        # Assuming the User model has a list of roles, update the
        # identity with the roles that the user provides
        roles = db_session.query(UsuarioRol).filter_by(id_usuario=current_user.id).all()
        for role in roles:
            if role.id_proyecto == None :
                identity.provides.add(RoleNeed(role.usuariorolrol.codigo))
            else :
                identity.provides.add(ItemNeed(role.usuariorolrol.codigo, int(role.id_proyecto) , 'manage'))
            permisos = db_session.query(Permiso).join(RolPermiso, RolPermiso.id_permiso == Permiso.id).filter(RolPermiso.id_rol == role.id_rol).all()
            for p in permisos:
                identity.provides.add(ItemNeed(p.codigo, p.id_recurso , 'manage'))


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
        #init_db(db_session)
        if 'logout' in request.form :
            session.pop('username', None)
            return redirect(url_for('index'))
         
        required =['username','passwd']
        for r  in required:
            if r not in request.form:
                flash("Error: {0} es Requerido.".format(r))
                return redirect(url_for('index'))
        username = request.form['username']
        #passwd = request.form['passwd']
        # Se un objeto md5 para encriptar la contrasenha del usuario   
        con = md5.new()    
        con.update(request.form['passwd'])
        passwd = con.hexdigest()
        
        user = db_session.query(Usuario).filter_by(usuario=username,password = passwd).first() 
        if user == None :
            flash("Usuario o Password Incorrecto", "success")
        else:
            #Keep the user info in the session using Flask-Login
            login_user(user)
            #Tell Flask-Principal the identity changed
            identity_changed.send(current_app._get_current_object(),
                                 identity=Identity(user.id))
            is_administrador(user.id)
            #session['pry'] = 1
            #===================================================================
            # session['username'] = username
            #===================================================================
                    
            if 'is_administrador' in session:
                if not session['is_administrador']:
                    return redirect(url_for('getProyectoByUsuario', id_usuario = current_user.id))
                else:
                    permission = UserRol('ADMINISTRADOR')
                    session['permission_admin'] = permission
                    return redirect(url_for('getProyectoByUsuario', id_usuario = current_user.id))
            
          
             
            
        return redirect(url_for('index'))

# el decorator indica que la vista requiere que los usuarios esten logueados
@app.route('/logout')
@login_required
def logout():
    """ funcion llamada cuando el usuario cierra sesion"""
    # Remove the user information from the session
    logout_user()

    #Remove session keys set by Flask-Principal
    for key in ('identity.name', 'identity.auth_type'):
        session.pop(key, None)
    #Tell Flask-Principal the user is anonymous
    identity_changed.send(current_app._get_current_object(),
                         identity=AnonymousIdentity())

    session.pop('is_administrador', None)
    session.pop('pry', None)
    session.pop('itemduenho', None)
    session.pop('permission_admin', None)
    session.pop('permiso_lider', None)
    session.pop('proyecto_nombre', None)
    session.pop('is_solicitud',None)
    return redirect(url_for('index'))

def is_administrador(userid):
    roles = db_session.query(UsuarioRol).filter_by(id_usuario=userid).all()
    isadmin = False
    for rol in roles:
        if isadmin == False:
            if rol.usuariorolrol.codigo == 'ADMINISTRADOR' :
                session['is_administrador'] = True
                isadmin=True
            else:
                session['is_administrador'] = False
        
app.add_url_rule('/',
                 view_func= Main.as_view('index'),
                 methods=["GET","POST"])

if __name__ == "__main__":
    app.run(debug=True)
