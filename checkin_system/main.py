import datetime

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from . import db
# from checkin_system.db import get_db
from checkin_system.auth import login_required

bp = Blueprint('main', __name__, url_prefix='/main')


@bp.route('/home')
@login_required
def home():
    cursor = db.get_db().cursor()
    g.reachable_user_ids = db.get_reachable_user_ids(cursor, g.user_id)
    g.reachable_users = []
    for user_id in g.reachable_user_ids:
        data = db.get_user_data(cursor, data)
        g.reachable_users += {
            "user_id": user_id,
            'name': data["name"]
        }
    if g.user_type == "admin":
        g.department_list = db.get_department_list(cursor)
    return render_template('home.html.j2')


@bp.route('/employee_info.xml', methods=['GET'])
@login_required
def employee_info(user_id=None):
    if g.user_type != "admin" and user_id is None:
        return redirect(url_for("main.denied"))
    cursor = db.get_db().cursor()
    return db.get_employee_xml(user_id)


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
        cursor = db.get_db().cursor()
        data = {
            "user_id": g.user_id,
            "leave_no": db.new_leave_id(cursor),
            "leave_begin": request.form['leave_begin'],
            "leave_end": request.form['leave_end'],
            "leave_reason": request.form['leave_reason'],
            "apply_day": datetime.date.today(),
            "reviewer_id": db.get_superior(cursor, g.user_id)
        }
        db.add_new_leave(cursor, data)
    return render_template('leave.html.j2')


@bp.route('/leave_review')
@login_required
def leave_review():
    cursor = db.get_db().cursor()
    g.leave_list = db.get_leave_list(cursor, g.user_id)
    return render_template('leave_review.html.j2')


@bp.route('/leave_review/accept', methods=['POST'])
@login_required
def accept_leave(leave_no):
    cursor = db.get_db().cursor()
    if not db.check_reviewable(cursor, g.user_id, leave_no):
        return redirect(url_for("main.denied"))
    db.accept_leave(cursor, leave_no)


@bp.route('/leave_review/reject', methods=['POST'])
@login_required
def reject_leave(leave_no):
    cursor = db.get_db().cursor()
    if not db.check_reviewable(cursor, g.user_id, leave_no):
        return redirect(url_for("main.denied"))
    db.reject_leave(cursor, leave_no)


@bp.route('/salary_dispense', methods=['GET', 'POST'])
@login_required
def salary_dispense():
    if g.user_level == "employee":
        return redirect(url_for("main.denied"))
    cursor = db.get_db().cursor()
    g.salary_list, last_salary_no = db.get_salary_list(cursor, g.user_id)
    g.salaryNos = range(last_salary_no+1, last_salary_no + len(g.salary_list))
    g.salary_list = [(salaryNo, s[0], s[1], s[2], s[3])
                     for salaryNo, s in zip(g.salaryNos, g.salary_list)]
    if not db.check_dispensable(cursor, g.user_id, g.salaryNos):
        return redirect(url_for("main.denied"))

    if request.method == 'POST':
        data = [
            {
                "workTime": request.form["workTime"],
                "salaryNo": salaryNo,
                "basicSalary": request.form["basic"+str(salaryNo)],
                "deduction": request.form["deduction"+str(salaryNo)],
                "realSalary": request.form["realSalary"+str(salaryNo)],
                "verifier": g.user_id
            } for salaryNo in g.salaryNos
        ]
        db.add_new_salary(cursor, data)
    return render_template('salary_dispense.html.j2')


@bp.route('/info_update', methods=['GET', 'POST'])
@login_required
def info_update():
    cursor = db.get_db().cursor()
    info = db.get_user_data(cursor, g.user_id)
    g.email = info["email"]
    g.phone = info["phone_number"]
    if request.method == 'POST':
        old_password = request.form["old_password"]

        true_password = db.get_password(cursor, g.user_id)

        if true_password == old_password:
            data = {
                "user_id": g.user_id,
                "email": request.form["email"],
                "phone_number": request.form["phone"],
                "password": request.form["password"]
            }
            db.update_employee_info(cursor, data)
        else:
            flash("密码错误！")
    return render_template('info_update.html.j2')


@bp.route('/employee_modify', methods=['GET'])
@login_required
def employee_modify():
    cursor = db.get_db().cursor()
    g.reachable_user_ids = db.get_reachable_user_ids(cursor, g.user_id)
    g.reachable_users = []
    for user_id in g.reachable_user_ids:
        data = db.get_user_data(cursor, data)
        g.reachable_users += {
            "user_id": user_id,
            "name": data['name'],
            "gender": data['gender'],
            "birthday": data['birthdate'],
            "department": data['department_id'],
            "email": data['email'],
            "phone": data['phone_number'],
            "id_number": data['id_number'],
            "level": data["level"]
        }
    return render_template('employee_modify.html.j2')


@bp.route('/employee_modify/update', methods=['POST'])
@login_required
def employee_modify_update(user_id):
    cursor = db.get_db().cursor()
    if user_id not in db.get_reachable_user_ids(cursor, g.user_id):
        flash("权限不足，无法修改个人信息！")
    else:
        data = {
            "user_id": user_id,
            "name": request.form['name'],
            "gender": request.form['gender'],
            "birthdate": request.form['birthday'],
            "department_id": request.form['department'],
            "email": request.form['email'],
            "phone_number": request.form['phone'],
            "id_number": request.form['id_number'],
            "level": request.form["level"]
        }
        db.update_employee_info(cursor, data)


@bp.route('/department', methods=['GET', 'POST'])
@login_required
def department(department_id):
    cursor = db.get_db().cursor()
    g.manager_list = None
    g.department_id = department_id
    department_data = db.get_department_info(cursor, department_id)
    g.department_name = department_data["name"]
    g.department_manager_id = department_data["manager"]
    g.department_description = department_data["description"]
    if request.method == "POST":
        if not db.check_department_updatable(cursor, g.user_id, department_id):
            flash("权限不足，无法修改部门信息！")
        else:
            data = {
                "department_id": department_id,
                "name": request.form["department_name"],
                "manager": request.form["manager"],
                "description": request.form["description"],
            }
            db.update_department_info(cursor, data)
    return render_template("department.html.j2")


@bp.route('/add_department')
@login_required
def add_department():
    if g.user_level != "admin":
        return redirect(url_for("main.denied"))
    cursor = db.get_db().cursor()
    department_id = db.new_department_id(cursor)
    return redirect(url_for("main.department", department_id=department_id))


@bp.route('/remove_department')
@login_required
def remove_department(department_id):
    if g.user_level != "admin":
        return redirect(url_for("main.denied"))
    cursor = db.get_db().cursor()
    db.delete_department(cursor, department_id)
    return redirect(url_for("main.success"))


@bp.route('/success')
def success():
    return render_template("success.html.j2")


@bp.route('/denied')
def denied():
    return render_template("denied.html.j2")
