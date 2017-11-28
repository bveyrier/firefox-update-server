from .. import app
from sqlalchemy import Column, Integer, String, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy_session import flask_scoped_session

_base = declarative_base()
_engine = create_engine(app.config['SQLALCHEMY_DB_URI'])
_session_factory = sessionmaker(bind=_engine)
session = flask_scoped_session(_session_factory, app)


class Update(_base):
    __tablename__ = 'updates'
    id = Column(Integer, primary_key=True)
    filename = Column(String, nullable=False)
    version = Column(String, nullable=False)
    hash_function = Column(String, nullable=False)
    hash_value = Column(String, nullable=False)
    size = Column(String, nullable=False)
    details_url = Column(String, nullable=False)
    patch_type = Column(String, nullable=False)
    update_type = Column(String, nullable=False)

    waves = relationship("Wave", back_populates="update")
    intermediate_updates = relationship("IntermediateUpdate", back_populates="update")

    def __repr__(self):
        return "<Update(id='%s', filename='%s', version='%s')>" % (self.id, self.filename, self.version)


class Wave(_base):
    __tablename__ = 'waves'
    id = Column(Integer, primary_key=True)
    id_update = Column(Integer, ForeignKey('updates.id'))

    update = relationship("Update", back_populates="waves")

    def __repr__(self):
        return "<Wave(id='%s', id_update='%s')>" % (self.id, self.id_update)


class IntermediateUpdate(_base):
    __tablename__ = 'intermediate_updates'
    id = Column(Integer, primary_key=True)
    id_update = Column(Integer, ForeignKey('updates.id'))
    version = Column(String, nullable=False)

    update = relationship("Update", back_populates="intermediate_updates")

    def __repr__(self):
        return "<IntermediateUpdate(id='%s', id_update='%s', version='%s')>" % (self.id, self.id_update, self.version)


if app.config['SQLALCHEMY_DB_DROP']:
    _base.metadata.drop_all(_engine)
    _base.metadata.create_all(_engine)
