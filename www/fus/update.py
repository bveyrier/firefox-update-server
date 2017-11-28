from . import app
from flask import make_response

import fus_database

@app.route('/api/update/')
@app.route('/api/update/<id>')
def update(id=None):
    resp = make_response(app.config['FUS_EMPTY_UPDATE'], 200)
    resp.headers['Content-Type'] = "application/xml"
    return resp
