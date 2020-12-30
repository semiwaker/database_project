from flask import g
import pymysql

'''里面所有SQL语句都在前面加了个test.xxxx，是因为这样有代码提示，最后会删掉'''

db_password = "123456"


def get_db(name="test"):
    db = pymysql.connect("localhost", "root", db_password, name)
    g.db = db
    return db


def __getResult(cursor):
    results = cursor.fetchall()
    col = cursor.description
    AttrList = [col[i][0] for i in range(len(col))]
    ret = []
    for item in results:
        tmp = {AttrList[i]: item[i] for i in range(len(item))}
        ret.append(tmp)
    return ret


def get_department_list(cursor):
    return [{"id": None, "name": None}]


def get_manager_list(cursor):
    return [{"id": None, "name": None}]


def get_user_data(cursor, user_id):
    return {
        "username": None,
        "name": None,
        "gender": None,
        "birthdate": None,
        "department_id": None,
        "email": None,
        "phone_number": None,
        "id_number": None,
        "level": None,
        "work_status": "in"  # "in" or "out"
    }


def get_password(cursor, userid):
    return ""


def get_id_and_password(cursor, username):
    return (0, "")


def get_reachable_user_ids(cursor, user_id):
    # 查询所有下属用户id，包括自己
    return [user_id]


def get_superior(cursor, user_id):
    return None


def get_leave_list(cursor, user_id):
    # 查询所有下属的未审核的请假申请
    return [
        {
            "leave_no": None,
            "leave_begin": None,
            "leave_end": None,
            "leave_reason": None,
            "apply_day": None
        }
    ]


def get_salary_list(cursor, user_id):
    # 查询所有下属的工资情况，用于发放
    last_salary_no = 0  # 最后一个salary编号, 因为不能缺少是否分发，必须等操作完了再修改最后的salary编号
    return ([
        ()  # departmentID,basicSalary,deduction,realSalary
    ], last_salary_no)


def get_department_info(cursor, department_id):
    return {
        "name": None,
        "manager_id": None,
        "description": None
    }

def get_reminders(cursor, user_id):
    return [{"name":None, "id": None}]

def get_employee_xml(cursor, user_id):
    if user_id is None:
        # return all employee
        pass
    return ""



def check_reviewable(curosr, user_id, leave_no):
    return True


def check_dispensable(curosr, user_id, salary_nos):
    # salary_nos is []
    return True


def check_department_updatable(curosr, user_id, deparment_id):
    return True


def accept_leave(cursor, leave_no):
    pass


def reject_leave(cursor, leave_no):
    pass


def new_employee_id(cursor):
    return None


def new_department_id(cursor):
    # 顺便创建一个只有空信息的部门
    return None


def new_leave_id(cursor):
    return None


def add_new_employee(cursor, data):
    # data = {
    #     "employee_id": ,
    #     "username": ,
    #     "name": ,
    #     "gender": ,
    #     "birthdate": ,
    #     "department_id": ,
    #     "email": ,
    #     "phone_number": ,
    #     "id_number": ,
    #     "password": ,
    #     "level": ,
    #     "entry_date":
    # }
    pass


def add_new_leave(cursor, data):
    # data = {
    #     "user_id": ,
    #     "leave_no": ,
    #     "leave_begin": ,
    #     "leave_end": ,
    #     "leave_reason": ,
    #     "apply_day": ,
    #     "reviewer_id":
    # }
    pass


def add_new_salary(cursor, data):
    # data = [
    #     {
    #         "workTime": ,
    #         "salaryNo": ,
    #         "basicSalary": ,
    #         "deduction": ,
    #         "realSalary": ,
    #         "verifier":
    #     } for salaryNo in g.salaryNos
    # ]
    # 记得更改最后的salayNo
    pass


def update_employee_info(cursor, data):
    # 修改自己
    # data = {
    #     "user_id": ,
    #     "email": ,
    #     "phone_number": ,
    #     "password":
    # }
    #
    # or
    #
    # 修改下属
    # data = {
    #     "user_id":
    #     "name":
    #     "gender":
    #     "age":
    #     "department_id":
    #     "email":
    #     "phone_number":
    #     "id_number":
    #     "level":
    # }
    pass


def update_department_info(cursor, data):
    # data = {
    #     "department_id": ,
    #     "name": ,
    #     "manager": ,
    #     "description":
    # }
    pass


def check_in(cursor, user_id, in_time, late):
    # 缺席怎么办？
    pass


def check_out(cursor, user_id, out_time, early):
    pass


def delete_department(cursor, department_id):
    pass

def clear_reminder(cursor, user_id):
    pass


def Query_leaveandlate_202001(cursor, topnum=10):
    sql = """with E_leaves(EmployeeID, tot_leaves) as
        (select EmployeeID, sum(Duration)
        from test.LEAVES
        where ApplyStatus = 1 and
            (LeaveBegin<='2020-01-31' and LeaveEnd>='2020-01-01')
        group by EmployeeID),
        E_lates(EmployeeID, tot_lates) as
        (select EmployeeID, sum(Lateornot|LeaveEarlyornot)
        from test.ATTENDENCES
        where Date >= '2020-01-01' and Date <= '2020-01-31'
        group by EmployeeID)
    select Name, tot_leaves+tot_lates LeaveandLate from
    ((E_lates inner join E_leaves on E_lates.EmployeeID = E_leaves.EmployeeID)
    inner join test.EMPLOYEE on E_lates.EmployeeID = test.EMPLOYEE.EmployeeID)
    order by LeaveandLate desc, Name asc LIMIT """ + str(topnum)
    cursor.execute(sql)
    return __getResult(cursor)

# Query 2.1


def Query_MaxVerifier_leaves(cursor):
    sql = """with t(ReviewerID, total) as
            (select ReviewerID, count(*)
            from test.Leaves
            where ApplyStatus = 1
            group by ReviewerID)

            select * from
            test.leaves
            where EmployeeID in
            (select ReviewerID
            from t
            where total = (select max(total) from t))
            order by ApplyDay desc
            """
    cursor.execute(sql)
    return __getResult(cursor)

# Query 2.2


def Query_MaxVerifier_lates(cursor):
    sql = """with t(ReviewerID, total) as
            (select ReviewerID, count(*)
            from test.Leaves
            where ApplyStatus = 1
            group by ReviewerID)

            select * from
            test.ATTENDENCES
            where EmployeeID in
            (select ReviewerID
            from t
            where total = (select max(total) from t)) and (Lateornot|LeaveEarlyornot)
            order by Date desc
            """
    cursor.execute(sql)
    return __getResult(cursor)

# Query 3


def Query_HugeDeduction(cursor, A):
    # 工资发好几次，罚金也罚好几次，这平均是什么范围内啊?
    pass

# Query 4


def Query_MaxRealSalary_2020(cursor):
    sql = """with tmp(Name, CorrespondingTime, RealSalary) as
            (select Name, CorrespondingTime, RealSalary
            from (select * from test.EMPLOYEE
           where Department_ID in
           (select Department_ID
           from test.EMPLOYEE
           group by Department_ID
           having count(EmployeeID)>=10)) as t inner join test.PAYROLL
            on t.EmployeeID = payroll.EmployeeID
            where payroll.CorrespondingTime >= '2020-01-01'
            and payroll.CorrespondingTime <= '2020-12-31')

           select Name, tmp.CorrespondingTime, RealSalary from
           (select CorrespondingTime, max(RealSalary) as maxsalary
           from tmp
           group by CorrespondingTime) as t inner join tmp
           where t.CorrespondingTime = tmp.CorrespondingTime
           and t.maxsalary = tmp.RealSalary"""
    cursor.execute(sql)
    return __getResult(cursor)

# Query 5


def Query_HugeLatingDuration(cursor):
    # 为了方便，要不把跨月份的请假拆成两次请假事件吧
    sql = """select Name, t1.Department_ID, LatesDuration
    from(select Department_ID, avg(LeaveDuration) * 24 as AVG_leaveDuration, month
        from (select employee.EmployeeID, Department_ID,
        sum(Duration) as LeaveDuration, date_format(LeaveBegin, '%Y-%m') as month
            from test.employee inner join test.leaves
            on employee.EmployeeID = leaves.EmployeeID
            where Privateornot = 0
            group by employee.EmployeeID, Department_ID, date_format(LeaveBegin, '%Y-%m')) as t
        group by Department_ID, month) as t1 inner join
        (select employee.EmployeeID, Name, Department_ID, LatesDuration, month from
            (select EmployeeID, sum(TimeMissing) as LatesDuration, date_format(Date, '%Y-%m') as month
            from test.attendences
            group by EmployeeID, date_format(Date, '%Y-%m')) as t3 inner join test.employee
            on t3.EmployeeID = employee.EmployeeID
        ) as t2
        on t1.Department_ID = t2.Department_ID and t1.month = t2.month
        where t1.AVG_leaveDuration <= t2.LatesDuration
    """
    cursor.execute(sql)
    return __getResult(cursor)

# Query 6


def Query_OverruledManyTimes(cursor):
    sql = """with GGperson(EmployeeID, Latetimes, Leavetimes, month) as
            (select t1.EmployeeID, Latetimes, Leavetimes, t1.month
            from(select EmployeeID, sum(Lateornot) as Latetimes, date_format(Date, '%Y-%m') as month
            from test.attendences
            group by EmployeeID, month
            having Latetimes>=2) as t1 inner join
            (select EmployeeID, sum(Privateornot) as Leavetimes, date_format(LeaveBegin, '%Y-%m') as month
            from test.leaves
            where ApplyStatus = 1
            group by EmployeeID, month
            having Leavetimes>=2) as t2
            on t1.EmployeeID = t2.EmployeeID and t1.month = t2.month)

            select employee.NAME, month, Latetimes, Leavetimes, department.Department, t.Name as Verifier_name
            from (((GGperson inner join test.employee
            on GGperson.EmployeeID = employee.EmployeeID) inner join test.department
            on employee.Department_ID = department.Department_ID) inner join test.employee as t
            on Manager_ID = t.EmployeeID)
    """


def Query_SQL(cursor, sql):
    cursor.execute(sql)
    return __getResult(cursor)


def close_db(exception=None):
    db = getattr(g, "db", None)
    if db:
        db.close()


def init_app(app):
    app.teardown_appcontext(close_db)


if __name__ == "__main__":
    db = get_db("test")
    cursor = db.cursor()
    t1 = Query_leaveandlate_202001(cursor)
    t2 = Query_MaxVerifier_leaves(cursor)
    t3 = Query_HugeDeduction(cursor)
    t4 = Query_MaxRealSalary_2020(cursor)
    t5 = Query_HugeLatingDuration(cursor)
    t6 = Query_OverruledManyTimes(cursor)
    close_db(db)
