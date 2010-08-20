/*
*/

var results;
var infowindow;

function markerInfo(i, pos, admin) {
//	alert('hello');
//	alert(i);
	var vout = results[i].vout;
	var vin = results[i].vin;
	var vtext = "недоступно";

	if((vout!=null) && (vin!=null)){
		if(vout > 6.0){
			vtext = "внешнее (" + vout + "V)";
		} else {
			vtext = "внутреннее (" + vin + "V)";
		}
	}

	if (infowindow) infowindow.close();
	infowindow = new google.maps.InfoWindow({content:
		'<div style="background-color: #F0E8F8; font-weight: bold;">' + results[i].date + "</div>" +
		'Скорость: <b>' + results[i].speed.toFixed(1) + " км/ч" +
		/*'</b><br />Направление: <b>' + results[i].course.toFixed(0) + "°" +*/
		'</b><br />Долгота: <b>' + results[i].lat.toFixed(5) +
		'</b><br />Широта: <b>' + results[i].long.toFixed(5) +
		'</b><br />Спутники: <b>' + results[i].sats +
		'</b><br />Питание: <b>' + vtext +
		/*'</b><br />Датчик 1: <b>' + results[i].in1.toFixed(3) +
		'</b><br />Датчик 2: <b>' + results[i].in2.toFixed(3) +*/
		(admin?('</b><br /><a class="smallButton" href="javascript:DeletePoint('+i+');" title="Удалить точку">X</a>'):''),
		position: pos
	});
//	infowindow.open(map, map.getMarker(i));
	infowindow.open(map);
}

/*

function createMarker(i, pos, admin) {
//function createMarker(i, date, name, pos, stop) {
	var marker;
//	if(stop){
	if(results[i].speed < 1.0){
		marker = new google.maps.Marker({position: pos, map: map, icon: image3, shape: shape2, index:i});
//		marker = new google.maps.Marker({position: pos, map: map, icon: "", shape: shape2, index:i});
	} else {
		marker = new google.maps.Marker({position: pos, map: map, icon: image2, shape: shape2, index:i});
//		marker = new google.maps.Marker({position: pos, map: map, icon: "", shape: shape2, index:i});
	}

//	google.maps.event.addListener(marker, "mouseover", function() {
//		//marker.icon
//	});

	google.maps.event.addListener(marker, "click", function() {markerInfo(i, pos);});
	google.maps.event.addListener(marker, "mouseover", function() {
		marker.setIcon(image4);
		marker.setShape(shape3);
	});
	google.maps.event.addListener(marker, "mouseout", function() {
		if(results[i].speed < 1.0){
			marker.setIcon(image3);
		} else {
			marker.setIcon(image2);
		}
		marker.setShape(shape2);
	});

	marker.setTitle(results[i].date);
//	marker.angle = results[i].course;

	return marker;
}

*/
google.maps.Map.prototype.markers = new Array();
    
google.maps.Map.prototype.addMarker = function(i, pos, admin) {
//	var isarrow;
//	if(i%8 == 0) isarrow = new MyArrow(ismarker.getPosition(), results[i].course, map);

	var ismarker = new MyMarker(pos, results[i].course, map, i, results[i], function() {markerInfo(i, pos, admin);});
	ismarker.setTitle(results[i].date);
//	google.maps.event.addListener(ismarker, "mouseover", function() {markerInfo(i);});
//	google.maps.event.addDomListener(ismarker, "click", function() {markerInfo(i);});


//	this.markers[this.markers.length] = {marker: ismarker, arrow: isarrow, index: i};
	this.markers[this.markers.length] = {marker: ismarker, index: i};
};
    
google.maps.Map.prototype.getMarkers = function() {
	return this.markers;
};

google.maps.Map.prototype.getMarker = function(i) {
	return this.markers[i].marker;
};

google.maps.Map.prototype.showMarker = function(i) {
	var marker = this.markers[i].marker;
	marker.setVisible(true);
};

google.maps.Map.prototype.hideMarker = function(i) {
	var marker = this.markers[i].marker;
	marker.setVisible(false);
};

//google.maps.Map.prototype.getArrow = function(i) {
//	return this.markers[i].arrow;
//};

google.maps.Map.prototype.delMarker = function(i) {
	if(infowindow) 	infowindow.close();
	this.markers[i].marker.setMap(null);
//	if(this.markers[i].arrow) this.markers[i].arrow.setMap(null);
	//this.arrows[i].setMap(null);
	for(var i=i; i<this.markers.length; i++){
		this.markers[i].index--;
//		this.arrows[i].index--;
	}
	//this.markers.slice(i, 1);
};

google.maps.Map.prototype.clearMarkers = function() {
	if(infowindow) infowindow.close();
    
	for(var i=0; i<this.markers.length; i++){
//		this.markers[i].setMap(null);
		this.markers[i].marker.setMap(null);
//		if(this.markers[i].arrow) this.markers[i].arrow.setMap(null);
//		this.arrows[i].setMap(null);
	}
	this.markers = [];
};

if(0){

var MyArrow_globalindex = 0;

function MyArrow(point, angle, map)
{
        this.point = point;
        this.angle = angle;
        this.map = map;
        this.div = null;
	this.index = MyArrow_globalindex;
	MyArrow_globalindex = MyArrow_globalindex + 1;

        // Optional parameters
	this.setMap(map);
}

MyArrow.prototype = new google.maps.OverlayView();

function ArrowMouseOver(i) {
//	alert("in: " + index);
//	map.showMarker(i);
//	alert(map.getMarker(i).getIcon());// = new google.maps.Size(320, 320);
}

function ArrowMouseOut(i) {
//	alert("out: " + index);
//	map.hideMarker(i);
}

MyArrow.prototype.onAdd = function() {

  // Note: an overlay's receipt of onAdd() indicates that
  // the map's panes are now available for attaching
  // the overlay to the map via the DOM.

  // Create the DIV and set some basic attributes.
  var div = document.createElement('div');
//  div.setAttribute("style", "border: solid 1px; -webkit-border-radius: 0px; -webkit-transform: rotate(30deg);width:16px;height:16px;");
  div.setAttribute("class", "arrowdiv");
  div.setAttribute("style", "-webkit-transform: rotate(" + this.angle + "deg); width: 16px; height: 16px;");
//  div.style.width = '16px';
//  div.style.height = '16px';
//  div.setAttribute("onMouseOver", "javascript:ArrowMouseOver(" + this.index +");");
//  div.setAttribute("onMouseOut", "javascript:ArrowMouseOut(" + this.index + ");");
  div.setAttribute("title", "Бла-бла-бла");


//  div.style.transform = "rotate(30deg)";
//  div.class = "arrowdiv";
//  div.style.border = "solid";
//  div.style.borderWidth = "1px";
//  div.style.position = "absolute";

  // Create an IMG element and attach it to the DIV.
/*  var canvas = document.createElement("canvas");
  canvas.id = this.classname;
  canvas.style.width = "16px";
  canvas.style.height = "16px";
  div.appendChild(canvas);*/

//  div.innerHTML = '<object style="-webkit-transform: rotate(30deg);width:16px;height:16px;" data="svg/arrow.svg" type="image/svg+xml" codebase="http://www.adobe.com/svg/viewer/install/"></object>';
//  div.innerHTML = '<object style="width:16px;height:16px;" data="svg/arrow.svg" type="image/svg+xml" codebase="http://www.adobe.com/svg/viewer/install/"></object>';
//  div.innerHTML = '<iframe style="width:16px;height:16px;" src="svg/arrow.svg" type="image/svg+xml" codebase="http://www.adobe.com/svg/viewer/install/"></irame>';

/*  var object = document.createElement("object");
  svg.setAttribute("style", "-webkit-transform: rotate(30deg);width:16px;height:16px;");
  svg.setAttribute("data", "svg/arrow.svg");
  svg.setAttribute("type", "image/svg+xml");
  svg.setAttribute("codebase", "http://www.adobe.com/svg/viewer/install/");
  div.appendChild(object);
*/

/*
  var svg = document.createElement("svg");

  //Set some attributes on the root node that are
  // required for proper rendering.
  svg.setAttribute("width","16px");
  svg.setAttribute("height","16px");
  svg.setAttribute("version","1.1");
  svg.setAttribute("xmlns","http://www.w3.org/2000/svg");
  div.appendChild(svg);

  var gNode = document.createElement("g");
//  gNode.setAttribute("transform","translate(0,0)");
  svg.appendChild(gNode);

  var path = document.createElement("path");
  path.setAttribute("style", "fill:none;stroke:#000000;stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1");
  path.setAttribute("d","M 8,15 8,1");
  gNode.appendChild(path);

  var path = document.createElement("path");
  path.setAttribute("style", "fill:none;stroke:#000000;stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1");
  path.setAttribute("d","M 3,7 8,1 13,7");
  gNode.appendChild(path);

  //var drw = canvas.getContext('2d');
  //drw.save();                   // save the canvas state
  //canvas.rotate(angle);            // rotate the canvas
  //canvas.translate(16*sina+16*cosa,16*cosa-16*sina); // translate the canvas 16,16 in the rotated axes
  //canvas.drawImage(img,-16,-16);   // plot the car
  //drw.fillRect(0,0,16,16);
  //drw.restore();                // restore the canvas state, to undo the rotate and translate		
*/
  // Set the overlay's div_ property to this DIV
  this.div = div;

  // We add an overlay to a map via one of the map's panes.
  // We'll add this overlay to the overlayImage pane.
  var panes = this.getPanes();
  panes.overlayLayer.appendChild(div);
//  panes.overlayMouseTarget.appendChild(div);
//  panes.floatPane.appendChild(div);

}

MyArrow.prototype.onRemove = function() {
  this.div.parentNode.removeChild(this.div);
  this.div = null;
}

MyArrow.prototype.draw = function() {

  // Size and position the overlay. We use a southwest and northeast
  // position of the overlay to peg it to the correct position and size.
  // We need to retrieve the projection from this overlay to do this.
  var overlayProjection = this.getProjection();

  // Retrieve the southwest and northeast coordinates of this overlay
  // in latlngs and convert them to pixels coordinates.
  // We'll use these coordinates to resize the DIV.
  var divpx = overlayProjection.fromLatLngToDivPixel(this.point);
//  var lng = overlayProjection.fromLatLngToDivPixel(this.point.lng());

  // Resize the image's DIV to fit the indicated dimensions.
  var div = this.div;
  div.style.left = divpx.x - 8 + 'px';
  div.style.top = divpx.y - 8 + 'px';
//  div.style.width = '16px';
//  div.style.height = '16px';
//  div.className = 'smalldot';

  //var drw = this.canvas.getContext('2d');
  //canvas = document.getElementById("mapcanvas").getContext('2d');
}

}
