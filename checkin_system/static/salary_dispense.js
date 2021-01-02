class SalaryCalulator extends React.Component {
    constructor(props) {
        super(props)
        this.props = props;
        // console.log(props)
        this.handleBasicChange = this.handleBasicChange.bind(this);
        this.handleDeductionChange = this.handleDeductionChange.bind(this);
        this.state = { basic: props.basicSalary, deduction: props.deduction, real_salary: props.realSalary };
    }
    handleBasicChange(event) {
        const basic = event.target.value
        this.setState({ basic: basic, deduction: this.state.deduction, real_salary: basic - this.state.deduction });
    }
    handleDeductionChange(event) {
        const deduction = event.target.value
        this.setState({ basic: this.state.basic, deduction: deduction, real_salary: this.state.basic - deduction });
    }
    render() {
        const basic = this.state.basic;
        const deduction = this.state.deduction;
        const real_salary = this.state.real_salary;
        const salaryNo = this.props.salaryNo
        const employee_id = this.props.employee_id
        const employee_name = this.props.employee_name
        // console.log(employee_id)
        // console.log(employee_name)
        return (
            <tr>
                <td>{salaryNo}</td>
                <td>{employee_id}</td>
                <td>{employee_name}</td>
                <td>{this.props.departmentID}</td>
                <td><input type="number" name={"basic" + salaryNo} value={basic} onChange={this.handleBasicChange} class="form-control" required /></td>
                <td><input type="number" name={"deduction" + salaryNo} value={deduction} onChange={this.handleDeductionChange} class="form-control" required /></td>
                <td><input type="number" name={"realSalary" + salaryNo} value={real_salary} class="form-control" readOnly /></td>
            </tr>
        );
    }
}
class SalaryDispense extends React.Component {
    constructor(props) {
        super(props)
        this.salaries = props.salaries;
        // console.log(this.salaries)
    }
    render() {
        const content = this.salaries.map(
            (x) => <SalaryCalulator salaryNo={x[0]} employee_id={x[1]} employee_name={x[2]} departmentID={x[3]} basicSalary={x[4]} deduction={x[5]} realSalary={x[6]} />
        );
        return (
            <form method="post">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>工资单编号</th>
                            <th>员工编号</th>
                            <th>员工姓名</th>
                            <th>部门编号</th>
                            <th>基本工资</th>
                            <th>缺勤早退扣除</th>
                            <th>应发工资</th>
                        </tr>
                    </thead>
                    <tbody>
                        {content}
                        <tr>
                            <td colSpan="4">
                                <div class="form_group">
                                    <label>对应工作日期</label>
                                    <input type="month" name="workTime" class="form-control" required/>
                                </div>
                            </td>
                            <td ><button type="submit" class="btn btn-primary" >发放</button></td>
                        </tr>
                    </tbody>
                </table>
            </form>
        );
    }
}

const domContainer = document.getElementById('salary_dispense');
// console.log(domContainer.getAttribute("salaries").replace(/'/g, '"'))
const salaries = JSON.parse(domContainer.getAttribute("salaries").replace(/'/g, '"'))
ReactDOM.render(<SalaryDispense salaries={salaries} />, domContainer)
