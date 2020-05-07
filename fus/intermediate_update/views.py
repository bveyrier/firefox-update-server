from fus.models import IntermediateUpdate
from flask import render_template, flash, url_for, redirect, abort
from flask_sqlalchemy_session import current_session

from . import intermediate_update
from .forms import IntermediateUpdateForm


@intermediate_update.route('/intermediate_updates')
def list_intermediate_updates():
    intermediate_updates = current_session.query(IntermediateUpdate).order_by(IntermediateUpdate.version).all()
    return render_template('intermediate_update/intermediate_updates.html', intermediate_updates=intermediate_updates,
                           title='IntermediateUpdate')


@intermediate_update.route('/intermediate_updates/add', methods=['GET', 'POST'])
def add_intermediate_update(name=None):
    add_intermediate_update = True
    form = IntermediateUpdateForm()
    if form.validate_on_submit():
        try:
            intermediate_update = IntermediateUpdate(version=form.version.data, update=form.update.data)
            current_session.add(intermediate_update)
            current_session.commit()
            flash('You have successfully created a intermediate update')
        except:
            flash('Error : Intermediate update already exists')
        return redirect(url_for('intermediate_update.list_intermediate_updates'))
    return render_template('intermediate_update/intermediate_update.html', action='Add',
                           add_wave=add_intermediate_update, form=form, title="Add intermediate update")


@intermediate_update.route('/intermediate_updates/edit/<int:id>', methods=['GET', 'POST'])
def edit_intermediate_update(id):
    add_intermediate_update = False
    intermediate_update = current_session.query(IntermediateUpdate).get(id)
    if intermediate_update is None:
        abort(404)
    form = IntermediateUpdateForm(obj=intermediate_update)
    if form.validate_on_submit():
        intermediate_update.version = form.version.data
        intermediate_update.update = form.update.data
        current_session.commit()
        flash('You have successfully edited the intermediate update')
        return redirect(url_for('intermediate_update.list_intermediate_updates'))
    form.version.data = intermediate_update.version
    form.update.data = intermediate_update.update
    return render_template('intermediate_update/intermediate_update.html', action='Edit',
                           add_wave=add_intermediate_update, form=form, title="Edit Intermediate update")


@intermediate_update.route('/intermediate_updates/delete/<int:id>', methods=['GET', 'POST'])
def delete_intermediate_update(id):
    intermediate_update = current_session.query(IntermediateUpdate).get(id)
    if intermediate_update is None:
        abort(404)
    current_session.delete(intermediate_update)
    current_session.commit()
    flash('You have successfully deleted the intermediate update.')
    return redirect(url_for('intermediate_update.list_intermediate_updates'))
