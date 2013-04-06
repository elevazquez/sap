from wtforms import Form, TextField, validators

class RolFormulario(Form):
    codigo = TextField('Codigo', [validators.Length(min=1, max=50), validators.Required()])
    descripcion = TextField('Descripcion', [validators.Length(min=2, max=100)])
