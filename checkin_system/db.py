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
    sql = """select Department_ID as id, Department as name
    from test.department"""
    cursor.execute(sql)
    return __getResult(cursor)
    # return [{"id": None, "name": None}]


def get_manager_list(cursor):
    sql = """select EmployeeID as id, name
        from test.employee"""
    cursor.execute(sql)
    return __getResult(cursor)
    # return [{"id": None, "name": None}]


def get_user_data(cursor, user_id):
    sql = """select username, name, gender, birthdate, department_id, E_mail as email,
    phone_number, id_number, level
    from test.employee
    where EmployeeID = """+str(user_id)
    cursor.execute(sql)
    ret_dict = __getResult(cursor)
    ret_dict["work_status"] = "in"
    return ret_dict
    # return {
    #     "username": None,
    #     "name": None,
    #     "gender": None,
    #     "birthdate": None,
    #     "department_id": None,
    #     "email": None,
    #     "phone_number": None,
    #     "id_number": None,
    #     "level": None,
    #     "work_status": "in"  # "in" or "out"
    # }


def get_password(cursor, userid):
    sql = """select password
            from test.employee
            where EmployeeID = """+str(userid)
    cursor.execute(sql)
    result = cursor.fetchall()
    return result[0][0]
    # return ""


def get_id_and_password(cursor, username):
    sql = """select EmployeeID, Password
                from test.employee
                where Username = \'""" + username + "\'"
    cursor.execute(sql)
    result = cursor.fetchall()
    return result[0][0], result[0][1]
    # return (0, "")


def get_department_and_level(cursor, user_id):
    sql = """select level, Department_ID
                from test.employee
                where EmployeeID = """ + str(user_id)
    cursor.execute(sql)
    result = cursor.fetchall()
    level = result[0][0]
    department = result[0][1]
    return department, level


def get_reachable_user_ids(cursor, user_id):
    # 查询所有下属用户id，包括自己
    # (nkc)这里如果要求只用一句SQL语言倒也不是不可以，是我后来此想到的所以先这么写了，不行再改
    department, level = get_department_and_level(cursor, user_id)
    if level == 'employee':
        return [user_id]
    elif level == 'manager':
        sql = """select EmployeeID
            from test.employee
            where Department_ID = """ + str(department)
        cursor.execute(sql)
        results = cursor.fetchall()
        return [item[0] for item in results]
    elif level == 'admin':
        sql = """select EmployeeID
            from test.employee"""
        cursor.execute(sql)
        results = cursor.fetchall()
        return [item[0] for item in results]
    # return [user_id]


def get_superior(cursor, user_id):
    department, level = get_department_and_level(cursor, user_id)
    if level == 'admin':
        return None
    elif level == 'manager':
        sql = """select EmployeeID
                from test.employee
                where Level = \'admin\'"""
        cursor.execute(sql)
        result = cursor.fetchall()
        return result[0][0]
    elif level == 'employee':
        sql = """select Manager_ID
            from test.department
            where Department_ID = """ + str(department)
        cursor.execute(sql)
        result = cursor.fetchall()
        return result[0][0]


def get_leave_list(cursor, user_id):
    # 查询所有下属的未审核的请假申请
    department, level = get_department_and_level(cursor, user_id)
    if level == 'employee':
        return []
    elif level == 'manager':
        sql = """select LeaveNo as leave_no, LeaveBegin as leave_begin, LeaveEnd as leave_end,
            LeaveReason as leave_reason, ApplyDay as apply_day
            from test.leaves, test.employee
            where leaves.EmployeeID = employee.EmployeeID
                and ApplyStatus = \'pending\'
                and Department_ID = """+str(department)+""" 
                and not leaves.EmployeeID = """+str(user_id)
        cursor.execute(sql)
        return __getResult(cursor)
    elif level == 'admin':
        sql = """select LeaveNo as leave_no, LeaveBegin as leave_begin, LeaveEnd as leave_end,
            LeaveReason as leave_reason, ApplyDay as apply_day
            from test.leaves, test.employee
            where leaves.EmployeeID = employee.EmployeeID
                and ApplyStatus = \'pending\'"""
        cursor.execute(sql)
        return __getResult(cursor)

    # return [
    #     {
    #         "leave_no": None,
    #         "leave_begin": None,
    #         "leave_end": None,
    #         "leave_reason": None,
    #         "apply_day": None
    #     }
    # ]


def get_salary_list(cursor, user_id):
    # 查询所有下属的工资情况，用于发放
    # (nkc)又没懂这里的需求QAQ
    last_salary_no = 0  # 最后一个salary编号, 因为不能缺少是否分发，必须等操作完了再修改最后的salary编号
    return ([
        ()  # departmentID,basicSalary,deduction,realSalary
    ], last_salary_no)


def get_department_info(cursor, department_id):
    sql = """select Department as name, manager_id, info as description
            from test.department
            where Department_ID = """ + str(department_id)
    cursor.execute(sql)
    return __getResult(cursor)
    # return {
    #     "name": None,
    #     "manager_id": None,
    #     "description": None
    # }

def get_reminders(cursor, user_id):
    return [{"name":None, "id": None}]

def get_employee_xml(cursor, user_id):
    # (nkc) 之后再写..
    if user_id is None:
        # return all employee
        pass
    return ""


def check_reviewable(cursor, user_id, leave_no):
    department, level = get_department_and_level(cursor, user_id)
    if level == 'admin':
        return True
    elif level == 'employee':
        return False
    sql = '''select leaves.EmployeeID, Department_ID
    from test.leaves, test.employee
    where LeaveNo = '''+str(leave_no)+''' 
        and leaves.EmployeeID = employee.EmployeeID'''
    cursor.execute(sql)
    result = cursor.fetchall()
    employee_id, department_id = result[0][0], result[0][1]
    if user_id == employee_id or department != department_id:
        return False


def check_dispensable(cursor, user_id, salary_nos):
    # (nkc)等确定了薪水发放规则之后写
    # salary_nos is []
    return True


def check_department_updatable(cursor, user_id, deparment_id):
    deparment, level = get_department_and_level(cursor, user_id)
    if level == 'admin' or (level == 'manager' and deparment == deparment_id):
        return True
    return False


def accept_leave(cursor, leave_no):
    # (nkc)还未验证正确性
    sql = '''update test.leaves
    set ApplyStatus = 'accepted'
    where LeaveNo = ''' + str(leave_no)
    cursor.execute(sql)
    g.db.commit()



def reject_leave(cursor, leave_no):
    # (nkc)还未验证正确性
    sql = '''update test.leaves
        set ApplyStatus = 'rejected'
        where LeaveNo = ''' + str(leave_no)
    cursor.execute(sql)
    g.db.commit()


def new_employee_id(cursor):
    sql = '''select LastEmployeeNo + 1
    from test.metadata '''
    cursor.execute(sql)
    result = cursor.fetchall()
    sql = '''update test.metadata
        set LastDepartmentNo = LastDepartmentNo + 1'''
    cursor.execute(sql)
    g.db.commit()
    return result[0][0]


def new_department_id(cursor):
    sql = '''select LastDepartmentNo + 1
    from test.metadata '''
    cursor.execute(sql)
    result = cursor.fetchall()
    ret = result[0][0]
    sql = '''insert into test.department(Department_ID, Department) 
    VALUES ('''+str(ret)+',\'No.'+str(ret+1)+'\')'
    cursor.execute(sql)
    g.db.commit()
    sql = '''update test.metadata
    set LastDepartmentNo = LastDepartmentNo + 1'''
    cursor.execute(sql)
    g.db.commit()
    return ret


def new_leave_id(cursor):
    sql = '''select LastLeaveNo + 1
    from test.metadata '''
    cursor.execute(sql)
    result = cursor.fetchall()
    sql = '''update test.metadata
        set LastLeaveNo = LastLeaveNo + 1'''
    cursor.execute(sql)
    g.db.commit()
    return result[0][0]


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

    # (nkc)还未验证正确性
    tmp = (data['employee_id'], data['name'], data['birthdate'], data['id_number'],
           data['entry_date'], data['username'], data['password'], data['gender'],
           data['phone_number'], data['email'], data['level'], data['department_id'])
    sql = '''insert into test.employee
    (EMPLOYEEID, NAME, BIRTHDATE, ID_NUMBER, ENTRYDATE, USERNAME, PASSWORD, 
    GENDER, PHONE_NUMBER, E_MAIL, LEVEL, DEPARTMENT_ID) 
        VALUES ''' + str(tmp)
    cursor.execute(sql)
    g.db.commit()


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

    # (nkc)还未验证正确性
    not_private = ['因公']
    import datetime
    duration = (datetime.strptime(data['leave_end'],'%Y-%m-%d') -
            datetime.strptime(data['leave_begin'], '%Y-%m-%d')).days
    tmp = (data['user_id'],
           data['leave_no'],
           data['leave_begin'],
           data['leave_end'],
           data['leave_reason'],
           data['leave_reason'] not in not_private,
           data['apply_day'],
           data['reviewer_id'],
           'pending',
           duration
           )
    sql = '''insert into test.leaves
        (EmployeeID, LeaveNo, LeaveBegin, LeaveEnd, LeaveReason, 
        Privateornot, ApplyDay, ReviewerID, ApplyStatus, Duration)
            VALUES ''' + str(tmp)
    cursor.execute(sql)
    g.db.commit()


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
    # salary相关的我都放最后写


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

    # (nkc)还未验证正确性
    # (nkc)Age之后填
    if 'level' in data:
        sql = '''update test.employee 
        set Name = ''' + data['name'] + ''',
        Gender = ''' + data['gender'] + ''',
        Department_ID = ''' + data['department_id'] + ''',
        E_mail = ''' + data['email'] + ''',
        Phone_number = ''' + data['phone_number'] + ''',
        ID_number = ''' + data['id_number'] + ''',
        Level = ''' + data['level'] +''' 
        where EmployeeID = ''' + str(data['user_id'])
    else:
        sql = '''update test.employee 
        set E_mail = ''' + data['email'] + ''',
        Phone_number = ''' + data['phone_number'] + ''',
        Password = ''' + data['password'] + ''' 
        where EmployeeID = ''' + str(data['user_id'])
    cursor.execute(sql)
    g.db.commit()


def update_department_info(cursor, data):
    # data = {
    #     "department_id": ,
    #     "name": ,
    #     "manager": ,
    #     "description":
    # }

    # (nkc)此处是否需要更新这个人的level?
    sql = '''update test.department 
            set Department = ''' + data['name'] + ''',
            Manager_ID = ''' + data['manager'] + ''',
            info = ''' + data['description'] + ''' 
            where Department_ID = ''' + str(data['department_id'])
    cursor.execute(sql)
    g.db.commit()


def check_in(cursor, user_id, in_time, late):
    # 缺席怎么办？
    pass


def check_out(cursor, user_id, out_time, early):
    pass


def delete_department(cursor, department_id):
    sql = '''delete from test.department 
            where Department_ID = ''' + str(department_id)
    cursor.execute(sql)
    g.db.commit()

def clear_reminder(cursor, user_id):
    pass


def Query_leaveandlate_202001(cursor, topnum=10):
    sql = """with E_leaves(EmployeeID, tot_leaves) as
        (select EmployeeID, sum(Duration)
        from test.LEAVES
        where ApplyStatus = \'accepted\' and 
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
            where ApplyStatus = \'accepted\'
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
            where ApplyStatus = \'accepted\'
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
            where ApplyStatus = \'accepted\'
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
    # db = get_db("test")
    db = pymysql.connect("localhost", "root", "", "test")
    cursor = db.cursor()
    # t1 = Query_leaveandlate_202001(cursor)
    # t2 = Query_MaxVerifier_leaves(cursor)
    # t3 = Query_HugeDeduction(cursor)
    # t4 = Query_MaxRealSalary_2020(cursor)
    # t5 = Query_HugeLatingDuration(cursor)
    # t6 = Query_OverruledManyTimes(cursor)
    a = get_reachable_user_ids(cursor, 21)
    a = get_superior(cursor, 34)
    # a = new_employee_id(cursor)
    # a = new_department_id(cursor)
    # delete_department(cursor, 5)
    print(a)
    db.close()
    # close_db(db)
