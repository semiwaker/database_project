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
