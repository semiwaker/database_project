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