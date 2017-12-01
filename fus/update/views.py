from fus.models import Update, IntermediateUpdate, Wave
from flask import make_response, render_template
from flask_sqlalchemy_session import current_session

from config import Config
from . import update


def make_xml(data):
    resp = make_response(data, 200)
    resp.headers['Content-Type'] = "application/xml"
    return resp


def greater_than(v1, v2):
    try:
        split_v1 = v1.split('.')
        split_v2 = v2.split('.')
        count = len(split_v1) if len(split_v2) > len(split_v1) else len(split_v2)
        i = 0
        while i < count:
            if int(split_v1[i]) < int(split_v2[i]):
                return False
            if int(split_v1[i]) > int(split_v2[i]):
                return True
            i += 1
        return False if len(split_v2) > len(split_v1) else True
    except:
        return False


@update.route('/api/update/<wave_id>/<version>')
def update(wave_id=None, version=None):
    wave = current_session.query(Wave).filter(wave_id == Wave.id).first()
    if wave != None and wave.update != None:
        intermediate_update = current_session.query(IntermediateUpdate).filter(
            version < IntermediateUpdate.version).all()
        if (intermediate_update != None):
            for up in intermediate_update:
                if not greater_than(version, up.update.version):
                    return make_xml(
                        render_template('update/update.xml', update=up.update,
                                        download_path=Config.FUS_DOWNLOAD_PATH))
        if not greater_than(version, wave.update.version):
            return make_xml(
                render_template('update/update.xml', update=wave.update, download_path=Config.FUS_DOWNLOAD_PATH))
    return make_xml(Config.FUS_EMPTY_UPDATE)
