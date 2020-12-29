class SalaryCalulator extends React.Component {
    constructor(props) {
        super(props)
        this.props = props;
        this.handleBasicChange = this.handleBasicChange.bind(this);
        this.handleDeductionChange = this.handleDeductionChange.bind(this);
        this.state = { basic: props.basicSalary, deduction: props.deduction, real_salary: props.realSalary };
    }
    handleBasicChange(basic) {
        this.setState({ basic: basic, deduction: this.state.deduction, real_salary: basic - this.state.deduction });
    }
    handleDeductionChange(deduction) {
        this.setState({ basic: this.state.basic, deduction: deduction, real_salary: this.state.basic - deduction });
    }
    render() {
        const basic = this.state.basic;
        const deduction = this.state.deduction;
        const real_salary = this.state.real_salary;
        const salaryNo = this.props.salaryNo
        return (
            <tr>
                <td>{salaryNo}</td>
                <td>{this.props.departmentID}</td>
                <td><input type="number" name={"basic" + salaryNo} value={basic} onChange={this.handleBasicChange} required /></td>
                <td><input type="number" name={"deduction" + salaryNo} value={deduction} onChange={this.handleDeductionChange} required /></td>
                <td><input type="number" name={"realSalary" + salaryNo} value={real_salary} readOnly /></td>
            </tr>
        );
    }
}
class SalaryDispense extends React.Component {
    constructor(props) {
        this.salaries = props.salaries;
    }
    render() {
        const content = this.salaries.map(
            (x) => <SalaryCalulator salaryNo={x[0]} departmentID={x[1]} basicSalary={x[2]} deduction={x[3]} realSalary={x[4]} />
        );
        return (
            <form method="post">
                <table>
                    <tr>
                        <th>工资单编号</th>
                        <th>部门编号</th>
                        <th>基本工资</th>
                        <th>缺勤早退扣除</th>
                        <th>应发工资</th>
                    </tr>
                    {content}
                    <tr>
                        <td colSpan="5" align="right">对应工作日期<input type="month" id="workTime" /></td>
                        <td ><input type="submit" >发放</input></td>
                    </tr>
                </table>
            </form>
        );
    }
}

const domContainer = document.getElementById('salary_dispense');
ReactDom.render(<SalaryDispense salaries={selection.salaries} />, SalaryDispense)
