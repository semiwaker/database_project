function Lister(props) {
    const x = props.x;
    const content = x.map((i) =>
        <tr><td><strong>{i[0]}</strong></td><td>{i[1]}</td></tr>
    );
    return (
        <table class="table table-hover table-bordered">
            <tbody>
                {content}
            </tbody>
        </table>
    );
}
function TableRow(props) {
    const row = props.row;
    const tds = row.map((i) => <td>{i}</td>);
    return (
        <tr>{tds}</tr>
    );
}
function Tabler(props) {
    const tags = props.tags;
    const values = props.values;
    const tag = tags.map((i) => <th>{i}</th>);
    const cont = values.map((i) => <TableRow row={i}></TableRow>);
    return (
        <table class="table table-hover table-bordered">
            <thead><tr>{tag}</tr></thead>
            <tbody>{cont}</tbody>
        </table>
    );
}
function BasicInfo(props) {
    const basic_info = props.basic_info;
    return (
        <div>
            <Lister x={[
                ["姓名", basic_info.getElementsByTagName('Name')[0].innerHTML],
                ["性别", basic_info.getElementsByTagName('Gender')[0].innerHTML],
                ["出生日期", basic_info.getElementsByTagName('Birthdate')[0].innerHTML],
                ["年龄", basic_info.getElementsByTagName('Age')[0].innerHTML],
                ["电子邮件", basic_info.getElementsByTagName('Email')[0].innerHTML],
                ["电话号码", basic_info.getElementsByTagName('Phone')[0].innerHTML],
                ["部门编号", basic_info.getElementsByTagName('DepartmentID')[0].innerHTML],
                ["部门名称", basic_info.getElementsByTagName('Department')[0].innerHTML],
                ["员工等级", basic_info.getElementsByTagName('Level')[0].innerHTML]
            ]}></Lister>
        </div>
    );
}
function GetCont(x, tag) {
    const len = x.length;
    var i, j;
    var cont = [];
    for (i = 0; i < len; i++) {
        const l2 = x[i].childNodes.length;
        var c = [];
        for (j = 0; j < l2; j++) {
            if (x[i].childNodes[j].nodeName != "#text")
                c.push(x[i].childNodes[j].innerHTML);
        }
        cont.push(c)
    }
    return cont
}
function Salaries(props) {
    const salaries = props.salaries
    const tags = ["工资单编号", "部门编号", "基本工资", "缺勤早退扣除", "应发工资", "对应工作时间", "发放时间", "审核者ID", "审核者姓名"];
    // console.log(salaries.getElementsByTagName('Salary'));
    const cont = GetCont(salaries.getElementsByTagName('Salary'));
    return (
        <Tabler tags={tags} values={cont}>
        </Tabler>
    );
}

function Latings(props) {
    const latings = props.latings;
    const tags = ["迟到编号", "迟到日期", "迟到时长"];
    const cont = GetCont(latings.getElementsByTagName("Lating"));
    return (
        <Tabler tags={tags} values={cont}>
        </Tabler>
    );
}
function Leaves(props) {
    const leaves = props.leaves;
    const tags = ["请假条编号", "请假开始日期", "请假结束日期", "请假原因", "申请日期", "审核人"];
    const cont = GetCont(leaves.getElementsByTagName("Leave"));
    return (
        <Tabler tags={tags} values={cont}>
        </Tabler>
    );
}
function EmployeeDisplay(employee_id, xml_doc) {
    // console.log(employee_id);
    // console.log(xml_doc);
    const employee = xml_doc.documentElement.getElementsByTagName("Employee")[0];
    // console.log(employee.getElementsByTagName("")[0])
    return (
        <div>
            <p><strong>员工编号：</strong> {employee.getElementsByTagName("EmployeeID")[0].innerHTML}</p>
            <BasicInfo basic_info={employee.getElementsByTagName("BasicInfo")[0]}></BasicInfo>
            <hr />
            <Salaries salaries={employee.getElementsByTagName("Salaries")[0]}></Salaries>
            <hr />
            <Latings latings={employee.getElementsByTagName("Latings")[0]}></Latings>
            <hr />
            <Leaves leaves={employee.getElementsByTagName("Leaves")[0]}></Leaves>
        </div >
    );
}

class EmployeeSelection extends React.Component {
    constructor(props) {
        super(props);
        this.state = { value: props.user_id };
        this.props = props;

        this.handleChange = this.handleChange.bind(this);

        this.xhttp = new XMLHttpRequest();


        this.render_display = this.render_display.bind(this);
        this.xhttp.onreadystatechange = this.render_display;

        this.xhttp.open('GET', 'employee_info_' + this.state.value + '.xml', true);
        this.xhttp.send();
    }

    render_display() {
        if (this.xhttp.readyState == 4 && this.xhttp.status == 200) {
            console.log('render')
            console.log(this.state.value)
            const domContainer = document.getElementById('employee_display');
            ReactDOM.render(EmployeeDisplay(this.state.value, this.xhttp.responseXML), domContainer);
        }
    }

    handleChange(event) {
        this.setState({ value: event.target.value });
        console.log(event.target.value);
        // console.log(this.state.value)
        this.xhttp = new XMLHttpRequest();
        this.xhttp.onreadystatechange = this.render_display;
        this.xhttp.open('GET', 'employee_info_' + event.target.value + '.xml', true);
        this.xhttp.send();
    }

    render() {
        // console.log(this.props.users)
        const cont = this.props.users.map(
            (x) => <option value={x[0]}> {x[1]} </option>
        );
        // console.log(cont)
        return (
            <form>
                <label> 选择展示员工:
                    <select value={this.state.value} onChange={this.handleChange} class="form-control">
                        {cont}
                    </select>
                </label>
            </form>
        );
    }
}


var xhttp = new XMLHttpRequest();

const domContainer = document.getElementById('employee_display');

xhttp.open('GET', 'employee_info_' + domContainer.getAttribute("employee_id") + '.xml', true);

xhttp.onreadystatechange = function () {
    if (xhttp.readyState == 4 && xhttp.status == 200) {
        // console.log(xhttp.response)
        // console.log(xhttp.responseType)
        // console.log(xhttp.responseXML)
        ReactDOM.render(EmployeeDisplay(domContainer.getAttribute("employee_id"), xhttp.responseXML), domContainer);
    }
};

xhttp.send();

const selection = document.getElementById('employee_selection')
if (selection) {
    // console.log(selection.getAttribute('user_id'))
    // console.log(selection.getAttribute('users'))
    const user_id = JSON.parse(selection.getAttribute("user_id"))
    const users = JSON.parse(selection.getAttribute('users').replace(/'/g, '"'))
    ReactDOM.render(<EmployeeSelection user_id={user_id} users={users} />, selection)
}