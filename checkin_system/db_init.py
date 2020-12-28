import pymysql

name = "test"
conn = pymysql.connect(host='localhost', user='root', password='', charset='utf8mb4')
cursor = conn.cursor()
sql = "drop database if exists " + name
cursor.execute(sql)
sql = "CREATE DATABASE " + name
cursor.execute(sql)
db = pymysql.connect("localhost", "root", "", name)
cursor = db.cursor()
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
cursor.execute(sql)

sql = """create table DEPARTMENT (
        Department_ID int, 
        Department char(30) not null,
        Manager_ID int,
        info char(140),
        primary key (Department_ID),
        foreign key(Manager_ID) references test.EMPLOYEE(EmployeeID)) """
cursor.execute(sql)

sql = """alter table test.EMPLOYEE add constraint C1
foreign key(Department_ID) references test.DEPARTMENT(Department_ID)"""
cursor.execute(sql)

sql = """create table PAYROLL (
        SalaryNo int, 
        EmployeeID int,
        BasicSalary int not null,
        CorrespondingTime date not null,
        PayTime timestamp(0) not null ,
        VerifierID int,
        WorkTime int,
        Deduction int not null default 0,
        RealSalary int not null,
        primary key (SalaryNo),
        foreign key(EmployeeID) references test.EMPLOYEE(EmployeeID),
        foreign key(VerifierID) references test.EMPLOYEE(EmployeeID)) """
cursor.execute(sql)

sql = """create table LEAVES (
        EmployeeID int,
        LeaveNo int, 
        LeaveBegin date not null,
        LeaveEnd date not null,
        LeaveReason char(30),
        Privateornot bool not null,
        ApplyDay date not null,
        ReviewerID int,
        ApplyStatus bool not null default 0,
        Duration int not null,
        primary key (LeaveNo),
        foreign key(ReviewerID) references test.EMPLOYEE(EmployeeID),
        foreign key(EmployeeID) references test.EMPLOYEE(EmployeeID)) """
cursor.execute(sql)

sql = """create table ATTENDENCES (
        EmployeeID int,
        AttendenceNo int,
        Date date not null , 
        ArriveTime time not null ,
        LeaveTime time not null ,
        Lateornot bool,
        LeaveEarlyornot bool,
        TimeMissing int not null,
        primary key (AttendenceNo)
        )"""
cursor.execute(sql)

sql = """create table REMINDERS (
        EmployeeID int,
        Total int not null default 0,
        primary key (EmployeeID),
        foreign key(EmployeeID) references test.EMPLOYEE(EmployeeID))"""
cursor.execute(sql)

sql = """create table METADATA (
        LastEmployeeNo int not null,
        LastDepartmentNo int not null,
        LastSalaryNo int not null,
        LastLeaveNo int not null,
        LastAttendenceNo int not null 
        )"""
cursor.execute(sql)

sql = """insert into test.METADATA
        (LastEmployeeNo,LastDepartmentNo,LastSalaryNo,LastLeaveNo,LastAttendenceNo)
        values (0,0,0,0,0)"""
cursor.execute(sql)

## 插入初始数据还没写