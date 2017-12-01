from flask import Blueprint

intermediate_update = Blueprint('intermediate_update', __name__)

from . import views
