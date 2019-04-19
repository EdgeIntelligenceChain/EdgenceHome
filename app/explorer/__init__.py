from flask import Blueprint

explorer = Blueprint('explorer', __name__,template_folder='templates',static_url_path='app/explorer/static',static_folder='static')

from . import edgenceExplorer