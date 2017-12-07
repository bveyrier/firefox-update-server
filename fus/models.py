from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from fus import Base


class Update(Base):
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


class Wave(Base):
    __tablename__ = 'waves'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    id_update = Column(Integer, ForeignKey('updates.id'))

    update = relationship("Update", back_populates="waves")

    def __repr__(self):
        return "<Wave(id='%s', id_update='%s')>" % (self.id, self.id_update)


class IntermediateUpdate(Base):
    __tablename__ = 'intermediate_updates'
    id = Column(Integer, primary_key=True)
    id_update = Column(Integer, ForeignKey('updates.id'))
    version = Column(String, nullable=False)

    update = relationship("Update", back_populates="intermediate_updates")

    def __repr__(self):
        return "<IntermediateUpdate(id='%s', id_update='%s', version='%s')>" % (self.id, self.id_update, self.version)


class DownloadTask(Base):
    __tablename__ = 'download_tasks'
    id = Column(Integer, primary_key=True)
    version = Column(String, nullable=False)
    status = Column(String, nullable=False)
    result = Column(String)

    def __repr__(self):
        return "<DownloadTask(id='%s', version='%s', status='%s', result='%s')>" % (
        self.id, self.version, self.status, self.result)
