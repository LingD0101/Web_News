from flask import Blueprint

new_blueprint = Blueprint('blue', __name__)

from . import views
