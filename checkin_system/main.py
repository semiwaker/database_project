import datetime

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


@bp.route('/employee_info.xml', methods=['GET'])
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


@bp.route('/leave', methods=['GET', 'POST'])
@login_required
def leave():
    if request.method == 'POST':
        leave_begin = request.form['leave_begin']
        leave_end = request.form['leave_end']
        leave_reason = request.form['leave_reason']
        apply_day = datetime.date.today()
        # TODO: add to DB
    return render_template('leave.html.j2')


@bp.route('/leave_review')
@login_required
def leave_review():
    return render_template('leave_review.html.j2')


@bp.route('/leave_review/accept', methods=['POST'])
@login_required
def accept_leave(leave_no):
    pass


@bp.route('/leave_review/reject', methods=['POST'])
@login_required
def reject_leave(leave_no):
    pass


@bp.route('/salary_dispense', methods=['GET', 'POST'])
@login_required
def salary_dispense():
    if request.method == 'POST':
        workTime = request.form["workTime"]
        for salaryNo in g.salaryNos:
            basicSalary = request.form["basic"+str(salaryNo)]
            deduction = request.form["deduction"+str(salaryNo)]
            realSalary = request.form["realSalary"+str(salaryNo)]
            # TODO: add to DB
    return render_template('salary_dispense.html.j2')


@bp.route('/info_update', methods=['GET', 'POST'])
@login_required
def info_update():
    if request.method == 'POST':
        email = request.form["email"]
        phone = request.form["phone"]
        password = request.form["password"]
        old_password = request.form["old_password"]
        # TODO: check old_password and add to DB
    return render_template('info_update.html.j2')


@bp.route('/employee_modify', methods=['GET'])
@login_required
def employee_modify():
    return render_template('employee_modify.html.j2')


@bp.route('/employee_modify/update', methods=['POST'])
@login_required
def employee_modify_update(user_id):
    if request.method == 'POST':
        name = request.form['name']
        gender = request.form['gender']
        age = request.form['age']
        department_id = request.form['department']
        email = request.form['email']
        id_number = request.form['id_number']
        # TODO: add to DB


@bp.route('/department', methods=['GET', 'POST'])
@login_required
def department(department_id):
    g.manager_list = None
    if request.method == "POST":
        department_name = request.form["department_name"]
        manager = request.form["manager"]
        description = request.form["description"]
        # TODO: add to DB
    return render_template("department.html.j2")
