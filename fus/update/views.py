from fus.models import Update, IntermediateUpdate, Wave
from flask import make_response, render_template, redirect, url_for, flash, abort
from flask_sqlalchemy_session import current_session

from fus.utils.natsort import natsorted, natcmp
import urllib2
import hashlib
from HTMLParser import HTMLParser

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
                if natcmp(version, up.update.version) < 0:
                    return make_xml(
                        render_template('update/update.xml', update=up.update,
                                        download_path=Config.FUS_DOWNLOAD_URL))
        if natcmp(version, wave.update.version) < 0:
            return make_xml(
                render_template('update/update.xml', update=wave.update, download_path=Config.FUS_DOWNLOAD_URL))
    return make_xml(Config.FUS_EMPTY_UPDATE)


@update.route('/updates')
def list_updates():
    updates = current_session.query(Update).order_by(Update.version).all()
    return render_template('update/updates.html', updates=updates, title='Updates')


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
                    if value != "" and value != "latest-esr" and natcmp(value, self._version_min) > 0:
                        self._updates.append(value)


@update.route('/updates/add')
def add_update():
    try:
        response = urllib2.urlopen(Config.FUS_RELEASE_URL)
        html = response.read()
        parser = MyHTMLParser(get_latest_update())
        parser.feed(html)
        updates = parser.updates
        updates = natsorted(updates)
        return render_template('update/update.html', updates=updates, title='Updates')
    except:
        flash("Error : Unable to contact Mozzila servers")
    return redirect(url_for('update.list_updates'))


def sha256(filename):
    hash_sha256 = hashlib.sha256()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()


@update.route('/updates/add/<version>')
def download_update(version):
    try:
        url = '{release_url}{version}/update/win32/fr/firefox-{version}.complete.mar'.format(
            release_url=Config.FUS_RELEASE_URL,
            version=version)
        filename = 'firefox-{version}.complete.mar'.format(version=version)
        full_filename = '{update_path}{filename}'.format(update_path=Config.FUS_UPDATE_PATH,
                                                         filename=filename)
        response = urllib2.urlopen(url)
        meta = response.info()
        file_size = int(meta.getheaders("Content-Length")[0])
        file_size_dl = 0
        f = open(full_filename, 'wb')
        while True:
            buffer = response.read(8192)
            if not buffer:
                break
            file_size_dl += len(buffer)
            f.write(buffer)
        f.close()
        details_url = 'https://www.mozilla.org/en-US/firefox/{version}/releasenotes/'.format(
            version=version.replace("esr", ""))
        u = Update(filename=filename,
                   version=version,
                   hash_function='SHA256',
                   hash_value=sha256(full_filename),
                   size=file_size,
                   details_url=details_url,
                   patch_type='complete',
                   update_type='minor')
        current_session.add(u)
        current_session.commit()
        flash("Update successfully downloaded")
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
