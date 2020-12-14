from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from checkin_system.db import get_db
from checkin_system.auth import login_required

bp = Blueprint('main', __name__, url_prefix='/main')


@bp.route('/home')
@login_required
def home():
    return render_template('home.html.j2')

@bp.route('/employee_info.xml', methods=('GET'))
@login_required
def employee_info(user_id):
    pass

@bp.route('/check_in')
@login_required
def check_in():
    pass

@bp.route('/check_out')
@login_required
def check_out():
    pass

@bp.route('/leave')
@login_required
def leave():
    pass