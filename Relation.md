EMPLOYEE(<u>EmployeeID</u>, Name, Birthdate, ID_number, Entrydate, Username, Password, Gender, Phone_number, E_mail, Level, Department_ID)

DEPARTMENT(<u>Department_ID</u>, Department, Manager_ID, info)

PAYROLL(<u>SalaryNo</u>, BasicSalary, WorkTime, PayTime, EmployeeID, VerifierID, Deduction, RealSalary)

ATTENDENCE(<u>AttendenceNo</u>, Date, ArriveTime, LeaveTime, Lateornot, LeaveEarlyornot, Timemissing, EmployeeID)

LEAVES(<u>LeaveNo</u>, LeaveBegin, LeaveEnd, LeaveReason, ApplyDay, ApplyStatus, ReviewerID, EmployeeID, Privateornot, Duration)

BADEVENT(<u>EmployeeID, Date</u>)