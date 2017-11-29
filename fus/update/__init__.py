from flask import Blueprint

update = Blueprint('update', __name__)

from . import views