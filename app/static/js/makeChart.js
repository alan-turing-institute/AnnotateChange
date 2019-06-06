// Based on: //https://github.com/benalexkeen/d3-flask-blog-post/blob/master/templates/index.html
// And: https://bl.ocks.org/mbostock/35964711079355050ff1

function makeChart(selector, data) {
	var n = 0;
	data.forEach(function(d) {
		d.X = n++;
		d.Y = d.value;
	});

	var divWidth = 1000;
	var divHeight = 480;

	var svg = d3.select(selector)
		.on("touchstart", nozoom)
		.on("touchmove", nozoom)
		.append("svg")
		.attr("width", divWidth)
		.attr("height", divHeight);

	var margin = {top: 20, right: 20, bottom: 50, left: 50};
	var width = +svg.attr("width") - margin.left - margin.right;
	var height = +svg.attr("height") - margin.top - margin.bottom;

	var zoom = d3.zoom()
		.scaleExtent([1, 50])
		.translateExtent([[0, 0], [width, height]])
		.extent([[0, 0], [width, height]])
		.on("zoom", zoomed);

	var x = d3.scaleLinear().range([0, width]);
	var x2 = d3.scaleLinear().range([0, width]);
	var y = d3.scaleLinear().range([height, 0]);

	var xAxis = d3.axisBottom(x);
	var yAxis = d3.axisLeft(y);
	yAxis.ticks(0);

	var xExtent = d3.extent(data, function(d) { return d.X; });
	var xRange = xExtent[1] - xExtent[0];
	var xDomainMin = xExtent[0] - xRange * 0.02;
	var xDomainMax = xExtent[1] + xRange * 0.02;

	var yExtent = d3.extent(data, function(d) { return d.Y; });
	var yRange = yExtent[1] - yExtent[0];
	var yDomainMin = yExtent[0] - yRange * 0.05;
	var yDomainMax = yExtent[1] + yRange * 0.05;

	x.domain([xDomainMin, xDomainMax]);
	y.domain([yDomainMin, yDomainMax]);
	x2.domain(x.domain());

	svg.append("defs").append("clipPath")
		.attr("id", "clip")
		.append("rect")
		.attr("width", width - 18)
		.attr("height", height)
		.attr("transform", "translate(" + 18 + ",0)");

	svg.append("g")
		.attr("class", "axis axis--y")
		.attr("transform", "translate(" + 18 + ",0)")
		.call(yAxis);

	svg.append("g")
		.attr("class", "axis axis--x")
		.attr("transform", "translate(0," + height + ")")
		.call(xAxis);

	svg.append("text")
		.attr("text-anchor", "middle")
		.attr("class", "axis-label")
		.attr("transform", "translate(" + (width - 20) + "," + (height + 50) + ")")
		.text("Time");

	var line = d3.line()
		.x(function(d) { return x(d.X); })
		.y(function(d) { return y(d.Y); });

	var g = svg.append("g")
		.call(zoom);

	g.append("rect")
		.attr("width", width)
		.attr("height", height);

	var view = g.append("g")
		.attr("class", "view");

	view.append("path")
		.datum(data)
		.attr("class", "line")
		.attr("d", line);

	var points = view.selectAll("circle")
		.data(data)
		.enter().append("circle")
		.attr("cx", function(d) { return x(d.X); })
		.attr("cy", function(d) { return y(d.Y); })
		.attr("data_X", function(d) { return d.X; })
		.attr("data_Y", function(d) { return d.Y; })
		.attr("r", 5)
		.on("click", clicked);

	function zoomed() {
		t = d3.event.transform;
		x.domain(t.rescaleX(x2).domain());
		svg.select(".line").attr("d", line);
		points.data(data)
			.attr("cx", function(d) { return x(d.X); })
			.attr("cy", function(d) { return y(d.Y); });
		svg.select(".axis--x").call(xAxis);
	}

	function clicked(d, i) {
		if (d3.event.defaultPrevented) return; // zoomed

		// this function handles changepoint marking
		var elem = d3.select(this);
		if (elem.classed("changepoint")) {
			elem.style("fill", "blue");
			elem.classed("changepoint", false);
		} else {
			elem.style("fill", "red");
			elem.classed("changepoint", true);
		}
		updateTable();
	}

	function nozoom() {
		d3.event.preventDefault();
	}
}

function makeChartAnnotated(selector, data, annotations) {
	var n = 0;
	data.forEach(function(d) {
		d.X = n++;
		d.Y = d.value;
	});

	var divWidth = 1000;
	var divHeight = 480;

	var svg = d3.select(selector)
		.on("touchstart", nozoom)
		.on("touchmove", nozoom)
		.append("svg")
		.attr("width", divWidth)
		.attr("height", divHeight)
		.attr("viewBox", "0 0 " + divWidth + " " + divHeight);

	var margin = {top: 20, right: 20, bottom: 50, left: 50};
	var width = +svg.attr("width") - margin.left - margin.right;
	var height = +svg.attr("height") - margin.top - margin.bottom;

	var zoom = d3.zoom()
		.scaleExtent([1, 50])
		.translateExtent([[0, 0], [width, height]])
		.extent([[0, 0], [width, height]])
		.on("zoom", zoomed);

	var x = d3.scaleLinear().range([0, width]);
	var x2 = d3.scaleLinear().range([0, width]);
	var y = d3.scaleLinear().range([height, 0]);

	var xAxis = d3.axisBottom(x);
	var yAxis = d3.axisLeft(y);
	yAxis.ticks(0);

	var xExtent = d3.extent(data, function(d) { return d.X; });
	var xRange = xExtent[1] - xExtent[0];
	var xDomainMin = xExtent[0] - xRange * 0.02;
	var xDomainMax = xExtent[1] + xRange * 0.02;

	var yExtent = d3.extent(data, function(d) { return d.Y; });
	var yRange = yExtent[1] - yExtent[0];
	var yDomainMin = yExtent[0] - yRange * 0.05;
	var yDomainMax = yExtent[1] + yRange * 0.05;

	x.domain([xDomainMin, xDomainMax]);
	y.domain([yDomainMin, yDomainMax]);
	x2.domain(x.domain());

	svg.append("defs").append("clipPath")
		.attr("id", "clip")
		.append("rect")
		.attr("width", width - 18)
		.attr("height", height)
		.attr("transform", "translate(" + 18 + ",0)");

	svg.append("g")
		.attr("class", "axis axis--y")
		.attr("transform", "translate(" + 18 + ",0)")
		.call(yAxis);

	svg.append("g")
		.attr("class", "axis axis--x")
		.attr("transform", "translate(0," + height + ")")
		.call(xAxis);

	svg.append("text")
		.attr("text-anchor", "middle")
		.attr("class", "axis-label")
		.attr("transform", "translate(" + (width - 20) + "," + (height + 50) + ")")
		.text("Time");

	var line = d3.line()
		.x(function(d) { return x(d.X); })
		.y(function(d) { return y(d.Y); });

	var g = svg.append("g")
		.call(zoom);

	g.append("rect")
		.attr("width", width)
		.attr("height", height);

	var view = g.append("g")
		.attr("class", "view");

	view.append("path")
		.datum(data)
		.attr("class", "line")
		.attr("d", line);

	var points = view.selectAll("circle")
		.data(data)
		.enter().append("circle")
		.attr("cx", function(d) { return x(d.X); })
		.attr("cy", function(d) { return y(d.Y); })
		.attr("data_X", function(d) { return d.X; })
		.attr("data_Y", function(d) { return d.Y; })
		.attr("r", 5);

	function zoomed() {
		t = d3.event.transform;
		x.domain(t.rescaleX(x2).domain());
		svg.select(".line").attr("d", line);
		points.data(data)
			.attr("cx", function(d) { return x(d.X); })
			.attr("cy", function(d) { return y(d.Y); });
		svg.select(".axis--x").call(xAxis);
	}

	function nozoom() {
		d3.event.preventDefault();
	}

	annotations.forEach(function(a) {
		for (i=0; i<points._groups[0].length; i++) {
			p = points._groups[0][i];
			if (p.getAttribute("data_X") == a.index) {
				var elem = d3.select(p);
				elem.classed("marked", "true");
				view.append("line")
					.attr("cp_idx", a.index)
					.attr("y1", y(yDomainMax))
					.attr("y2", y(yDomainMin))
					.attr("x1", x(a.index))
					.attr("x2", x(a.index))
					.attr("class", "ann-line");
				break;
			}
		}
	});
}

function makeChartAnnotatedAdmin(selector, data, annotations) {
	var n = 0;
	data.forEach(function(d) {
		d.X = n++;
		d.Y = d.value;
	});

	var divWidth = 1000;
	var divHeight = 480;

	var svg = d3.select(selector)
		.on("touchstart", nozoom)
		.on("touchmove", nozoom)
		.append("svg")
		.attr("width", divWidth)
		.attr("height", divHeight);

	var margin = {top: 20, right: 20, bottom: 50, left: 50};
	var width = +svg.attr("width") - margin.left - margin.right;
	var height = +svg.attr("height") - margin.top - margin.bottom;

	var zoom = d3.zoom()
		.scaleExtent([1, 50])
		.translateExtent([[0, 0], [width, height]])
		.extent([[0, 0], [width, height]])
		.on("zoom", zoomed);

	var x = d3.scaleLinear().range([0, width]);
	var x2 = d3.scaleLinear().range([0, width]);
	var y = d3.scaleLinear().range([height, 0]);

	var xAxis = d3.axisBottom(x);
	var yAxis = d3.axisLeft(y);

	var xExtent = d3.extent(data, function(d) { return d.X; });
	var xRange = xExtent[1] - xExtent[0];
	var xDomainMin = xExtent[0] - xRange * 0.02;
	var xDomainMax = xExtent[1] + xRange * 0.02;

	var yExtent = d3.extent(data, function(d) { return d.Y; });
	var yRange = yExtent[1] - yExtent[0];
	var yDomainMin = yExtent[0] - yRange * 0.05;
	var yDomainMax = yExtent[1] + yRange * 0.05;

	x.domain([xDomainMin, xDomainMax]);
	y.domain([yDomainMin, yDomainMax]);
	x2.domain(x.domain());

	svg.append("defs").append("clipPath")
		.attr("id", "clip")
		.append("rect")
		.attr("width", width - 30)
		.attr("height", height)
		.attr("transform", "translate(" + 30 + ",0)");

	svg.append("g")
		.attr("class", "axis axis--y")
		.attr("transform", "translate(" + 30 + ",0)")
		.call(yAxis);

	svg.append("g")
		.attr("class", "axis axis--x")
		.attr("transform", "translate(0," + height + ")")
		.call(xAxis);

	svg.append("text")
		.attr("text-anchor", "middle")
		.attr("class", "axis-label")
		.attr("transform", "translate(" + (width - 20) + "," + (height + 50) + ")")
		.text("Time");

	var line = d3.line()
		.x(function(d) { return x(d.X); })
		.y(function(d) { return y(d.Y); });

	var g = svg.append("g")
		.call(zoom);

	g.append("rect")
		.attr("width", width)
		.attr("height", height);

	var view = g.append("g")
		.attr("class", "view");

	view.append("path")
		.datum(data)
		.attr("class", "line")
		.attr("d", line);

	var points = view.selectAll("circle")
		.data(data)
		.enter().append("circle")
		.attr("cx", function(d) { return x(d.X); })
		.attr("cy", function(d) { return y(d.Y); })
		.attr("data_X", function(d) { return d.X; })
		.attr("data_Y", function(d) { return d.Y; })
		.attr("r", 5)
		.on("click", clicked);

	function zoomed() {
		t = d3.event.transform;
		x.domain(t.rescaleX(x2).domain());
		svg.select(".line").attr("d", line);
		points.data(data)
			.attr("cx", function(d) { return x(d.X); })
			.attr("cy", function(d) { return y(d.Y); });
		annolines = view.selectAll("line");
		annolines._groups[0].forEach(function(l) {
			l.setAttribute("x1", x(l.getAttribute("cp_idx")));
			l.setAttribute("x2", x(l.getAttribute("cp_idx")));
		});
		svg.select(".axis--x").call(xAxis);
	}

	function clicked(d, i) {
		if (d3.event.defaultPrevented) return; // zoomed
	}

	function nozoom() {
		d3.event.preventDefault();
	}

	annotations.forEach(function(a) {
		for (i=0; i<points._groups[0].length; i++) {
			p = points._groups[0][i];
			if (p.getAttribute("data_X") == a.index) {
				var elem = d3.select(p);
				elem.classed(a.user, 'true');
				view.append("line")
					.attr("cp_idx", a.index)
					.attr("y1", y(yDomainMax))
					.attr("y2", y(yDomainMin))
					.attr("x1", x(a.index))
					.attr("x2", x(a.index))
					.attr("class", "ann-line" + " " + a.user);
			}
		}
	});
}
