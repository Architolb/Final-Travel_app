from ast import PyCF_ONLY_AST
from logging import PlaceHolder
from tkinter import Y
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('place', __name__)

@bp.route('/')
def index():
    db = get_db()
    places = db.execute(
        'SELECT p.id, title, body, created, users_id, username'
        ' FROM place p JOIN user u ON p.users_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('place/index.html', places=places)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO place (title, body, users_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('place.index'))

    return render_template('place/create.html')


def get_place(id, check_user=True):
    place = get_db().execute(
        'SELECT p.id, title, body, created, users_id, username'
        ' FROM place p JOIN user u ON p.users_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if place is None:
        abort(404, f"Place id {id} doesn't exist.")

    if check_user and place['user_id'] != g.user['id']:
        abort(403)

    return place

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_place(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Trip name is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE place SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('place.index'))

    return render_template('place/update.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_place(id)
    db = get_db()
    db.execute('DELETE FROM place WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('place.index'))