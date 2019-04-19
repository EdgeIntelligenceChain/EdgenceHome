from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_caching import Cache

bootstrap = Bootstrap()
moment = Moment()
db = SQLAlchemy()
cache=Cache()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    cache.init_app(app,config={'CACHE_TYPE': 'simple'})

    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)

    # bluePrint registed home and
    from .main import main as main_blueprint
    from .explorer import explorer as explorer_blueprint 
    app.register_blueprint(main_blueprint,url_prefix="")
    app.register_blueprint(explorer_blueprint,url_prefix="/explorer")

    app.config['TEMPLATES_AUTO_RELOAD'] = True

    return app
