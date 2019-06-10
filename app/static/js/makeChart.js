// Based on: //https://github.com/benalexkeen/d3-flask-blog-post/blob/master/templates/index.html
// And: https://bl.ocks.org/mbostock/35964711079355050ff1

function preprocessData(data) {
	var n = 0;
	data.forEach(function(d) {
		d.X = n++;
		d.Y = d.value;
	});
}

function scaleAndAxis(data, width, height) {
	// xScale is the active scale used for zooming, xScaleOrig is used as 
	// the original scale that is never changed.
	var xScale = d3.scaleLinear().range([0, width]);
	var xScaleOrig = d3.scaleLinear().range([0, width]);
	var yScale = d3.scaleLinear().range([height, 0]);

	// create the axes
	var xAxis = d3.axisBottom(xScale);
	var yAxis = d3.axisLeft(yScale);

	// turn off ticks on the y axis. We don't want annotators to be 
	// influenced by whether a change is big in the absolute sense.
	yAxis.ticks(0);

	// compute the domains for the axes
	var xExtent = d3.extent(data, function(d) { return d.X; });
	var xRange = xExtent[1] - xExtent[0];
	var xDomainMin = xExtent[0] - xRange * 0.02;
	var xDomainMax = xExtent[1] + xRange * 0.02;

	var yExtent = d3.extent(data, function(d) { return d.Y; });
	var yRange = yExtent[1] - yExtent[0];
	var yDomainMin = yExtent[0] - yRange * 0.05;
	var yDomainMax = yExtent[1] + yRange * 0.05;

	// set the axis domains
	xScale.domain([xDomainMin, xDomainMax]);
	xScaleOrig.domain([xDomainMin, xDomainMax]);
	yScale.domain([yDomainMin, yDomainMax]);

	return [xAxis, yAxis, xScale, xScaleOrig, yScale, yDomainMin, yDomainMax];
}


function noZoom() {
	d3.event.preventDefault();
}

function baseChart(selector, data, clickFunction, annotations, annotationFunction) {
	// preprocess the data
	preprocessData(data);

	var divWidth = 1000;
	var divHeight = 480;

	var svg = d3.select(selector)
		.on("touchstart", noZoom)
		.on("touchmove", noZoom)
		.append("svg")
		.attr("width", divWidth)
		.attr("height", divHeight)
		.attr("viewBox", "0 0 " + divWidth + " " + divHeight);

	var margin = {top: 20, right: 20, bottom: 50, left: 50};
	var width = +svg.attr("width") - margin.left - margin.right;
	var height = +svg.attr("height") - margin.top - margin.bottom;

	var [xAxis, yAxis, xScale, xScaleOrig, yScale, yDomainMin, yDomainMax] = scaleAndAxis(
		data,
		width,
		height);

	// Create the line object
	var lineObj = d3.line()
		.x(function(d) { return xScale(d.X); })
		.y(function(d) { return yScale(d.Y); });

	// Initialise the zoom behaviour
	var zoomObj = d3.zoom()
		.scaleExtent([1, 100])
		.translateExtent([[0, 0], [width, height]])
		.extent([[0, 0], [width, height]])
		.on("zoom", zoomTransform);

	function zoomTransform() {
		transform = d3.event.transform;
		// transform the axis
		xScale.domain(transform.rescaleX(xScaleOrig).domain());

		// transform the data line
		svg.select(".line").attr("d", lineObj);

		// transform the circles
		points.data(data)
			.attr("cx", function(d) { return xScale(d.X); })
			.attr("cy", function(d) { return yScale(d.Y); });

		// transform the annotation lines (if any)
		annoLines = gView.selectAll("line");
		annoLines._groups[0].forEach(function(l) {
			l.setAttribute("x1", xScale(l.getAttribute("cp_idx")));
			l.setAttribute("x2", xScale(l.getAttribute("cp_idx")));
		});

		svg.select(".axis--x").call(xAxis);
	}

	// Build the SVG layer cake
	// There are a few elements to this:
	//
	//  1. a clip path that ensures elements aren't drawn outside the 
	//  axes. This is activated with css
	//  2. axes and x axis label
	//  3. wrapper "g" element with the zoom event
	//  3. rectangle to keep the drawing
	//  4. line
	//  5. circles with a click event
	//

	// clip path
	svg.append("defs")
		.append("clipPath")
		.attr("id", "clip")
		.append("rect")
		.attr("width", width - 18)
		.attr("height", height)
		.attr("transform", "translate(" + 18 + ",0)");

	// y axis
	svg.append("g")
		.attr("class", "axis axis--y")
		.attr("transform", "translate(" + 18 + ",0)")
		.call(yAxis);

	// x axis
	svg.append("g")
		.attr("class", "axis axis--x")
		.attr("transform", "translate(0, " + height + ")")
		.call(xAxis);

	// x axis label
	svg.append("text")
		.attr("text-anchor", "middle")
		.attr("class", "axis-label")
		.attr("transform", "translate(" + (width - 20) + "," + (height + 50) + ")")
		.text("Time");

	// wrapper for zoom
	var gZoom = svg.append("g").call(zoomObj);

	// rectangle for the graph area
	gZoom.append("rect")
		.attr("width", width)
		.attr("height", height);

	// view for the graph
	var gView = gZoom.append("g")
		.attr("class", "view");

	// add the line to the view
	gView.append("path")
		.datum(data)
		.attr("class", "line")
		.attr("d", lineObj);

	// add the points to the view
	var points = gView.selectAll("circle")
		.data(data)
		.enter()
		.append("circle")
		.attr("cx", function(d) { return xScale(d.X); })
		.attr("cy", function(d) { return yScale(d.Y); })
		.attr("data_X", function(d) { return d.X; })
		.attr("data_Y", function(d) { return d.Y; })
		.attr("r", 5)
		.on("click", function(d, i) {
			d.element = this;
			return clickFunction(d, i);
		});

	// handle the annotations
	annotations.forEach(function(a) {
		for (i=0; i<points._groups[0].length; i++) {
			p = points._groups[0][i];
			if (p.getAttribute("data_X") != a.index)
				continue;
			var elem = d3.select(p);
			annotationFunction(a, elem, gView, xScale, yScale, yDomainMin, yDomainMax);
		}
	});
}

function annotateChart(selector, data) {
	function handleClick(d, i) {
		if (d3.event.defaultPrevented) return; // zoomed
		var elem = d3.select(d.element);
		if (elem.classed("changepoint")) {
			elem.style("fill", null);
			elem.classed("changepoint", false);
		} else {
			elem.style("fill", "red");
			elem.classed("changepoint", true);
		}
		updateTable();
	}
	baseChart(selector, data, handleClick, [], null);
}

function viewAnnotations(selector, data, annotations) {
	function handleAnnotation(ann, elem, view, xScale, yScale, yDomainMin, yDomainMax) {
		elem.classed("marked", true);
		view.append("line")
			.attr("cp_idx", ann.index)
			.attr("y1", yScale(yDomainMax))
			.attr("y2", yScale(yDomainMin))
			.attr("x1", xScale(ann.index))
			.attr("x2", xScale(ann.index))
			.attr("class", "ann-line");
	}
	baseChart(selector, data, function() {}, annotations, handleAnnotation);
}

function adminViewAnnotations(selector, data, annotations) {
	function handleAnnotation(ann, elem, view, xScale, yScale, yDomainMin, yDomainMax) {
		elem.classed(ann.user, true);
		view.append("line")
			.attr("cp_idx", ann.index)
			.attr("y1", yScale(yDomainMax))
			.attr("y2", yScale(yDomainMin))
			.attr("x1", xScale(ann.index))
			.attr("x2", xScale(ann.index))
			.attr("class", "ann-line" + " " + ann.user);
	}
	baseChart(selector, data, function() {}, annotations, handleAnnotation);
}
