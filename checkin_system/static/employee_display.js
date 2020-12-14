function Lister(x) {
    const content = x.map((i) =>
        <tr><td><b>{x[0]}：</b></td><td>{x[1]}</td></tr>
    );
    return (
        <table>
            {content}
        </table>
    );
}
function TableRow(row) {
    const tds = row.map((i) => <td>{i}</td>);
    return (
        <tr>{tds}</tr>
    );
}
function Tabler(tags, values) {
    const tag = tags.map((i) => <th>{i}</th>);
    const cont = values.map((i) => <TableRow row={i}></TableRow>);
    return (
        <table border="1">
            <tr>{tag}</tr>
            {cont}
        </table>
    );
}
function BasicInfo(basic_info) {
    return (
        <div>
            <Lister x={[
                ["姓名", basic_info.getElementsByTagName('Name')[0].nodeValue],
                ["性别", basic_info.getElementsByTagName('Gender')[0].nodeValue],
                ["年龄", basic_info.getElementsByTagName('Age')[0].nodeValue],
                ["部门编号", basic_info.getElementsByTagName('DepartmentID')[0].nodeValue],
                ["部门名称", basic_info.getElementsByTagName('Department')[0].nodeValue],
                ["员工等级", basic_info.getElementsByTagName('Level')[0].nodeValue]
            ]}></Lister>
        </div>
    );
}
function Salaries(salaries) {
    const tags = ["工资单编号", "部门编号", "基本工资", "缺勤早退扣除", "应发工资", "工作年限", "发放时间", "审核者ID", "审核者姓名"]
    const cont = salaries.childNode.map((x) => x.childeNode.map((y) => y.nodeValue));
    return (
        <Tabler tags={tags} values={cont}>
        </Tabler>
    );
}
function Latings(latings) {
    const tags = ["迟到编号", "迟到日期", "迟到时长"]
    const cont = latings.childNode.map((x) => x.childeNode.map((y) => y.nodeValue));
    return (
        <Tabler tags={tags} values={cont}>
        </Tabler>
    );
}
function Leaves(leaves) {
    const tags = ["请假条编号", "请假开始日期", "请假结束日期", "请假原因", "申请日期", "审核人"]
    const cont = leaves.childNode.map((x) => x.childeNode.map((y) => y.nodeValue));
    return (
        <Tabler tags={tags} values={cont}>
        </Tabler>
    );
}
function EmployeeDisplay(employee_id, xml_doc) {
    employee = xml_doc.documentElement.getElementsByTagName("Employee")[0];
    return (
        <div>
            <hr />
            <p>员工编号： {employee.firstChild.nodeValue}</p>
            <BasicInfo basic_info={employee.getElementsByTagName("BasicInfo")[0]}></BasicInfo>
            <hr />
            <Salaries salaries={employee.getElementsByTagName("Salaries")[0]}></Salaries>
            <hr />
            <Latings latings={employee.getElementsByTagName("Latings")[0]}></Latings>
            <hr />
            <Leaves leaves={employee.getElementsByTagName("Leaves")[0]}></Leaves>
            <hr />
        </div >
    );
}

class EmployeeSelection extends React.Component {
    constructor(options) {
        this.state = { value: '' };
        this.options = options

        this.handleChange = this.handleChange.bind(this);

        this.xhttp = new XMLHttpRequest();

        const domContainer = document.getElementById('employee_display');

        this.xhttp.onreadystatechange = function () {
            if (xhttp.readyState == 4 && xhttp.status == 200)
                ReactDOM.render(EmployeeDisplay(this.state.value, xhttp.responseXML), domContainer);
        };

        this.xhttp.open('GET', 'employee_display.xml?user_id=' + this.state.value, true);
        this.xhttp.send();
    }

    handleChange(event) {
        this.setState({ value: event.target.value });
        this.xhttp.open('GET', 'employee_display.xml?user_id=' + this.state.value, true);
        this.xhttp.send();
    }


    render() {
        return (
            <form>
                <label> 选择展示员工:
                    <selection value={this.state.value} onChange={this.handleChange}>
                        {this.options}
                    </selection>
                </label>
            </form>
        );
    }
}


var xhttp = new XMLHttpRequest();

const domContainer = document.getElementById('employee_display');

xhttp.open('GET', 'employee_display.xml?user_id=' + domContainer.employee_id, true);

xhttp.onreadystatechange = function () {
    if (xhttp.readyState == 4 && xhttp.status == 200)
        ReactDOM.render(EmployeeDisplay(domContainer.employee_id, xhttp.responseXML), domContainer);
};

xhttp.send();

const selection = document.getElementById('employee_selection')
ReactDom.render(<EmployeeSelection />, selection)