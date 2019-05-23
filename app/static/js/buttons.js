function resetOnClick() {
	var changepoints = d3.selectAll(".changepoint");
	changepoints.each(function(d, i) {
		var elem = d3.select(this);
		elem.classed("changepoint", false);
		elem.style("fill", "blue");
	});
	updateTable();
}

function noCPOnClick(task_id) {
	var changepoints = document.getElementsByClassName("changepoint");
	// validation
	if (changepoints.length > 0) {
		$('#NoCPYesCPModal').modal();
		return;
	}

	var obj = {
		task: task_id,
		changepoints: null
	};

	var xhr = new XMLHttpRequest();
	xhr.open("POST", "");
	xhr.withCredentials = true;
	xhr.setRequestHeader("Content-Type", "application/json");
	xhr.send(JSON.stringify(obj));
	xhr.onreadystatechange = function() {
		if (xhr.readyState == XMLHttpRequest.DONE) {
			if (xhr.status === 200)
				window.location.href = xhr.responseText;
		} else {
			console.log("Error: " + xhr.status);
		}
	};
}

function submitOnClick(task_id) {
	var changepoints = document.getElementsByClassName("changepoint");
	// validation
	if (changepoints.length === 0) {
		$('#submitNoCPModal').modal();
		return;
	}

	var obj = {};
	obj["task"] = task_id;
	obj["changepoints"] = [];
	var i, cp;
	for (i=0; i<changepoints.length; i++) {
		cp = changepoints[i];
		elem = {
			id: i,
			x: cp.getAttribute("data_X"),
			y: cp.getAttribute("data_Y")
		};
		obj["changepoints"].push(elem);
	}

	var xhr = new XMLHttpRequest();
	xhr.open("POST", "");
	xhr.withCredentials = true;
	xhr.setRequestHeader("Content-Type", "application/json");
	xhr.send(JSON.stringify(obj));
	xhr.onreadystatechange = function() {
		if (xhr.readyState == XMLHttpRequest.DONE) {
			if (xhr.status === 200)
				window.location.href = xhr.responseText;
		} else {
			console.log("Error: " + xhr.status);
		}
	};
}

