import datetime
import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, Markup
)
from werkzeug.security import check_password_hash, generate_password_hash

from . import db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    cursor = db.get_db().cursor()
    g.department_list = db.get_department_list(cursor)
    if request.method == 'POST':
        data = {
            "employee_id": db.new_employee_id(cursor),
            "username": request.form['username'],
            "name": request.form['name'],
            "gender": request.form['gender'],
            "birthdate": request.form['birthday'],
            "department_id": request.form['department'],
            "email": request.form['email'],
            "phone_number": request.form['phone'],
            "id_number": request.form['id_number'],
            "password": request.form['password'],
            "level": "employee",
            "entry_date": datetime.date.today().strftime("%Y-%m-%d")
        }
        db.add_new_employee(c，cursor, data)
        if not getattr(g, "error", None):
            session.clear()
            session["user_id"], _ = db.get_id_and_password(
                cursor, data["username"])
            return redirect(url_for("main.success"))

    return render_template('auth/register.html.j2')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    error = None
    if request.method == 'POST':
        cursor = db.get_db().cursor()
        username = request.form['username']
        password = request.form['password']

        user_id, true_password = db.get_id_and_password(cursor, username)

        if username is None or user_id is None:
            error = Markup('用户名错误')
        elif password != true_password:
            error = Markup('Wrong password')

        if error is None:
            session.clear()
            session['user_id'] = user_id
            return redirect(url_for('main.home'))

    return render_template('auth/login.html.j2', error=error)


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is not None:
        cursor = db.get_db().cursor()

        data = db.get_user_data(cursor, user_id)

        if getattr(g, "error", None):
            print(g.error)

        g.user_id = user_id
        g.username = data["username"]
        g.user_level = data["level"]
        g.department_id = data["department_id"]
        g.work_status = data["work_status"]
        if g.user_level != "employee":
            g.reminder_num = len(db.get_reminders(cursor, g.user_id))
            g.leave_num = len(db.get_leave_list(cursor, g.user_id))
        if g.user_level == "admin":
            g.department_list = db.get_department_list(cursor)


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.home'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if getattr(g, "user_id", None) is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
