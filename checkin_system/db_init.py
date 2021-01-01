from IPython import embed
import numpy as np
import random
import pymysql
import datetime
import os

def get_password():
    if not os.path.exists("./db_password.txt"):
        return ""
    with open("./db_password.txt", "r") as file:
        db_password = file.read()
    return db_password

password = get_password()

name = "test"
conn = pymysql.connect(host='localhost', user='root',
                       password=password, charset='utf8mb4')
cursor = conn.cursor()
sql = "drop database if exists " + name
cursor.execute(sql)
sql = "CREATE DATABASE " + name
cursor.execute(sql)
db = pymysql.connect("localhost", "root", password, name)
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
        Username char(20) not null,
        Password char(20) not null,
        Gender char(6),
        Phone_number char(20),
        E_mail char(30),
        Level char(10) not null,
        Department_ID int,
        primary key (EmployeeID),
        check(Gender in ('Male', 'Female')),
        check(Level in ('employee', 'manager', 'admin')))"""
cursor.execute(sql)

sql = """create table DEPARTMENT (
        Department_ID int,
        Department char(30) not null,
        Manager_ID int,
        info char(140),
        primary key (Department_ID),
        foreign key(Manager_ID) references test.EMPLOYEE(EmployeeID)) """
cursor.execute(sql)

sql = """create table PAYROLL (
        SalaryNo int,
        EmployeeID int,
        BasicSalary int not null,
        CorrespondingTime char(10) not null ,
        PayTime timestamp(0),
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
        ApplyStatus char(10) not null,
        Duration int not null,
        check(ApplyStatus in ('pending', 'accepted', 'rejected')),
        primary key (LeaveNo),
        foreign key(ReviewerID) references test.EMPLOYEE(EmployeeID),
        foreign key(EmployeeID) references test.EMPLOYEE(EmployeeID)) """
cursor.execute(sql)

sql = """create table ATTENDENCES (
        EmployeeID int,
        AttendenceNo int,
        Date date not null ,
        ArriveTime time not null ,
        LeaveTime time,
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

# 数据生成部分
first_name = ['Jacob', 'Emily', 'Michael', 'Hannah', 'Joshua', 'Madison', 'Matthew', 'Samantha']
#, 'Andrew','Ashley', 'Joseph', 'Sarah', 'Nicholas', 'Elizabeth', 'Anthony', 'Kayla', 'Tyler', 'Alexis', 'Daniel', 'Abigail']
last_name = ['Adams', 'Anderson', 'Arnold', 'Bell', 'Carter', 'Charles', 'David']
             #, 'Edward', 'Gary', 'George',
             #'Harris', 'Jaskson', 'James', 'Peter', 'Smith', 'Walker', 'Williams', 'Rose', 'Oliver', 'Leonard', 'Keith', 'Eddie']
n = len(first_name)*len(last_name)
# n = 10
D = 5
D_name = ['A01', 'A02', 'B01', 'B02', 'S']
Employee = [[
    i*len(last_name)+j+1,  # EmloyeeID
    first_name[i]+' '+last_name[j],  # Name
    str(random.randint(1960, 2000))+'-'+str(random.randint(1, 12)
                                            ).zfill(2)+'-'+str(random.randint(1, 28)).zfill(2),  # Birthdate
    ''.join(np.random.choice(['0', '1', '2', '3', '4', '5', '6',
                              '7', '8', '9'], 18, replace=True)),  # fake ID_number
    str(random.randint(2010, 2020))+'-'+str(random.randint(1, 12)
                                            ).zfill(2)+'-'+str(random.randint(1, 28)).zfill(2),  # Entrydate
    first_name[i]+'_'+last_name[j],  # Username
    first_name[i] + '_' + last_name[j],  # Password
    'Male' if random.randint(0, 1) == 0 else 'Female',  # Gender
    ''.join(np.random.choice(['0', '1', '2', '3', '4', '5', '6',
                              '7', '8', '9'], 7, replace=True)),  # fake Phone_number
    first_name[i]+'_'+last_name[j]+'@' + \
    ('gmail.com' if random.randint(0, 1) == 0 else 'pku.edu.cn'),  # fake E-mail
    'employee',  # Level
    random.randint(1, D),  # Department_ID
] for i in range(len(first_name)) for j in range(len(last_name))]

M = np.random.choice(range(1, n+1), D+1, replace=False).tolist()
Admin = M.pop()
for i in range(1, D+1):
    Employee[M[i-1]-1][10] = 'manager'
    Employee[M[i-1]-1][11] = i
Employee[Admin-1][10] = 'admin'
Employee[Admin-1].pop()
# 数据插入部分
for i in range(1,n+1):
    if(i == Admin):
        sql = '''INSERT INTO EMPLOYEE(EmployeeID, Name, BirthDate,
        ID_number, EntryDate, Username, Password, Gender, Phone_number,
        E_mail, Level) VALUES ''' + str(tuple(Employee[i-1]))
    else:
        sql = '''INSERT INTO EMPLOYEE(EmployeeID, Name, BirthDate,
        ID_number, EntryDate, Username, Password, Gender, Phone_number,
        E_mail, Level, Department_ID) VALUES '''+str(tuple(Employee[i-1]))
    try:
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
        print("Insert Employee Error")
        embed()

for i in range(1, D+1):
    value = [i, D_name[i-1], M[i-1], "This is "+D_name[i-1]+'.']
    sql = '''INSERT INTO DEPARTMENT(Department_ID, Department, Manager_ID,
        info) VALUES ''' + str(tuple(value))
    try:
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
        print("Insert Department Error")
        embed()

# 懒得写延迟检查了，直接把这个限制挪到了后面
sql = """alter table EMPLOYEE add constraint C1
foreign key(Department_ID) references DEPARTMENT(Department_ID) on delete
 set null """
cursor.execute(sql)

# 生成请假与考勤记录,先跑起来，之后再改
L=0
A=0
Ded = np.zeros((n, 13))
for eid in range(1, n+1):
    print(eid)
    if Employee[eid-1][10] == 'employee':
        late_P = 0.1
        leave_P = 0.1
        verifier = M[Employee[eid-1][11]-1]
    elif Employee[eid-1][10] == 'manager':
        late_P = 0.02
        leave_P = 0.02
        verifier = Admin
    else:
        continue

    begin = datetime.date(2020,1,6)
    end = datetime.date(2020,12,25)
    d = begin
    delta = datetime.timedelta(days=1)
    while d <= end:
        day = 0
        if random.random() < leave_P:
            if random.random() < 0.5:
                private = True
            else:
                private = False
            day = random.randint(1, 5)
            if (not private) or random.random() < 0.6:
                a_s = 'accepted'
            else:
                a_s = 'rejected'
            s_day = d.strftime("%Y-%m-%d")
            dd = d
            for i in range(day):
                dd += delta
            e_day = dd.strftime("%Y-%m-%d")
            a_day = (d-delta).strftime("%Y-%m-%d")
            L += 1
            item = [eid, L, s_day, e_day,
                    '胃疼' if private else '因公', private,
                    a_day, verifier, a_s, day]
            sql = '''insert into test.leaves(EmployeeID, LeaveNo, LeaveBegin, 
            LeaveEnd, LeaveReason, Privateornot, ApplyDay, 
            ReviewerID, ApplyStatus, Duration) VALUES '''+str(tuple(item))
            cursor.execute(sql)
            db.commit()
            if a_s == 'rejected':
                day = 0
        for i in range(day):
            d += delta
        for i in range(5-day):
            missing = 0
            if random.random() < late_P:
                lateornot = True
                missing += 1
                Ded[eid-1][d.month] += 100
            else:
                lateornot = False
            if random.random() < late_P:
                leaveearlyornot = True
                missing += 1
                Ded[eid-1][d.month] += 100
            else:
                leaveearlyornot = False
            A += 1
            item = [eid, A, d.strftime("%Y-%m-%d"),
                    '09:01:00' if lateornot else '08:59:00',
                    '16:59:00' if leaveearlyornot else '17:01:00',
                    lateornot, leaveearlyornot, missing]
            sql = '''insert into test.attendences(EmployeeID, AttendenceNo,
            Date, ArriveTime, LeaveTime, Lateornot, LeaveEarlyornot, TimeMissing) 
            VALUES ''' + str(tuple(item))
            cursor.execute(sql)
            db.commit()
            d += delta
        d += delta
        d += delta

S = 0
for eid in range(1, n+1):
    if eid == Admin:
        continue
    if Employee[eid - 1][10] == 'employee':
        basic = 8000
        verifier = M[Employee[eid - 1][11] - 1]
    else:
        basic = 20000
        verifier = Admin
    worktime = 2021 - int(Employee[eid - 1][4][0:4])
    for month in range(1,13):
        cor = "2020-"+str(month).zfill(2)
        paytime = datetime.datetime(
            2021 if month==12 else 2020,
            1 if month==12 else month+1,
            random.randint(1,5),0,0,0).strftime("%Y-%m-%d %H:%M:%S")
        deduction = Ded[eid-1][month]
        real = basic - deduction
        S += 1
        item = [S, eid, basic, cor, paytime, verifier, worktime, deduction, real]
        sql = '''insert into test.payroll(SalaryNo, EmployeeID, BasicSalary,
         CorrespondingTime, PayTime, VerifierID, WorkTime, Deduction, RealSalary) 
         VALUES '''+str(tuple(item))
        cursor.execute(sql)
        db.commit()


sql = """insert into test.METADATA
        (LastEmployeeNo,LastDepartmentNo,LastSalaryNo,LastLeaveNo,LastAttendenceNo)
        values """+str((n,D,S,L,A))
cursor.execute(sql)
db.commit()

