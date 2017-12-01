from fus.models import Wave
from flask import render_template, flash, url_for, redirect, abort
from flask_sqlalchemy_session import current_session

from . import wave
from forms import WaveForm


@wave.route('/waves')
def list_waves():
    waves = current_session.query(Wave).order_by(Wave.name).all()
    return render_template('wave/waves.html', waves=waves, title='Waves')


@wave.route('/waves/add', methods=['GET', 'POST'])
def add_wave(name=None):
    add_wave = True
    form = WaveForm()
    if form.validate_on_submit():
        try:
            wave = Wave(name=form.name.data, update=form.update.data)
            current_session.add(wave)
            current_session.commit()
            flash('You have successfully created a wave')
        except:
            flash('Error : Wave name already exists')
        return redirect(url_for('wave.list_waves'))
    return render_template('wave/wave.html', action='Add', add_wave=add_wave, form=form, title="Add Wave")


@wave.route('/waves/edit/<int:id>', methods=['GET', 'POST'])
def edit_wave(id):
    add_wave = False
    wave = current_session.query(Wave).get(id)
    if wave is None:
        abort(404)
    form = WaveForm(obj=wave)
    if form.validate_on_submit():
        wave.name = form.name.data
        wave.update = form.update.data
        current_session.commit()
        flash('You have successfully edited the wave')
        return redirect(url_for('wave.list_waves'))
    form.name.data = wave.name
    form.update.data = wave.update
    return render_template('wave/wave.html', action='Edit', add_wave=add_wave, form=form, title="Edit Wave")


@wave.route('/waves/delete/<int:id>', methods=['GET', 'POST'])
def delete_wave(id):
    wave = current_session.query(Wave).get(id)
    if wave is None:
        abort(404)
    current_session.delete(wave)
    current_session.commit()
    flash('You have successfully deleted the wave.')
    return redirect(url_for('wave.list_waves'))
