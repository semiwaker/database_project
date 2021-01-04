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

name = "ProjectExecutionComp"
conn = pymysql.connect(host='localhost', user='root',
                       password=password, charset='utf8mb4')
cursor = conn.cursor()
sql = "drop database if exists " + name
cursor.execute(sql)
sql = "CREATE DATABASE " + name
cursor.execute(sql)
db = pymysql.connect("localhost", "root", password, name)
cursor = db.cursor()

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
        foreign key(Manager_ID) references ProjectExecutionComp.EMPLOYEE(EmployeeID)) """
cursor.execute(sql)

sql = """create table PAYROLL (
        SalaryNo int,
        EmployeeID int,
        BasicSalary int not null,
        WorkTime char(10) not null ,
        PayTime timestamp(0),
        VerifierID int,
        Deduction int not null default 0,
        RealSalary int not null,
        primary key (SalaryNo),
        foreign key(EmployeeID) references ProjectExecutionComp.EMPLOYEE(EmployeeID),
        foreign key(VerifierID) references ProjectExecutionComp.EMPLOYEE(EmployeeID)) """
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
        foreign key(ReviewerID) references ProjectExecutionComp.EMPLOYEE(EmployeeID),
        foreign key(EmployeeID) references ProjectExecutionComp.EMPLOYEE(EmployeeID)) """
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
        foreign key(EmployeeID) references ProjectExecutionComp.EMPLOYEE(EmployeeID))"""
cursor.execute(sql)

sql = """create table METADATA (
        LastEmployeeNo int not null,
        LastDepartmentNo int not null,
        LastSalaryNo int not null,
        LastLeaveNo int not null,
        LastAttendenceNo int not null
        )"""
cursor.execute(sql)

sql = """create table BADEVENTS (
        EmployeeID int not null,
        Date Date not null,
        primary key (EmployeeID, Date)
        )"""
cursor.execute(sql)


# 数据生成部分
first_name = ['Jacob', 'Emily', 'Michael', 'Hannah',
              'Joshua', 'Madison', 'Matthew', 'Samantha']
# , 'Andrew','Ashley', 'Joseph', 'Sarah', 'Nicholas', 'Elizabeth', 'Anthony', 'Kayla', 'Tyler', 'Alexis', 'Daniel', 'Abigail']
last_name = ['Adams', 'Anderson', 'Arnold',
             'Bell', 'Carter', 'Charles', 'David']
# , 'Edward', 'Gary', 'George',
# 'Harris', 'Jaskson', 'James', 'Peter', 'Smith', 'Walker', 'Williams', 'Rose', 'Oliver', 'Leonard', 'Keith', 'Eddie']
n = len(first_name)*len(last_name)
# n = 10
D = 5
D_name = ['A', 'B', 'C', 'D', 'S']
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
# Employee[Admin-1].pop()
# 数据插入部分
employee_data = ",".join([str(tuple(Employee[i-1])) for i in range(1, n+1)])
sql = '''INSERT INTO EMPLOYEE(EmployeeID, Name, BirthDate,
    ID_number, EntryDate, Username, Password, Gender, Phone_number,
    E_mail, Level, Department_ID) VALUES ''' + employee_data
try:
    cursor.execute(sql)
    db.commit()
except:
    db.rollback()
    print("Insert Employee Error")
    embed()

values = []
for i in range(1, D+1):
    value = [i, D_name[i-1], M[i-1], "This is "+D_name[i-1]+'.']
    values.append(str(tuple(value)))

sql = '''INSERT INTO DEPARTMENT(Department_ID, Department, Manager_ID,
    info) VALUES ''' + ",".join(values)
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
L = 0
A = 0
Ded = np.zeros((n, 13))
leave_values = []
attend_values = []

def generate_late_str(is_late_man):
    if is_late_man:
        return "16:58:00", 478
    t = random.randint(1, 180)
    return str(9+t//60).zfill(2)+":"+str(t%60).zfill(2)+":00", t

first_man = [0 for i in range(D+1)]
for eid in range(1, n+1):
    if Employee[eid-1][10] == 'employee':
        if first_man[Employee[eid-1][11]] == 0:  # 每个部门有一个专门迟到哥（为了查询3和查询5）
            first_man[Employee[eid - 1][11]] = 1
            late_P = 1
            leave_P = 0
        elif first_man[Employee[eid-1][11]] == 1:  # 每个部门还有一个专门迟到哥（为了查询6）
            first_man[Employee[eid - 1][11]] = 2
            late_P = 1
            leave_P = 0.9
        else:
            late_P = 0.1
            leave_P = 0.1
        verifier = M[Employee[eid-1][11]-1]
    elif Employee[eid-1][10] == 'manager':
        if Employee[eid-1][11] == 5:  # S部门的经理每天请假
            leave_P = 1
        else:
            leave_P = 0.02
        late_P = 0.02
        verifier = Admin
    else:
        late_P = 0
        leave_P = 0

    begin = datetime.date(2020, 1, 6)
    end = datetime.date(2020, 12, 25)
    d = begin
    delta = datetime.timedelta(days=1)
    while d <= end:
        day = 0
        if random.random() < leave_P:
            if random.random() < 0.8 and not leave_P == 1:  # 对请假型经理特殊处理
                private = True
            else:
                private = False
            if leave_P == 1:  # 对请假型经理特殊处理
                day = 5
            else:
                day = random.randint(1, 5)
            if (not private) or random.random() < 0.6:
                a_s = 'accepted'
            else:
                a_s = 'rejected'
            s_day = d.strftime("%Y-%m-%d")
            dd = d
            for i in range(day-1):
                dd += delta
            e_day = dd.strftime("%Y-%m-%d")
            a_day = (d-delta).strftime("%Y-%m-%d")
            L += 1
            item = [eid, L, s_day, e_day,
                    '胃疼' if private else '因公', private,
                    a_day, verifier, a_s, day]
            leave_values.append(str(tuple(item)))
            if a_s == 'rejected':
                day = 0
        for i in range(day):
            d += delta
        for i in range(5-day):
            missing = 0
            if random.random() < late_P:
                lateornot = True
                arrive_time, tt = generate_late_str(late_P==1)
                missing += tt
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
                    arrive_time if lateornot else '08:59:00',
                    '16:59:00' if leaveearlyornot else '17:01:00',
                    lateornot, leaveearlyornot, missing]
            attend_values.append(str(tuple(item)))
            d += delta
        d += delta
        d += delta

sql = '''insert into ProjectExecutionComp.leaves(EmployeeID, LeaveNo, LeaveBegin,
LeaveEnd, LeaveReason, Privateornot, ApplyDay,
ReviewerID, ApplyStatus, Duration) VALUES ''' + ",".join(leave_values)
try:
    cursor.execute(sql)
    db.commit()
except:
    embed()

try:
    sql = '''insert into ProjectExecutionComp.attendences(EmployeeID, AttendenceNo,
    Date, ArriveTime, LeaveTime, Lateornot, LeaveEarlyornot, TimeMissing)
    VALUES ''' + ",".join(attend_values)
    cursor.execute(sql)
    db.commit()
except:
    embed()

payroll_values = []
S = 0
for eid in range(1, n+1):
    if eid == Admin:
        continue
    if Employee[eid - 1][10] == 'employee':
        basic = 3000
        verifier = M[Employee[eid - 1][11] - 1]
    else:
        basic = 8000
        verifier = Admin
    for month in range(1, 13):
        worktime = "2020-"+str(month).zfill(2)
        paytime = datetime.datetime(
            2021 if month == 12 else 2020,
            1 if month == 12 else month+1,
            random.randint(1, 5), 0, 0, 0).strftime("%Y-%m-%d %H:%M:%S")
        deduction = Ded[eid-1][month]
        real = basic - deduction
        S += 1
        item = [S, eid, basic, paytime, verifier, worktime, deduction, real]
        payroll_values.append(str(tuple(item)))

sql = '''insert into ProjectExecutionComp.payroll(SalaryNo, EmployeeID, BasicSalary,
    PayTime, VerifierID, WorkTime, Deduction, RealSalary)
    VALUES ''' + ",".join(payroll_values)
cursor.execute(sql)
db.commit()

sql = """insert into ProjectExecutionComp.METADATA
        (LastEmployeeNo,LastDepartmentNo,LastSalaryNo,LastLeaveNo,LastAttendenceNo)
        values """+str((n, D, S, L, A))
cursor.execute(sql)
db.commit()


# 为了防止有以前的提醒，最后再加触发器
sql = """create trigger LeaveAutoDetect AFTER UPDATE
ON ProjectExecutionComp.leaves FOR EACH ROW
BEGIN
    if (NEW.ApplyStatus = 'accepted' and NEW.Privateornot = TRUE)
        then
        insert into ProjectExecutionComp.badevents(EmployeeID, Date)
        VALUES (NEW.EmployeeID, NEW.LeaveEnd);
        select count(*) from ProjectExecutionComp.badevents
            where EmployeeID = NEW.EmployeeID
            and DATEDIFF(Date, NEW.LeaveBegin)>=-6 into @a;
        if @a > 3
            then
            if (select count(*) from ProjectExecutionComp.reminders
                where EmployeeID = NEW.EmployeeID) > 0
                then
                UPDATE ProjectExecutionComp.reminders
                set Total = @a
                where EmployeeID = NEW.EmployeeID;
                else
                insert into ProjectExecutionComp.reminders(EmployeeID, Total)
                VALUES (NEW.EmployeeID, @a);
            end if;
        end if;
    end if;
end;"""
cursor.execute(sql)

sql = """create trigger LateAutoDetect AFTER INSERT
ON ProjectExecutionComp.attendences FOR EACH ROW
BEGIN
    if (NEW.Lateornot = TRUE)
        then
        insert into ProjectExecutionComp.badevents(EmployeeID, Date)
        VALUES (NEW.EmployeeID, NEW.Date);
        select count(*) from ProjectExecutionComp.badevents
            where EmployeeID = NEW.EmployeeID
            and DATEDIFF(Date, NEW.Date)>=-6 into @a;
        if @a > 3
            then
            if (select count(*) from ProjectExecutionComp.reminders
                where EmployeeID = NEW.EmployeeID) > 0
                then
                UPDATE ProjectExecutionComp.reminders
                set Total = @a
                where EmployeeID = NEW.EmployeeID;
                else
                insert into ProjectExecutionComp.reminders(EmployeeID, Total)
                VALUES (NEW.EmployeeID, @a);
            end if;
        end if;
    end if;
end;"""
cursor.execute(sql)
