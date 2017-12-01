from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from flask_sqlalchemy_session import current_session

from ..models import Update


class WaveForm(FlaskForm):
    """
    Form to add or delete a wave
    """
    name = StringField('Name', validators=[DataRequired()])
    update = QuerySelectField(query_factory=lambda: current_session.query(Update).all(), get_label="version")
    submit = SubmitField('Submit')
