from flask import Blueprint

battle = Blueprint('battle', __name__, template_folder='battle_templates')

from . import routes