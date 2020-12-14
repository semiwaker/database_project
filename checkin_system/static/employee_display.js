function employee_display(employee_id, xml_doc) {

}


var xhttp = new XMLHttpRequest();

const domContainer = document.getElementById('employee_display');

xhttp.open('GET', 'employee_display.xml?user_id=' + domContainer.employee_id, true)

xhttp.onreadystatechange = function () {
    if (this.readyState == 4 && this.status == 200)
        ReactDOM.render(employee_display(domContainer.employee_id, xhttp.responseXML), domContainer);
}

xhttp.send()
