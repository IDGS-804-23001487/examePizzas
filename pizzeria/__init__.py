from flask import Blueprint

pizzeria = Blueprint(
    'pizzeria',
    __name__,
    template_folder='templates',
    static_folder='static')
from . import routes