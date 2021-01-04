import datetime

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, Markup, Response
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
        data = db.get_user_data(cursor, user_id)
        g.reachable_users.append([user_id, data["name"]])
    # print(g.reachable_users)

    return render_template('home.html.j2')


@bp.route('/employee_info_<user_id>.xml', methods=['GET'])
@login_required
def employee_info(user_id):
    if g.user_level != "admin" and user_id == "all":
        return redirect(url_for("main.denied"))
    cursor = db.get_db().cursor()
    return Response(
        response=Markup(db.get_employee_xml(cursor, user_id)),
        status=200,
        mimetype="application/xml",
        content_type="text/xml; charset=utf-8"
    )


@bp.route('/check_in')
@login_required
def check_in():
    in_time = datetime.datetime.now()
    base = datetime.datetime.today()
    base = datetime.datetime(base.year, base.month, base.day, 9)
    # 我希望这里的late是一个数值类型用来记录迟到了多少分钟
    late = (in_time - base).seconds // 60

    cursor = db.get_db().cursor()
    db.check_in(cursor, g.user_id, in_time, late)

    return redirect(url_for('main.success'))


@bp.route('/check_out')
@login_required
def check_out():
    out_time = datetime.datetime.now()
    base = datetime.datetime.today()
    base = datetime.datetime(base.year, base.month, base.day, 17)
    # 我希望这里的early是一个数值类型用来记录早退了多少分钟
    early = (base - out_time).seconds // 60

    cursor = db.get_db().cursor()
    db.check_out(cursor, g.user_id, out_time, early)
    return redirect(url_for('main.success'))


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
        return redirect(url_for('main.success'))
    return render_template('leave.html.j2')


@bp.route('/leave_review')
@login_required
def leave_review():
    cursor = db.get_db().cursor()
    g.leave_list = db.get_leave_list(cursor, g.user_id)
    return render_template('leave_review.html.j2')


@bp.route('/leave_review/accept/<leave_no>', methods=['POST'])
@login_required
def accept_leave(leave_no):
    cursor = db.get_db().cursor()
    if not db.check_reviewable(cursor, g.user_id, leave_no):
        return redirect(url_for("main.denied"))
    db.accept_leave(cursor, leave_no)
    return leave_review()


@bp.route('/leave_review/reject/<leave_no>', methods=['POST'])
@login_required
def reject_leave(leave_no):
    cursor = db.get_db().cursor()
    if not db.check_reviewable(cursor, g.user_id, leave_no):
        return redirect(url_for("main.denied"))
    db.reject_leave(cursor, leave_no)
    return leave_review()


@bp.route('/salary_dispense', methods=['GET', 'POST'])
@login_required
def salary_dispense():
    if g.user_level == "employee":
        return redirect(url_for("main.denied"))
    cursor = db.get_db().cursor()
    g.salary_list, last_salary_no = db.get_salary_list(cursor, g.user_id)
    g.salaryNos = range(last_salary_no+1, last_salary_no + len(g.salary_list))
    g.salary_list = [[salaryNo, s[0], f"{s[1]}", s[2], s[3], s[4], s[5]]
                     for salaryNo, s in zip(g.salaryNos, g.salary_list)]
    salaryNo2id = {s[0]: s[1]
                   for s in g.salary_list}

    if request.method == 'POST':
        data = [
            {
                'employee_id': salaryNo2id[salaryNo],
                "workTime": request.form["workTime"],
                "payTime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "salaryNo": salaryNo,
                "basicSalary": request.form["basic"+str(salaryNo)],
                "deduction": request.form["deduction"+str(salaryNo)],
                "realSalary": request.form["realSalary"+str(salaryNo)],
                "verifier": g.user_id
            } for salaryNo in g.salaryNos
        ]
        db.add_new_salary(cursor, data)
        return redirect(url_for('main.success'))
    return render_template('salary_dispense.html.j2')


@bp.route('/info_update', methods=['GET', 'POST'])
@login_required
def info_update():
    cursor = db.get_db().cursor()
    info = db.get_user_data(cursor, g.user_id)
    g.email = info["email"]
    g.phone = info["phone_number"]
    msg = None
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
            msg = Markup("修改成功！")
        else:
            msg = Markup("密码错误！")
    return render_template('info_update.html.j2', msg=msg)


@bp.route('/employee_modify/<user_id>', methods=['GET', 'POST'])
@login_required
def employee_modify(user_id):
    cursor = db.get_db().cursor()
    g.reachable_user_ids = db.get_reachable_user_ids(cursor, g.user_id)
    g.reachable_users = [
        {
            "id": i,
            "name": db.get_user_data(cursor, i)['name']
        }
        for i in g.reachable_user_ids
    ]
    g.department_list = db.get_department_list(cursor)
    data = db.get_user_data(cursor, user_id)
    g.user_data = {
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
    msg = None
    succeed = False
    if request.method == "POST":
        if int(user_id) not in g.reachable_user_ids:
            msg = Markup("权限不足，无法修改个人信息！")
        else:
            print(request.form)
            if g.user_level == "admin":
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
            else:
                data = {
                    "user_id": user_id,
                    "name": request.form['name'],
                    "gender": request.form['gender'],
                    "birthdate": request.form['birthday'],
                    "department_id": g.user_data['department'],
                    "email": request.form['email'],
                    "phone_number": request.form['phone'],
                    "id_number": request.form['id_number'],
                    "level": g.user_data["level"]
                }
            db.update_employee_info(cursor, data)
            msg = Markup("修改成功")
            succeed = True
    return render_template('employee_modify.html.j2', msg=msg, succeed=True)


@bp.route('/employee_modify/delete/<user_id>', methods=['POST'])
@login_required
def employee_delete(user_id):
    # (nkc) 为什么点删除员工没进到这个函数...
    cursor = db.get_db().cursor()
    g.reachable_user_ids = db.get_reachable_user_ids(cursor, g.user_id)
    if int(user_id) not in g.reachable_user_ids:
        return redirect(url_for('main.denied'))
    db.delete_user(cursor, user_id)
    return redirect(url_for('main.success'))


@bp.route('/department/<department_id>', methods=['GET', 'POST'])
@login_required
def department(department_id):
    cursor = db.get_db().cursor()
    g.manager_list = db.get_manager_list(cursor)
    g.department_id = department_id
    department_data = db.get_department_info(cursor, department_id)
    g.department_name = department_data["name"]
    g.department_manager_id = department_data["manager_id"]
    g.department_description = department_data["description"]
    msg = None
    if request.method == "POST":
        if not db.check_department_updatable(cursor, g.user_id, department_id):
            msg = Markup("权限不足，无法修改部门信息！")
        else:
            data = {
                "department_id": department_id,
                "name": request.form["department_name"],
                "manager": request.form["manager"],
                "description": request.form["description"],
            }
            db.update_department_info(cursor, data)
            msg = Markup("修改成功！")
    return render_template("department.html.j2", msg=msg)


@bp.route('/add_department')
@login_required
def add_department():
    if g.user_level != "admin":
        return redirect(url_for("main.denied"))
    cursor = db.get_db().cursor()
    department_id = db.new_department_id(cursor)
    return redirect(url_for("main.department", department_id=department_id))


@bp.route('/remove_department/<department_id>')
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


@bp.route('/sql_query/<query_id>', methods=['GET', 'POST'])
@login_required
def sql_query(query_id):
    if g.user_level != 'admin':
        return redirect(url_for('main.denied'))
    cursor = db.get_db().cursor()
    results = None
    summaries = None
    sql_results = None
    last_sql = None
    no_results = None
    query_id = int(query_id)
    query_funcs = {
        1: [db.Query_leaveandlate_202001],
        2: [db.Query_MaxVerifier_lates, db.Query_MaxVerifier_leaves],
        3: [db.Query_HugeDeduction],
        4: [db.Query_MaxRealSalary_2020],
        5: [db.Query_HugeLatingDuration],
        6: [db.Query_OverruledManyTimes]
    }
    query_summaries = {
        1: ["查询结果"],
        2: ["迟到情况", "请假情况"],
        3: ["查询结果"],
        4: ["查询结果"],
        5: ["查询结果"],
        6: ["查询结果"],
    }

    if query_id != 0:
        results = [func(cursor) for func in query_funcs[query_id]]
        summaries = query_summaries[query_id]

    if request.method == 'POST':
        results = [db.Query_SQL(cursor, request.form["sql"])]
        summaries = ["查询结果"]
        last_sql = request.form["sql"]

    if results:
        sql_results = [
            {
                "summary": summary,
                "title": [u for u, v in result[0].items()],
                "content": [[v for u, v in row.items()] for row in result]
            } for result, summary in zip(results, summaries) if result and len(result)
        ]
        no_results = len(sql_results) == 0

    return render_template("sql_query.html.j2", sql_results=sql_results, last_sql=last_sql, no_results=no_results)


@bp.route("/reminder", methods=["GET", "POST"])
@login_required
def reminder():
    cursor = db.get_db().cursor()
    g.reminder_list = db.get_reminders(cursor, g.user_id)
    if request.method == 'POST':
        db.clear_reminder(cursor, g.user_id)
        return redirect(url_for('main.success'))
    return render_template("reminder.html.j2")
