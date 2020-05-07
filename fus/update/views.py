from fus.models import Update, IntermediateUpdate, Wave, DownloadTask
from flask import make_response, render_template, redirect, url_for, flash, abort
from flask_sqlalchemy_session import current_session
import requests
from natsort import natsorted, natsort_key
import urllib.request
import hashlib
from html.parser import HTMLParser

from config import Config
from . import update


def make_xml(data):
    resp = make_response(data, 200)
    resp.headers['Content-Type'] = "application/xml"
    return resp


@update.route('/api/update/<wave_id>/<version>')
def check_update(wave_id=None, version=None):
    wave = current_session.query(Wave).filter(wave_id == Wave.id).first()
    if wave != None and wave.update != None:
        intermediate_update = current_session.query(IntermediateUpdate).filter(
            version < IntermediateUpdate.version).all()
        if (intermediate_update != None):
            for up in intermediate_update:
                if natsort_key(version) < natsort_key(up.update.version) < 0:
                    return make_xml(
                        render_template('update/update.xml', update=up.update,
                                        download_path=Config.FUS_DOWNLOAD_URL))
        if natsort_key(version) < natsort_key(wave.update.version):
            return make_xml(
                render_template('update/update.xml', update=wave.update, download_path=Config.FUS_DOWNLOAD_URL))
    return make_xml(Config.FUS_EMPTY_UPDATE)


@update.route('/updates')
def list_updates():
    updates = current_session.query(Update).order_by(Update.version).all()
    tasks = current_session.query(DownloadTask).filter(DownloadTask.status != "Done").all()
    return render_template('update/updates.html', updates=updates, title='Updates', tasks=tasks)


def get_latest_update():
    updates = current_session.query(Update).order_by(Update.version).all()
    if not updates:
        return '0'
    tmp = [u.version for u in updates]
    updates = natsorted(tmp)
    return updates[len(updates) - 1]


class MyHTMLParser(HTMLParser):
    @property
    def updates(self):
        return self._updates

    def __init__(self, version_min):
        HTMLParser.__init__(self)
        self._version_min = version_min
        self._updates = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for name, value in attrs:
                if name == "href":
                    value = str.replace(value, "/pub/firefox/releases/", "")
                    value = str.replace(value, "/pub/firefox/", "")
                    value = str.replace(value, "/", "")
                    if value != "" and value != "latest-esr" and natsort_key(value) >  natsort_key(self._version_min):
                        self._updates.append(value)


@update.route('/updates/add')
def add_update():
    response = requests.get(Config.FUS_RELEASE_URL)
    parser = MyHTMLParser(get_latest_update())
    parser.feed(response.text)
    updates = parser.updates
    updates = natsorted(updates)
    return render_template('update/update.html', updates=updates, title='Updates')


def sha256(filename):
    hash_sha256 = hashlib.sha256()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()


from threading import Thread

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
class AsyncUpdateDownload(Thread):
    def __init__(self, version, task_id):
        Thread.__init__(self)
        self._version = version
        self._task_id = task_id
        self.SQLALCHEMY_DATABASE_URI = Config.SQLALCHEMY_DATABASE_URI

    def run(self):
        some_engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
        Session = sessionmaker(bind=some_engine)
        session = Session()
        try:
            task = session.query(DownloadTask).get(self._task_id)
        except:
            return
        try:
            url = '{release_url}{version}/update/win64/fr/firefox-{version}.complete.mar'.format(
                release_url=Config.FUS_RELEASE_URL,
                version=self._version)
            filename = 'firefox-{version}.complete.mar'.format(version=self._version)
            full_filename = '{update_path}{filename}'.format(update_path=Config.FUS_UPDATE_PATH,
                                                             filename=filename)
            response = requests.get(url, stream=True)
            file_size = int(response.headers['Content-Length'])
            file_size_dl = 0
            with open(full_filename, 'wb') as fd:
                for chunk in response.iter_content(chunk_size=8192):
                    file_size_dl += fd.write(chunk)
                    task.result = file_size_dl * 100 / file_size
                    session.commit()
            response.close()
            details_url = 'https://www.mozilla.org/en-US/firefox/{version}/releasenotes/'.format(
                version=self._version.replace("esr", ""))
            u = Update(filename=filename,
                       version=self._version,
                       hash_function='SHA256',
                       hash_value=sha256(full_filename),
                       size=file_size,
                       details_url=details_url,
                       patch_type='complete',
                       update_type='minor')
            task.status = "Done"
            session.add(u)
            session.commit()
        except:
            task.status = "Error"
            task.result = "Error: Unable to download update {version}".format(version=self._version)
            session.commit()


@update.route('/updates/add/<version>')
def download_update(version):
    try:
        task = DownloadTask(status="Processing", version=version)
        current_session.add(task)
        current_session.commit()
        worker = AsyncUpdateDownload(version=version, task_id=task.id)
        worker.start()
        flash("Update download started")
    except:
        flash("Error : Unable to download update")
    return redirect(url_for('update.list_updates'))


@update.route('/updates/delete/<int:id>', methods=['GET', 'POST'])
def delete_update(id):
    update = current_session.query(Update).get(id)
    if update is None:
        abort(404)
    current_session.delete(update)
    current_session.commit()
    flash('You have successfully deleted the update.')
    return redirect(url_for('update.list_updates'))
