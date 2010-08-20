/*
	Что хочется от маркера.
	Svg-представление
	По умолчанию размер не выходящий за линию трека
	При наезде курсором несколько увеличивается в размере
*/
function MyMarker(point, angle, map, i, result, onclick)
{
        this.point = point;
        this.angle = angle;
        this.map = map;
        this.div = null;
        this.arrdiv = null;
        this.onclick = onclick;
        this.i = i;
	this.title = null;
	this.result = result;
//	this.index = MyMarker_globalindex;
//	MyMarker_globalindex = MyMarker_globalindex + 1;

        // Optional parameters
	this.setMap(map);
}

MyMarker.prototype = new google.maps.OverlayView();

MyMarker.prototype.onAdd = function() {

	// Note: an overlay's receipt of onAdd() indicates that
	// the map's panes are now available for attaching the overlay to the map via the DOM.

	var div = document.createElement('div');
	div.marker = this;

	div.setAttribute("class", "mymarker");

//	if(this.result.speed < 1.0) div.setAttribute("style", "background-color: red;");
//	else div.setAttribute("style", "background-color: green;");


/*	if(this.result.speed < 1.0) div.style['background-color'] = 'red';
	else div.style['background-color'] = 'lime';
*/

	div.style['background-image'] = (this.result.speed < 1.0)?'url(images/marker-stop.png)':'url(images/marker-move.png)';


	div.setAttribute("title", this.title);

	div.addEventListener('click', this.onclick, false);


	div.addEventListener('mouseover', function(e){
		this.marker.arrdiv.style.display = "block";
		//this.marker.div.style['background-image'] = 'url(images/marker-select.png)'
		//this.marker.div.style.width = 16;
		//this.marker.div.style.height = 16;
	}, false);

	div.addEventListener('mouseout', function(e){
		if(this.marker.i % 8) this.marker.arrdiv.style.display = "none";
	}, false);

	var arrdiv = document.createElement('div');
	arrdiv.setAttribute("class", "arrowdiv");
	arrdiv.setAttribute("style", "-webkit-transform: rotate(" + this.angle + "deg);z-index:-1;");

	if(this.i % 8) arrdiv.style.display = "none";

	this.div = div;
	this.arrdiv = arrdiv;

	// We add an overlay to a map via one of the map's panes.
	// We'll add this overlay to the overlayImage pane.
	var panes = this.getPanes();
	this.panes = panes;
//	panes.overlayLayer.appendChild(div);
//  	panes.overlayLayer.appendChild(arrdiv);
	panes.overlayMouseTarget.appendChild(arrdiv);
	panes.overlayMouseTarget.appendChild(div);
//	panes.floatPane.appendChild(div);

}

MyMarker.prototype.setTitle = function(title) {
//	var div = this.div;
//	div.setAttribute("title", title);
	this.title = title;
}

MyMarker.prototype.onRemove = function() {
	this.div.parentNode.removeChild(this.div);
	this.div = null;
	if(this.arrdiv){
		this.arrdiv.parentNode.removeChild(this.arrdiv);
		this.arrdiv = null;
	}
}

MyMarker.prototype.draw = function() {

	// Size and position the overlay. We use a southwest and northeast
	// position of the overlay to peg it to the correct position and size.
	// We need to retrieve the projection from this overlay to do this.
	var overlayProjection = this.getProjection();

	// Retrieve the southwest and northeast coordinates of this overlay
	// in latlngs and convert them to pixels coordinates.
	// We'll use these coordinates to resize the DIV.
	var divpx = overlayProjection.fromLatLngToDivPixel(this.point);
	// var lng = overlayProjection.fromLatLngToDivPixel(this.point.lng());

	// Resize the image's DIV to fit the indicated dimensions.
	var div = this.div;
	div.style.left = divpx.x - 2 + 'px';
	div.style.top = divpx.y - 2 + 'px';

	if(this.arrdiv){
		var arrdiv = this.arrdiv;
		arrdiv.style.left = divpx.x - 16 + 'px';
		arrdiv.style.top = divpx.y - 16 + 'px';
	}

}