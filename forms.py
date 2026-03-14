from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, BooleanField, IntegerField, DateField
from wtforms import validators

class ClienteForm(FlaskForm):
    nombre = StringField('Nombre completo', [
        validators.DataRequired(message="El nombre no puede estar vacío"),
        validators.length(min=3, max=100, message="Mínimo 3 caracteres")
    ])
    direccion = StringField('Dirección de entrega', [
        validators.DataRequired(message="La dirección es obligatoria"),
        validators.length(min=5, max=200, message="Ingresa una dirección válida")
    ])
    telefono = StringField('Número de teléfono', [
        validators.DataRequired(message="El teléfono es obligatorio")
    ])
    fecha = DateField('Fecha del pedido', [
        validators.DataRequired(message="Selecciona una fecha")
    ])

class PizzaForm(FlaskForm):
    tamano = RadioField('Tamaño',
        choices=[('Chica', 'Chica — $40'), ('Mediana', 'Mediana — $80'), ('Grande', 'Grande — $120')],
        validators=[validators.DataRequired(message="Debes seleccionar un tamaño")]
    )
    jamon = BooleanField('Jamón (+$10)')
    pina = BooleanField('Piña (+$10)')
    champinones = BooleanField('Champiñones (+$10)')
    num_pizzas = IntegerField('Cantidad de pizzas', [
        validators.DataRequired(message="Indica cuántas pizzas quieres"),
    ])