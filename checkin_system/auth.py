import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

# from checkin_system.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    g.department_list = []  # TODO: get department list from DB
    if request.method == 'POST':
        username = request.form['username']
        name = request.form['name']
        gender = request.form['gender']
        birthday = request.form['birthday']
        department_id = request.form['department']
        email = request.form['email']
        phone = request.form['phone']
        id_number = request.form['id_number']
        password = request.form['password']
        # TODO: add to DB
    return render_template('auth/register.html.j2')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        pass
        # username = request.form['username']
        # password = request.form['password']
        # db = get_db()
        # error = None
        # user = db.execute(
        #     'SELECT * FROM user WHERE username = ?', (username,)
        # ).fetchone()

        # if user is None:
        #     error = 'Incorrect username.'
        # elif not check_password_hash(user['password'], password):
        #     error = 'Incorrect password.'

        # if error is None:
        #     session.clear()
        #     session['user_id'] = user['id']
        #     return redirect(url_for('index'))

        # flash(error)

    return render_template('auth/login.html.j2')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    g.user = user_id
    # if user_id is None:
    # else:
    # pass
    # g.user = get_db().execute(
    # 'SELECT * FROM user WHERE id = ?', (user_id,)
    # ).fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        # if g.user is None:
        #     return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
