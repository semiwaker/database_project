from IPython import embed
import numpy as np
import random
import pymysql
import datetime


password = ''

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
D = 5
D_name = ['A01', 'A02', 'B01', 'B02', 'S']
Employee = [[
    i*len(last_name)+j,  # EmloyeeID
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
    random.randint(0, D-1),  # Department_ID
] for i in range(len(first_name)) for j in range(len(last_name))]

M = np.random.choice(range(n), D+1, replace=False).tolist()
Admin = M.pop()
for i in range(D):
    Employee[M[i]][10] = 'manager'
    Employee[M[i]][11] = i
Employee[Admin][10] = 'admin'
Employee[Admin].pop()
# 数据插入部分
for i in range(n):
    if(i == Admin):
        sql = '''INSERT INTO EMPLOYEE(EmployeeID, Name, BirthDate,
        ID_number, EntryDate, Username, Password, Gender, Phone_number,
        E_mail, Level) VALUES ''' + str(tuple(Employee[i]))
    else:
        sql = '''INSERT INTO EMPLOYEE(EmployeeID, Name, BirthDate,
        ID_number, EntryDate, Username, Password, Gender, Phone_number,
        E_mail, Level, Department_ID) VALUES '''+str(tuple(Employee[i]))
    try:
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
        print("Insert Employee Error")
        embed()

for i in range(D):
    value = [i, D_name[i], M[i], "This is "+D_name[i]+'.']
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
for eid in range(n):
    print(eid)
    if Employee[eid][10] == 'employee':
        late_P = 0.1
        leave_P = 0.1
        verifier = M[Employee[eid][11]]
    elif Employee[eid][10] == 'manager':
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
            item = [eid, L, s_day, e_day,
                    '胃疼' if private else '因公', private,
                    a_day, verifier, a_s, day]
            L += 1
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
            else:
                lateornot = False
            if random.random() < late_P:
                leaveearlyornot = True
                missing += 1
            else:
                leaveearlyornot = False
            item = [eid, A, d.strftime("%Y-%m-%d"),
                    '09:01:00' if lateornot else '08:59:00',
                    '16:59:00' if leaveearlyornot else '17:01:00',
                    lateornot, leaveearlyornot, missing]
            A += 1
            sql = '''insert into test.attendences(EmployeeID, AttendenceNo,
            Date, ArriveTime, LeaveTime, Lateornot, LeaveEarlyornot, TimeMissing) 
            VALUES ''' + str(tuple(item))
            cursor.execute(sql)
            db.commit()
            d += delta
        d += delta
        d += delta

sql = """insert into test.METADATA
        (LastEmployeeNo,LastDepartmentNo,LastSalaryNo,LastLeaveNo,LastAttendenceNo)
        values """+str((n-1,D-1,0,L,A))
cursor.execute(sql)
db.commit()

