from flask import g
import pymysql


def get_db(name):
    db = pymysql.connect("localhost", "root", "", name)
    return db


def __getResult(cursor, AttrList):
    results = cursor.fetchall()
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

def delete_department(cursor, department_id):
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
    return __getResult(cursor, ['Name', 'LeaveandLate'])


def Query_MaxVerify():
    # 语文不好，这里是要查经理本人的还是他审核的啊?
    pass


def Query_HugeDeduction():
    pass


def close_db(db, exception=None):
    db.close()


def init_app(self, app):
    app.teardown_appcontext(close_db)


if __name__ == "__main__":
    db = get_db("test")
    cursor = db.cursor()
    Query_leaveandlate_202001(cursor)
    close_db(db)
