import datetime
from flask import g
import pymysql

import os
import functools

'''里面所有SQL语句都在前面加了个test.xxxx，是因为这样有代码提示，最后会删掉'''


def throw_dec(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except BaseException as e:
            g.error = str(e)

    return wrapper


def get_dbpassword():
    if not os.path.exists("./db_password.txt"):
        return ""
    with open("./db_password.txt", "r") as file:
        db_password = file.read()
    return db_password


db_password = get_dbpassword()


def get_db(name="test"):
    db = pymysql.connect("localhost", "root", db_password, name)
    g.db = db
    return db


@throw_dec
def __getResult(cursor):
    results = cursor.fetchall()
    col = cursor.description
    AttrList = [col[i][0] for i in range(len(col))]
    ret = []
    for item in results:
        tmp = {AttrList[i]: item[i] for i in range(len(item))}
        ret.append(tmp)
    return ret


@throw_dec
def get_department_list(cursor):
    sql = """select Department_ID as id, Department as name
    from test.department"""
    cursor.execute(sql)
    return __getResult(cursor)
    # return [{"id": None, "name": None}]


@throw_dec
def get_manager_list(cursor):
    sql = """select EmployeeID as id, name
        from test.employee"""
    cursor.execute(sql)
    return __getResult(cursor)
    # return [{"id": None, "name": None}]


@throw_dec
def get_user_data(cursor, user_id):
    sql = """select username, name, gender, birthdate, department_id, E_mail as email,
    phone_number, id_number, level
    from test.employee
    where EmployeeID = """+str(user_id)
    cursor.execute(sql)
    ret_dict = __getResult(cursor)[0]
    today = datetime.date.today().strftime('%Y-%m-%d')
    sql = """select *
    from test.attendences
    where EmployeeID = """+str(user_id)+"""
    and Date = \'"""+today+'\''

    cursor.execute(sql)
    results = cursor.fetchall()
    if len(results) > 0:
        ret_dict["work_status"] = "in"
    else:
        ret_dict["work_status"] = "out"
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


@throw_dec
def get_password(cursor, userid):
    sql = """select password
            from test.employee
            where EmployeeID = """+str(userid)
    cursor.execute(sql)
    result = cursor.fetchall()
    return result[0][0]
    # return ""


@throw_dec
def get_id_and_password(cursor, username):
    sql = """select EmployeeID, Password
                from test.employee
                where Username = \'""" + username + "\'"
    cursor.execute(sql)
    result = cursor.fetchall()
    if len(result):
        return result[0][0], result[0][1]
    else:
        return None, None
    # return (0, "")


@throw_dec
def get_department_and_level(cursor, user_id):
    sql = """select level, Department_ID
                from test.employee
                where EmployeeID = """ + str(user_id)
    cursor.execute(sql)
    result = cursor.fetchall()
    level = result[0][0]
    department = result[0][1]
    return department, level


@throw_dec
def get_reachable_user_ids(cursor, user_id):
    # 查询所有下属用户id，包括自己
    department, level = get_department_and_level(cursor, user_id)
    if level == 'employee':
        return [user_id]
    elif level == 'manager':
        sql = """select EmployeeID
            from test.employee
            where Department_ID = """ + str(department) + """
            and Level != "admin"
            order by Name
            """
        cursor.execute(sql)
        results = cursor.fetchall()
        return [item[0] for item in results]
    elif level == 'admin':
        sql = """select EmployeeID
            from test.employee
            order by Name"""
        cursor.execute(sql)
        results = cursor.fetchall()
        return [item[0] for item in results]
    # return [user_id]


@throw_dec
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


@throw_dec
def get_leave_list(cursor, user_id):
    # 查询所有下属的未审核的请假申请
    department, level = get_department_and_level(cursor, user_id)
    if level == 'employee':
        return []
    elif level == 'manager':
        sql = """select LeaveNo as leave_no, Name as name, LeaveBegin as leave_begin, LeaveEnd as leave_end,
            LeaveReason as leave_reason, ApplyDay as apply_day
            from test.leaves, test.employee
            where leaves.EmployeeID = employee.EmployeeID
                and ApplyStatus = \'pending\'
                and Department_ID = """+str(department)+"""
                and not leaves.EmployeeID = """+str(user_id)
        cursor.execute(sql)
        return __getResult(cursor)
    elif level == 'admin':
        sql = """select LeaveNo as leave_no, Name as name, LeaveBegin as leave_begin, LeaveEnd as leave_end,
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


@throw_dec
def get_salary_list(cursor, user_id):
    # 这个月的deduction要不就按一次迟到早退扣100，缺勤扣200算好了……
    # 算工作日太麻烦，我直接按每个月出勤20天，多了不补少了扣钱算的
    # 假定一个月最后一天发工资
    today = datetime.date.today()
    month_str = today.strftime('%Y-%m')
    reachable_L = get_reachable_user_ids(cursor, user_id)
    ret_L = []
    for reachable_id in reachable_L:
        if reachable_id == user_id:
            continue
        sql = '''select Name, Department_ID, Level
        from test.employee
        where EmployeeID = '''+str(reachable_id)
        cursor.execute(sql)
        result = cursor.fetchall()[0]
        name, departmentID, level = result[0], result[1], result[2]
        if departmentID is None:
            print(reachable_id)
        if level == 'manager':
            basicSalary = 8000
        elif level == 'employee':
            basicSalary = 3000
        else:
            basicSalary = 20000
        sql = '''select count(Lateornot)+count(LeaveEarlyornot), count(*)
        from test.attendences
        where Date like \''''+month_str+'''%\'
        and EmployeeID = '''+str(reachable_id)
        cursor.execute(sql)
        result = cursor.fetchall()[0]
        deduction_times, attendence_times = result[0], result[1]
        sql = '''select ifnull(sum(Duration), 0)
        from test.leaves
        where ApplyStatus = 'accepted'
        and YEAR(LeaveBegin) = '''+today.strftime('%Y')+'''
        and MONTH(LeaveBegin) = '''+today.strftime('%m')+'''
        and EmployeeID = '''+str(reachable_id)
        cursor.execute(sql)
        leave_days = int(cursor.fetchall()[0][0])
        deduction = deduction_times*100+(20-leave_days-attendence_times)*200
        ret_L.append((reachable_id, name, departmentID, basicSalary,
                      deduction, basicSalary-deduction))
    sql = '''select LastSalaryNo from test.metadata'''
    cursor.execute(sql)
    # 最后一个salary编号, 因为不能确定是否分发，必须等操作完了再修改最后的salary编号
    last_salary_no = cursor.fetchall()[0][0]
    return (ret_L, last_salary_no)
    # [
    # () departmentID,basicSalary,deduction,realSalary
    # ]


@throw_dec
def get_department_info(cursor, department_id):
    sql = """select Department as name, manager_id, info as description
            from test.department
            where Department_ID = """ + str(department_id)
    cursor.execute(sql)
    return __getResult(cursor)[0]
    # return {
    #     "name": None,
    #     "manager_id": None,
    #     "description": None
    # }


@throw_dec
def get_reminders(cursor, user_id):
    # (nkc)还未验证正确性
    department, level = get_department_and_level(cursor, user_id)
    if level == 'admin':
        sql = '''select employee.EmployeeID as id, name, total
        from test.reminders, test.employee
        where employee.EmployeeID = reminders.EmployeeID'''
    elif level == 'manager':
        sql = '''select employee.EmployeeID as id, name, total
            from test.reminders, test.employee
            where employee.EmployeeID = reminders.EmployeeID
            and Department_ID = '''+str(department)+'''
            and employee.EmployeeID != '''+str(user_id)
    cursor.execute(sql)
    return __getResult(cursor)


@throw_dec
def get_employee_xml(cursor, user_id):
    def make_xml(cursor, user_id):
        user_data = get_user_data(cursor, user_id)

        sql = '''select SalaryNo, BasicSalary,
                PayTime, VerifierID, Name as VerifierName, WorkTime, Deduction, RealSalary
                from test.payroll, test.employee where
                payroll.EmployeeID=''' + str(user_id)+'''
                and VerifierID=employee.EmployeeID
                order by Paytime desc
                '''
        cursor.execute(sql)
        salary_data = __getResult(cursor)

        salary_xml = '\n'.join([f'''<Salary>
  <SalaryNo>{salary["SalaryNo"]}</SalaryNo>
  <DepartmentID>{user_data["department_id"]}</DepartmentID>
  <BasicSalary>{salary["BasicSalary"]}</BasicSalary>
  <Deduction>{salary["Deduction"]}</Deduction>
  <RealSalary>{salary["RealSalary"]}</RealSalary>
  <WorkTime>{salary["WorkTime"]}</WorkTime>
  <PayTime>{salary["PayTime"]}</PayTime>
  <VerifierID>{salary["VerifierID"]}</VerifierID>
  <VerifierName>{salary["VerifierName"]}</VerifierName>
</Salary>
''' for salary in salary_data])

        sql = f'''select Department from test.DEPARTMENT where Department_ID={user_data["department_id"]}'''
        cursor.execute(sql)
        user_data["department"] = __getResult(cursor)[0]['Department']

        sql = f'''select AttendenceNo as LatingNo, Date as LatingDay, ArriveTime
        from test.ATTENDENCES where EmployeeID={str(user_id)} and Lateornot=1
        order by Date desc
        '''
        cursor.execute(sql)
        lating_data = __getResult(cursor)

        for i in lating_data:
            base = i["LatingDay"]
            base = datetime.datetime(base.year, base.month, base.day, hour=9)
            arr = datetime.datetime(
                base.year, base.month, base.day) + i["ArriveTime"]
            i["LatingTime"] = str((arr-base).seconds // 60) + " min"

        lating_xml = '\n'.join([f'''<Lating>
  <LatingNo>{lating["LatingNo"]}</LatingNo>
  <LatingDay>{lating["LatingDay"]}</LatingDay>
  <LatingTime>{lating["LatingTime"]}</LatingTime>
</Lating>''' for lating in lating_data])

        sql = '''select
        LeaveNo, LeaveBegin, LeaveEnd, LeaveReason,
        ApplyDay, Name as Reviewer
        from test.leaves, test.employee
        where leaves.EmployeeID='''+str(user_id)+'''
        and ApplyStatus="accepted"
        and leaves.ReviewerID=employee.EmployeeID
        '''
        cursor.execute(sql)
        leaves_data = __getResult(cursor)
        leaves_xml = '\n'.join([f'''<Leave>
  <LeaveNo>{leave["LeaveNo"]}</LeaveNo>
  <LeaveBegin>{leave["LeaveBegin"]}</LeaveBegin>
  <LeaveEnd>{leave["LeaveEnd"]}</LeaveEnd>
  <LeaveReason>{leave["LeaveReason"]}</LeaveReason>
  <ApplyDay>{leave["ApplyDay"]}</ApplyDay>
  <Reviewer>{leave["Reviewer"]}</Reviewer>
</Leave>''' for leave in leaves_data])

        birthday = user_data["birthdate"]
        age = (datetime.date.today()-birthday).days // 365

        result = f'''<Employee>
  <EmployeeID>{str(user_id)}</EmployeeID>
  <Info>
    <BasicInfo>
      <Name>{user_data["name"]}</Name>
      <Gender>{user_data["gender"]}</Gender>
      <Birthdate>{user_data["birthdate"]}</Birthdate>
      <Age>{age}</Age>
      <Email>{user_data["email"]}</Email>
      <Phone>{user_data["phone_number"]}</Phone>
      <DepartmentID>{user_data["department_id"]}</DepartmentID>
      <Department>{user_data["department"]}</Department>
      <Level>{user_data["level"]}</Level>
    </BasicInfo>
    <OtherInfo>
        <Salaries>
        {salary_xml}
        </Salaries>
        <Latings>
        {lating_xml}
        </Latings>
        <Leaves>
        {leaves_xml}
        </Leaves>
    </OtherInfo>
  </Info>
</Employee>'''
        return result

    if user_id == 'all':
        cursor.execute('select EmployeeID from test.EMPLOYEE')
        ids = __getResult(cursor)
        xmls = '\n'.join([make_xml(cursor, i["EmployeeID"]) for i in ids])
        result = f"<XML><Employees>{xmls}</Employees></XML>"
    else:
        result = f"<XML><Employees>{make_xml(cursor, user_id)}</Employees></XML>"
    return result.replace('\n', '')


@throw_dec
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
    return True


@throw_dec
def check_department_updatable(cursor, user_id, department_id):
    department, level = get_department_and_level(cursor, user_id)
    if level == 'admin' or (level == 'manager' and department == int(department_id)):
        return True
    return False


@throw_dec
def accept_leave(cursor, leave_no):
    sql = '''update test.leaves
    set ApplyStatus = 'accepted'
    where LeaveNo = ''' + str(leave_no)
    cursor.execute(sql)
    g.db.commit()


@throw_dec
def reject_leave(cursor, leave_no):
    sql = '''update test.leaves
        set ApplyStatus = 'rejected'
        where LeaveNo = ''' + str(leave_no)
    cursor.execute(sql)
    g.db.commit()


@throw_dec
def new_employee_id(cursor):
    sql = '''select LastEmployeeNo + 1
    from test.metadata '''
    cursor.execute(sql)
    result = cursor.fetchall()
    sql = '''update test.metadata
        set LastEmployeeNo = LastEmployeeNo + 1'''
    cursor.execute(sql)
    g.db.commit()
    return result[0][0]


@throw_dec
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


@throw_dec
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


@throw_dec
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


@throw_dec
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
    # TODO 需要把跨月份的拆成两次
    not_private = ['因公']
    duration = (datetime.datetime.strptime(data['leave_end'], '%Y-%m-%d') -
                datetime.datetime.strptime(data['leave_begin'], '%Y-%m-%d')).days + 1
    tmp = (data['user_id'],
           data['leave_no'],
           data['leave_begin'],
           data['leave_end'],
           data['leave_reason'],
           data['leave_reason'] not in not_private,
           data['apply_day'].strftime("%Y-%m-%d"),
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


@throw_dec
def add_new_salary(cursor, data):
    # (nkc) data里还需要一些东西，标在下面了

    # data = [
    #     {
    #         "workTime": ,  这个工资单对应的年月
    #         "employee_id": ,  工资单所有者的id
    #         "payTime": ,  发放工资的时刻（精确到秒），可以直接用点下按钮的时间戳？
    #         "salaryNo": ,
    #         "basicSalary": ,
    #         "deduction": ,
    #         "realSalary": ,
    #         "verifier":
    #     } for salaryNo in g.salaryNos
    # ]
    # 记得更改最后的salayNo

    # (nkc) 还未测试其正确性
    sql = '''select LastSalaryNo from test.metadata'''
    cursor.execute(sql)
    salayNo = cursor.fetchall()[0][0]
    for D in data:
        item = (D['salaryNo'], D['employee_id'], D['basicSalary'],
                D['payTime'], D['verifier'],
                D['workTime'], D['deduction'], D['realSalary'])
        sql = '''insert into test.payroll(SalaryNo, EmployeeID, BasicSalary,
                PayTime, VerifierID, WorkTime, Deduction, RealSalary)
        VALUES '''+str(tuple(item))
        cursor.execute(sql)
        g.db.commit()
        salayNo = max(salayNo, D['salaryNo'])
    sql = '''update test.metadata
    set LastSalaryNo = '''+str(salayNo)
    cursor.execute(sql)
    g.db.commit()


@throw_dec
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
    #     "birthdate":
    #     "department_id":
    #     "email":
    #     "phone_number":
    #     "id_number":
    #     "level":
    # }

    if 'level' in data:
        sql = '''update test.employee
        set Name = \'''' + data['name'] + '''\',
        Gender = \'''' + data['gender'] + '''\',
        Birthdate = \'''' + data['birthdate'] + '''\',
        Department_ID = ''' + str(data['department_id']) + ''',
        E_mail = \'''' + data['email'] + '''\',
        Phone_number = \'''' + data['phone_number'] + '''\',
        ID_number = \'''' + data['id_number'] + '''\',
        Level = \'''' + data['level'] + '''\'
        where EmployeeID = ''' + str(data['user_id'])
    else:
        sql = '''update test.employee
        set E_mail = \'''' + data['email'] + '''\',
        Phone_number = \'''' + data['phone_number'] + '''\',
        Password = \'''' + data['password'] + '''\'
        where EmployeeID = ''' + str(data['user_id'])
    cursor.execute(sql)
    g.db.commit()


@throw_dec
def update_department_info(cursor, data):
    # data = {
    #     "department_id": ,
    #     "name": ,
    #     "manager": ,
    #     "description":
    # }
    sql = '''update test.employee
                set level = 'employee'
                where level = 'manager'
                and Department_ID = ''' + str(data['department_id'])
    cursor.execute(sql)
    g.db.commit()

    sql = '''update test.department
            set Department = \'''' + data['name'] + '''\',
            Manager_ID = ''' + data['manager'] + ''',
            info = \'''' + data['description'] + '''\'
            where Department_ID = ''' + str(data['department_id'])
    cursor.execute(sql)
    g.db.commit()

    sql = '''update test.employee
            set Department_ID = \'''' + str(data['department_id']) + '''\',
            Level = 'manager'
            where EmployeeID = ''' + str(data['manager'])
    cursor.execute(sql)
    g.db.commit()


@throw_dec
def check_in(cursor, user_id, in_time, late):
    sql = '''select LastAttendenceNo + 1
        from test.metadata '''
    cursor.execute(sql)
    result = cursor.fetchall()
    A = result[0][0]+1
    sql = '''update test.metadata
            set LastAttendenceNo = LastAttendenceNo + 1'''
    cursor.execute(sql)
    g.db.commit()
    item = [user_id, A,
            in_time.strftime("%Y-%m-%d"),
            in_time.strftime("%H:%M:%S"),
            late > 0,
            late]
    sql = '''insert into test.attendences(EmployeeID, AttendenceNo, Date,
    ArriveTime, Lateornot, TimeMissing)
    VALUES ''' + str(tuple(item))
    cursor.execute(sql)
    g.db.commit()


@throw_dec
def check_out(cursor, user_id, out_time, early):
    sql = '''update test.attendences
    set LeaveTime = \''''+out_time.strftime("%H:%M:%S")+'''\',
    LeaveEarlyornot = '''+str(early > 0)+''',
    TimeMissing = TimeMissing +'''+str(early)+'''
    where Date = \'''' + out_time.strftime("%Y-%m-%d")+'\''
    cursor.execute(sql)
    g.db.commit()


@throw_dec
def delete_department(cursor, department_id):
    sql = '''delete from test.department
            where Department_ID = ''' + str(department_id)
    cursor.execute(sql)
    g.db.commit()


@throw_dec
def delete_user(cursor, user_id):
    sql = '''delete from test.attendences
                where EmployeeID = ''' + str(user_id)
    cursor.execute(sql)
    g.db.commit()
    sql = '''delete from test.leaves
                where EmployeeID = ''' + str(user_id)
    cursor.execute(sql)
    g.db.commit()
    sql = '''delete from test.payroll
                where EmployeeID = ''' + str(user_id)
    cursor.execute(sql)
    g.db.commit()
    sql = '''delete from test.employee
            where EmployeeID = ''' + str(user_id)
    cursor.execute(sql)
    g.db.commit()


@throw_dec
def clear_reminder(cursor, user_id):
    # (nkc) 还未验证其正确性
    department, level = get_department_and_level(cursor, user_id)
    if level == 'admin':
        sql = '''truncate table test.reminders'''
    elif level == 'manager':
        sql = '''delete
            from test.reminders
            where EmployeeID in (
                select EmployeeID
                from test.employee
                where Department_ID = ''' + str(department) + '''
                and employee.EmployeeID != ''' + str(user_id)+''')'''
    else:
        sql = ''''''
    cursor.execute(sql)
    g.db.commit()


# Query 1
@throw_dec
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


@throw_dec
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


@throw_dec
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


@throw_dec
def Query_HugeDeduction(cursor, year=2020, month=12, D_id=1):
    sql = """with cur(eid, Deduction, RealSalary) as
        (select EmployeeID, Deduction, RealSalary
        from test.payroll
        where WorkTime = \'"""+'-'.join([str(year), str(month).zfill(2)])+"""\')

    select employee.EmployeeID, Name, Deduction
    from cur, test.employee
    where eid = employee.EmployeeID
    and Department_ID = """+str(D_id)+"""
    and Deduction >= (select avg(RealSalary) from cur)
    order by Deduction desc"""
    cursor.execute(sql)
    return __getResult(cursor)


# Query 4
@throw_dec
def Query_MaxRealSalary_2020(cursor):
    sql = """with tmp(Name, WorkTime, RealSalary) as
            (select Name, WorkTime, RealSalary
            from (select * from test.EMPLOYEE
           where Department_ID in
           (select Department_ID
           from test.EMPLOYEE
           group by Department_ID
           having count(EmployeeID)>=10)) as t inner join test.PAYROLL
            on t.EmployeeID = payroll.EmployeeID
            where payroll.WorkTime >= '2020-01-01'
            and payroll.WorkTime <= '2020-12-31')

           select Name, tmp.WorkTime, RealSalary from
           (select WorkTime, max(RealSalary) as maxsalary
           from tmp
           group by WorkTime) as t inner join tmp
           where t.WorkTime = tmp.WorkTime
           and t.maxsalary = tmp.RealSalary"""
    cursor.execute(sql)
    return __getResult(cursor)


# Query 5
@throw_dec
def Query_HugeLatingDuration(cursor):
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
@throw_dec
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
    cursor.execute(sql)
    return __getResult(cursor)


@throw_dec
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
    # a = get_reachable_user_ids(cursor, 21)
    # a = get_superior(cursor, 34)
    # a = new_employee_id(cursor)
    # a = new_department_id(cursor)
    # delete_department(cursor, 5)
    a = Query_HugeDeduction(cursor)
    print(a)
    db.close()
    # close_db(db)
