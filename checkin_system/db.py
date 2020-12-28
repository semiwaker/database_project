from flask import g
import pymysql

'''里面所有SQL语句都在前面加了个test.xxxx，是因为这样有代码提示，最后会删掉'''

def get_db(name):
    db = pymysql.connect("localhost", "root", "", name)
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

# Query 1
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


def close_db(db, exception=None):
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