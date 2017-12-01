from flask import Blueprint

wave = Blueprint('wave', __name__)

from . import views
