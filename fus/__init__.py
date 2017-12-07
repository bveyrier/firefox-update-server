from flask import Flask
from flask_sqlalchemy_session import flask_scoped_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from flask_bootstrap import Bootstrap

from config import app_config

Base = declarative_base()


def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])

    Bootstrap(app)

    _engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    _session_factory = sessionmaker(bind=_engine)
    flask_scoped_session(_session_factory, app)

    from fus import models

    if app.config['SQLALCHEMY_DATABASE_DROP']:
        Base.metadata.drop_all(_engine)
        Base.metadata.create_all(_engine)

    from .update import update as update_blueprint
    app.register_blueprint(update_blueprint)

    from .wave import wave as wave_blueprint
    app.register_blueprint(wave_blueprint)

    from .intermediate_update import intermediate_update as intermediate_update_blueprint
    app.register_blueprint(intermediate_update_blueprint)

    return app
