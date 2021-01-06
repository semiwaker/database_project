# 用户程序设计文档

## 技术路线

+ 语言：python 3
+ 数据库：MySQL, MySQL python接口
+ 后台程序：Flask
+ 前端框架：React用于处理活动页面, Bootstrap用于CSS。

## 运行说明

### 依赖

+ Python 3+
+ flask
+ pymysql
+ IPython

`pip install -U flask pymysql IPython`

### 运行方式

将路径设为最外层文件夹后：

```cmd
set FLASK_APP=main.py
python -m flask run
```

用浏览器打开127.0.0.1:5000。

### 数据库初始化

将路径设为最外层文件夹后：

`python checkin_system/db_init.py`

运行后将产生一个随机的数据库实例。

### 数据库密码

在最外层文件夹建立`db_password.txt`并将密码写入其中，如果使用免密码的登录方式则可以不建立此文件。

## 程序文件结构

* main.py   Flask服务器入口
* checkin_system
  * static 静态文件，包括CSS，javascript和字体文件
  * template 网页模板
  * __ init __.py Flask应用入口
  * auth.py 登录、注册功能
  * db.py 与数据库的所有交互
  * db_init.py 用于初始化数据库实例 
  * main.py 用户程序主体功能

## 功能与实现

如无特殊说明，页面均为动态页面，在调用相应函数时，根据模板，从数据库获取数据放入内存，并根据内存的数据直接生成对应页面。

### 注册与登录

`\auth\register`为注册页面，实现函数为`auth.register`，注册成功后转到`\main\success`成功页面，失败后在原页面展示失败信息。

`\auth\login`为登录页面，实现函数为`auth.login`，登录成功后转到`\main\home`主页页面，失败后在原页面展示失败信息。

登录成功后，在session记录用户编号，并在每一个页面获取前获得所需的用户信息。

登录、注册、登出的入口在页面上方黑色导航栏。

为方便SQL展示，用户密码采用明文传输与储存。

### 主页

`\main\home`为主页，用于展示员工信息。普通员工仅能展示自己，经理和管理员可以选择自己或任意下属的信息进行展示。

展示界面通过Ajax查询相应XML获取信息，对应的url为`\main\employee_info_<user_id>.xml`，其中user_id为对应的用户编号，当user_id='all'时，为将所有用户信息集合在一起的xml（没有对应的展示页面）。

XML的展示使用javascript进行处理，`static\employee_display.js`负责将XML转换为对应的网页元素，以及负责处理主页的展示员工选择功能。

### 签到、签退功能

右侧导航栏中，根据到/离岗状态，可以点击“到岗”或“离岗”按钮实现签到和签退功能，对应的函数为`main.check_in`和`main.check_out`，成功后转到`\main\success`。

工作时间以9点到17点记，9点后到岗为迟到，17点前离岗为早退，在数据库中没有记录为缺勤。

`main\attendences`为考勤页面，对经理或管理员可见，用于查看或删除下属员工的考勤记录，对应函数为`main.attendences`。

### 请假与审批

`\main\leave`为请假页面，入口在右侧导航栏。对应函数为`main.leave`。
`\main\leave_review`为请假审批页面，经理以及管理员在右侧导航栏可见，当下属员工有未审批的请假条时，会以数字标签的形式提醒经理或管理员审批。请假条以表格形式展示，右侧有接受和拒绝按钮。对应函数为`main.leave_review`。

`\main\leaves`为请假条查看页面，经理及管理员可见，用于查看或删除下属员工的已审核的请假条。对应函数为`main.leaves`。

### 修改自身信息

`\main\info_update`为修改自身信息页面，仅可修改邮件地址、电话号码和密码，入口在右侧导航栏。对应函数为`main.info_update`。

### 修改下属员工信息

`\main\employee_modify\<user_id>`为修改下属员工信息页面，可以选择下属员工或自己，并修改其个人信息，经理以及管理员在右侧导航栏可见。对应函数为`main.employee_modify(user_id)`

### 部门信息

`\main\department\<department_id>`为展示或修改部门信息页面，经理以及管理员在右侧导航栏可见。对应函数为`main.department(department_id)`。

管理员的右侧导航栏中，会依次显示所有部门的名称，作为修改部门信息入口。最后的"+"表示新增部门，会赋予新增部门初始信息后跳转到对应的部门信息展示或修改页面。

### 工资

`main\salary_dispense`为工资发放页面，对经理或管理员可见，列出了所有下属员工的基本工资和迟到早退扣除，以及计算后的真实工资。可以修改基本工资后者迟到早退扣除，在最下方选择对应的工作日期后，同时发放所有工资。对应函数为`main.salary_dispense`

真实工资的动态计算由`static\salary_dispense.js`中的javascript完成。

`main\salaries`为工资单查看页面，对经理或管理员可见，用于查看或删除所有下属员工的已经发放的工资单。对应函数为`main.salaries`。

### SQL查询

`main\sql_query\<query_id>`为SQL查询页面，仅对管理员开放，用于展示预先定义的查询问题的结果，并支持任意SQL查询语句的输入与结果展示，对应函数为`main.sql_query(query_id)`。

对任意SQL查询语句的安全性没有做检查，因为只有管理员才能进入这个页面，安全性由管理员自己负责。

### 提醒

`main\reminder`为频繁迟到、请假提醒页面，当数据库的对应触发器被触发后，在右侧导航栏中这个页面入口处会以数字标签的形式提醒经理或者管理员查看。对应函数为`main.remider`。

### 辅助页面

`main\success`操作成功页面。
`main\denied`权限不足，操作失败页面，当检测到用户试图直接输入地址或者发出http POST请求以绕过权限检测时，会重定向到此页面。



