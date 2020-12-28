from flask import g
import pymysql


class DataBase:

    def __init__(self, name):
        self.conn = pymysql.connect(host='localhost', user='root', password='', charset='utf8mb4')
        cursor = self.conn.cursor()
        sql = "drop database if exists " + name
        cursor.execute(sql)
        sql = "CREATE DATABASE " + name
        cursor.execute(sql)
        self.db = pymysql.connect("localhost", "root", "", name)
        self.cursor = self.db.cursor()
        '''
        关于违反参照完整性要进行的级联操作之后再细化定义
        '''

        # 使用预处理语句创建表
        sql = """create table EMPLOYEE (
                EmployeeID int, 
                Name char(30),
                Birthdate date,
                ID_number char(18) unique, 
                Entrydate date,
                Username char(10) not null,
                Password char(10) not null,
                Gender char(6),
                Phone_number char(20),
                E_mail char(20),
                Level int not null,
                Department_ID int,
                primary key (EmployeeID),
                check(Gender in ('Male', 'Female')),
                check(Level in (0, 1, 2)))"""
        self.cursor.execute(sql)

        sql = """create table DEPARTMENT (
                Department_ID int, 
                Department char(30) not null,
                Manager_ID int,
                info char(140),
                primary key (Department_ID),
                foreign key(Manager_ID) references test.EMPLOYEE(EmployeeID)) """
        self.cursor.execute(sql)

        sql = """alter table test.EMPLOYEE add constraint C1
        foreign key(Department_ID) references test.DEPARTMENT(Department_ID)"""
        self.cursor.execute(sql)

        sql = """create table PAYROLL (
                SalaryNo int, 
                BasicSalary int not null,
                CorrespondingTime_start date not null,
                CorrespondingTime_end date not null,
                PayTime timestamp(0) not null ,
                VerifierID int,
                WorkTime int,
                Deduction int not null default 0,
                RealSalary int not null,
                primary key (SalaryNo),
                foreign key(VerifierID) references test.EMPLOYEE(EmployeeID)) """
        self.cursor.execute(sql)

        sql = """create table LEAVES (
                EmployeeID int,
                LeaveNo int, 
                LeaveBegin date not null,
                LeaveEnd date not null,
                LeaveReason char(30),
                ApplyDay date not null,
                ReviewerID int,
                ApplyStatus bool not null default 0,
                Duration int not null,
                primary key (LeaveNo),
                foreign key(ReviewerID) references test.EMPLOYEE(EmployeeID),
                foreign key(EmployeeID) references test.EMPLOYEE(EmployeeID)) """
        self.cursor.execute(sql)

        sql = """create table ATTENDENCES (
                EmployeeID int,
                AttendenceNo int,
                Date date not null , 
                ArriveTime time not null ,
                LeaveTime time not null ,
                Lateornot bool,
                LeaveEarlyornot bool,
                primary key (AttendenceNo)
                )"""
        self.cursor.execute(sql)

        sql = """create table REMINDERS (
                EmployeeID int,
                Total int not null default 0,
                primary key (EmployeeID),
                foreign key(EmployeeID) references test.EMPLOYEE(EmployeeID))"""
        self.cursor.execute(sql)

        sql = """create table METADATA (
                LastEmployeeNo int not null,
                LastDepartmentNo int not null,
                LastSalaryNo int not null,
                LastLeaveNo int not null,
                LastAttendenceNo int not null 
                )"""
        self.cursor.execute(sql)

        sql = """insert into test.METADATA
                (LastEmployeeNo,LastDepartmentNo,LastSalaryNo,LastLeaveNo,LastAttendenceNo)
                values (0,0,0,0,0)"""
        self.cursor.execute(sql)

    def init_data(self, file_path):
        pass

    def __getResult(self, AttrList):
        results = self.cursor.fetchall()
        ret = []
        for item in results:
            tmp = {AttrList[i]: item[i] for i in range(len(item))}
            ret.append(tmp)
        return ret

    def Query_leaveandlate_202001(self, topnum=10):
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
        self.cursor.execute(sql)
        return self.__getResult(['Name', 'LeaveandLate'])

    def Query_MaxVerify(self):
        # 语文不好，这里是要查经理本人的还是他审核的啊?
        pass

    def Query_HugeDeduction(self):


    def close_db(self, exception=None):
        self.db.close()

    def init_app(self, app):
        app.teardown_appcontext(self.close_db)

if __name__ == "__main__":
    D = DataBase("test")
    D.init_data('sample.pkl')
    D.Query_leaveandlate_202001()
    D.close_db()