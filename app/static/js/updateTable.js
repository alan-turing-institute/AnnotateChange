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

function updateTableMulti(numCharts) {
	var changepoints = document.getElementsByClassName('changepoint');
	var myTableDiv = document.getElementById('changepoint-table');
	var oldTable = document.getElementById('cp-table');
	oldTable.remove();

	var table = document.createElement('TABLE');
	table.id = 'cp-table';
	table.className = 'table table-striped';
	if (changepoints.length == 0) {
		myTableDiv.appendChild(table);
		return;
	}

	var heading = new Array();
	heading[0] = "#";
	heading[1] = "X";
	for (j=0; j<numCharts; j++)
		heading[2+j] = "Y" + (j + 1);

	// Table Columns
	var thead = document.createElement('THEAD');
	thead.className = 'thead-dark';
	table.appendChild(thead);
	for (i=0; i<heading.length; i++) {
		var th = document.createElement('TH');
		th.appendChild(document.createTextNode(heading[i]));
		th.setAttribute("scope", "col");
		thead.appendChild(th);
	}

	var consolidated = {};
	var keys = [];
	for (i=0; i<changepoints.length; i++) {
		cp = changepoints[i];
		data = d3.select(cp).data()[0];
		if (!(data.X in consolidated)) {
			consolidated[data.X] = {}
			keys.push(data.X);
		}
		id_parts = cp.id.split('-')
		yindex = id_parts[id_parts.length - 1];
		consolidated[data.X][yindex] = data.Y;
	}
	keys.sort(function(a, b) { return parseInt(a) - parseInt(b); });

	var body = document.createElement("TBODY");
	for (i=0; i<keys.length; i++) {
		X = keys[i];
		cp = consolidated[keys[i]];

		var tr = document.createElement('TR');

		var th = document.createElement('TH');
		th.setAttribute("scope", "row");
		th.appendChild(document.createTextNode(i+1));
		tr.appendChild(th);

		var td = document.createElement('TD');
		td.appendChild(document.createTextNode(X));
		tr.appendChild(td);

		for (j=0; j<numCharts; j++) {
			var td = document.createElement('TD');
			td.appendChild(document.createTextNode(cp['y' + j]));
			tr.appendChild(td);
		}

		body.appendChild(tr);
	}
	table.appendChild(body);
	myTableDiv.appendChild(table);
}
