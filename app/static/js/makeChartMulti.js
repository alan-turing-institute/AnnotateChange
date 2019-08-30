// Based on: https://tylernwolf.com/corrdisp/index.html

/*
# TODO NOTES:
- we now have two definitions of the data (data and labelData). The best thing 
would be to preprocess the data such that it is formatted as labelData (probably)
*/

/*
 * Our data is a struct with top-level keys "time" (optional) and "values" 
 * (required). The "values" object is an array with a variable length of 
 * variables.
 */

function preprocess(data) {
	var cleanData = [];
	var nVar = data.values.length;

	if (data["time"] != null) {
		console.warn("Time axis is not implemented yet. Ignoring.");
	}
	for (i=0; i<data.values[0].raw.length; i++) {
		var item = {"X": i}
		for (j=0; j<nVar; j++) {
			item["Y" + j] = data.values[j].raw[i];
		}
		cleanData.push(item);
	}
	return cleanData;
}


function getLabelData(data, lbl) {
	var lblData = [];
	for (i=0; i<data.length; i++) {
		if (isNaN(data[i][lbl]))
			continue;
		var item = {"X": data[i]["X"], "Y": data[i][lbl]};
		lblData.push(item);
	}
	return lblData;
}

function makeLabelData(data, numCharts) {
	var labelData = {};
	for (j=0; j<numCharts; j++) {
		labelData[j] = getLabelData(data, "Y"+j);
	}
	return labelData;
}

function Axes(data, numCharts, width, lineHeight, chartPadding) {
	this.chartColors = d3.scaleOrdinal();

	var xRange = data.length;
	var xDomainMin = 0 - xRange * 0.02;
	var xDomainMax = data.length + xRange * 0.02;

	// NOTE: domain needs to be adapted if we provide a time axis
	this.xScale = d3.scaleLinear()
		.domain([xDomainMin, xDomainMax])
		.range([0, width]);

	this.xScaleOrig = d3.scaleLinear()
		.domain([xDomainMin, xDomainMax])
		.range([0, width]);

	this.xAxis = d3.axisBottom(this.xScale);

	var labels = [];
	var chartRange = [];

	for (j=0; j<numCharts; j++) {
		var v = [];
		for (i=0; i<data.length; i++)
			v.push(data[i]["Y" + j]);

		var extent = d3.extent(v);
		var range = extent[1] - extent[0];
		var minVal = extent[0] - range * 0.05;
		var maxVal = extent[1] + range * 0.05;

		this["yScale" + j] = d3.scaleLinear();
		this["yScale" + j].domain([minVal, maxVal]);
		this["yScale" + j].range([lineHeight, 0]);

		labels.push("Y" + j);
		chartRange.push(j * (lineHeight + chartPadding));
	}

	this.charts = d3.scaleOrdinal();
	this.charts.domain(labels);
	this.charts.range(chartRange);
};


function baseChart(selector, data, clickFunction, annotations, annotationFunction) {
	var lineObjects = {};
	var pointSets = {}

	/* Note:
	 * It may be tempting to scale the width/height of the div to be 
	 * proportional to the size of the window. However this may cause some 
	 * users with wide screens to perceive changes in the time series 
	 * differently than others because the horizontal axis is more 
	 * stretched out. It is therefore better to keep the size of the graph 
	 * the same for all users.
	 */
	var lineHeight = 150;
	var lineWidth = 1000;

	var chartPadding = 30;

	var visPadding = {
		top: 10,
		right: 0,
		bottom: 10,
		left: 0,
		middle: 50
	};

	// Data preprocessing (TODO: remove need to have labelData *and*
	// preprocess!)
	var numCharts = data.values.length;
	data = preprocess(data);
	var labelData = makeLabelData(data, numCharts);

	var width = lineWidth - visPadding.middle;
	var height = (chartPadding + lineHeight) * numCharts + chartPadding + 50;

	var axes = new Axes(data, numCharts, width, lineHeight, chartPadding);

	var zoomObj = d3.zoom()
		.scaleExtent([1, 100])
		.translateExtent([[0, 0], [width, height]])
		.extent([[0, 0], [width, height]])
		.on("zoom", zoomTransform);

	function zoomTransform() {
		transform = d3.event.transform;

		// transform the axes
		axes.xScale.domain(transform.rescaleX(axes.xScaleOrig).domain());

		// transform the data lines
		for (j=0; j<numCharts; j++) {
			bigWrapper.select("#line-"+j).attr("d", lineObjects[j]);
		}

		// transform the points
		for (j=0; j<numCharts; j++) {
			pointSets[j].data(labelData[j])
				.attr("cx", function(d) { return axes.xScale(d.X); })
				.attr("cy", function(d) { return axes["yScale" + j](d.Y); })
		}

		svg.select(".x-axis").call(axes.xAxis);

		// transform the annotation lines (if any)
		annoLines = bigWrapper.selectAll(".ann-line")
		annoLines._groups[0].forEach(function(l) {
			l.setAttribute("x1", axes.xScale(l.getAttribute("cp_idx")));
			l.setAttribute("x2", axes.xScale(l.getAttribute("cp_idx")));
		});
	}

	var svg = d3.select(selector).append('svg')
		.attr("width", lineWidth)
		.attr("height", height);

	svg.append("defs")
		.append("clipPath")
		.attr("id", "clip")
		.append("rect")
		.attr("width", width)
		.attr("height", height)
		.attr("transform", "translate(0, 0)");

	var bigWrapper = svg.append("g")
		.attr("class", "bigWrapper")
		.attr('transform', 'translate(' + visPadding.left + ',' + visPadding.top + ')');

	var ytrans = numCharts * (lineHeight + chartPadding) - chartPadding / 2;

	// x axis
	bigWrapper.append("g")
		.attr("class", "x-axis")
		.attr("transform", "translate(0, " + ytrans + ")")
		.call(axes.xAxis);

	// x axis label
	bigWrapper.append("text")
		.attr("text-anchor", "middle")
		.attr("class", "axis-label")
		.attr("transform", "translate(" + (width - 20) + "," + 
			(ytrans + 40) + ")")
		.text("Time");

	// wrapper for zoom
	var gZoom = bigWrapper.append("g").call(zoomObj);

	// rectangle for the graph area
	gZoom.append("rect")
		.attr("width", width)
		.attr("height", height);

	// wrapper for charts
	var chartWrap = gZoom.append('g')
		.attr('class', 'chart-wrap');

	for (j=0; j<numCharts; j++) {
		var lbl = "Y" + j;

		// wrapper for the line, includes translation.
		var lineWrap = chartWrap.append('g')
			.attr('class', 'line-wrap')
			.attr('transform', 'translate(0,' + axes.charts(lbl) + ")");

		// line for the minimum
		var minLine = lineWrap.append('g')
			.attr('class', 'z-line');
		var minVal = d3.min(labelData[j], function(d) { return d.Y; });
		minLine.append('line')
			.attr('x1', 0)
			.attr('x2', lineWidth - visPadding.middle)
			.attr('y1', axes['yScale' + j](minVal))
			.attr('y2', axes['yScale' + j](minVal));

		// create the line object
		var lineobj = d3.line()
			.x(function(d) { return axes.xScale(d.X); })
			.y(function(d) { return axes['yScale'+j](d.Y); });

		lineObjects[j] = lineobj;

		var line = lineWrap.append('path')
			.datum(labelData[j])
			.attr('class', 'line')
			.attr('id', 'line-'+j)
			.attr('d', lineobj);

		// add the points
		pointSets[j] = lineWrap.selectAll('circle')
			.data(labelData[j])
			.enter()
			.append('circle')
			.attr('cx', function(d) { return axes.xScale(d.X); })
			.attr('cy', function(d) { return axes['yScale'+j](d.Y); })
			.attr('data_X', function(d) { return d.X; })
			.attr('data_Y', function(d) { return d.Y; })
			.attr('r', 5)
			.attr('id', function(d) { return 'circle-x' + d.X + '-y' + j; })
			.on('click', function(d, i) {
				d.element = this;
				return clickFunction(d, i, numCharts);
			});

		// handle the annotations
		// annotations is a dict with keys j = 0..numCharts-1.
		if (annotations === null)
			continue;
		annotations.forEach(function(a) {
			for (i=0; i<pointSets[j]._groups[0].length; i++) {
				p = pointSets[j]._groups[0][i];
				if (p.getAttribute("data_X") != a.index)
					continue;
				var elem = d3.select(p);
				annotationFunction(a, elem, lineWrap, axes, j);
			}
		});
	}
}

function annotateChart(selector, data) {
	handleClick = function(d, i, numCharts) {
		if (d3.event.defaultPrevented) return;

		var X = d.element.getAttribute('data_X');
		for (j=0; j<numCharts; j++) {
			var id = '#circle-x' + X + '-y' + j;
			var elem = d3.select(id);

			if (elem.classed("changepoint")) {
				elem.style("fill", null);
				elem.classed("changepoint", false);
			} else {
				elem.style("fill", "red");
				elem.classed("changepoint", true);
			}
		}

		updateTableMulti(numCharts);
	}
	baseChart(selector, data, handleClick, null, null);
}

function viewAnnotations(selector, data, annotations) {
	function handleAnnotation(ann, elem, view, axes, j) {
		elem.classed("marked", true);
		ymin = axes['yScale' + j].domain()[0];
		ymax = axes['yScale' + j].domain()[1];
		view.append("line")
			.attr("cp_idx", ann.index)
			.attr("y1", axes['yScale' + j](ymax))
			.attr("y2", axes['yScale' + j](ymin))
			.attr("x1", axes["xScale"](ann.index))
			.attr("x2", axes["xScale"](ann.index))
			.attr("class", "ann-line");
	}

	baseChart(selector, data, function() {}, annotations, handleAnnotation);
}

function adminViewAnnotations(selector, data, annotations) {
	function handleAnnotation(ann, elem, view, axes, j) {
		elem.classed("marked", true);
		ymin = axes['yScale' + j].domain()[0];
		ymax = axes['yScale' + j].domain()[1];
		view.append("line")
			.attr("cp_idx", ann.index)
			.attr("y1", axes['yScale' + j](ymax))
			.attr("y2", axes['yScale' + j](ymin))
			.attr("x1", axes["xScale"](ann.index))
			.attr("x2", axes["xScale"](ann.index))
			.attr("class", "ann-line" + " " + ann.user);
	}
	baseChart(selector, data, function() {}, annotations, handleAnnotation);
}
