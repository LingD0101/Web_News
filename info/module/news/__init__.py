from flask import Blueprint

api = Blueprint('blue', __name__)

from . import views
