function updateTable() {
	var changepoints = document.getElementsByClassName("changepoint");

	var myTableDiv = document.getElementById("changepoint-table");

	var old_table = document.getElementById("cp-table");
	old_table.remove();

	var table = document.createElement('TABLE')
	table.id = "cp-table";
	table.className = "table table-striped";

	if (changepoints.length == 0) {
		myTableDiv.appendChild(table);
		return;
	}

	var heading = new Array();
	heading[0] = "#";
	heading[1] = "X";
	heading[2] = "Y";

	// TABLE COLUMNS
	var thead = document.createElement('THEAD');
	thead.className = "thead-dark";
	table.appendChild(thead);
	for (i = 0; i < heading.length; i++) {
		var th = document.createElement('TH')
		th.appendChild(document.createTextNode(heading[i]));
		th.setAttribute("scope", "col");
		thead.appendChild(th);
	}
	var body = document.createElement("TBODY");

	//TABLE ROWS
	for (i = 0; i < changepoints.length; i++) {
		cp = changepoints[i];

		var tr = document.createElement('TR');

		var th = document.createElement('TH');
		th.setAttribute("scope", "row");
		th.appendChild(document.createTextNode(i+1));
		tr.appendChild(th);

		var td = document.createElement('TD');
		td.appendChild(document.createTextNode(
			d3.select(cp).data()[0].X
		));
		tr.appendChild(td);

		var td = document.createElement('TD');
		td.appendChild(document.createTextNode(
			d3.select(cp).data()[0].Y
		));
		tr.appendChild(td);

		body.appendChild(tr);
	}
	table.appendChild(body);
	myTableDiv.appendChild(table);
}
