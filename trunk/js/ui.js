// ================= Fit Map control ===================

function FitControl(label) {
    this.label = label;
}

FitControl.prototype = new GControl();

FitControl.prototype.initialize = function(map) {
    var container = document.createElement("div");
    container.innerHTML = '<input id="fitControllButton" type="button" value="' + this.label + '" onclick="fitMarkers();return false;"/>';
    map.getContainer().appendChild(container);
    return container;
};


FitControl.prototype.disable = function() {
    document.getElementById("fitControllButton").disabled = true;
};

FitControl.prototype.enable = function() {
    document.getElementById("fitControllButton").disabled = false;
}


FitControl.prototype.getDefaultPosition = function() {
    return new GControlPosition(G_ANCHOR_TOP_LEFT, new GSize(80, 6));
}


function fitMarkers() {
    timePanelEnabled = false;
    if(animationDisabled){        
        $("#timePanel").css("width",0);
    }else{
        $("#timePanel").animate({width:0});
    }

    zoom = map.getBoundsZoomLevel(getBounds());
    map.setCenter(getBounds().getCenter(), zoom);
    hideTrack();
    showLabels();
    showAllMarkers();
    updateDeviceList();
}

// ================= MapTypeControl control ===================

function MapTypeControl(value) {
    this.value = value;
}

MapTypeControl.prototype = new GControl();

MapTypeControl.prototype.initialize = function(map) {
    var container = document.createElement("div");
    container.innerHTML =
    'Карта: <select id="mapTypeControl" onchange="changeMapType(this.value);return false">' +
    '<option value="Карта">Google-Карта</option>' +
    '<option value="Yandex" >Yandex-Карта</option>' +
    '<option value="WebGIS" >WebGis-Карта</option>' +
    '<option value="OpenStreet">OpenStreet-Карта</option>' +
    '<option value="Спутник">Вид со спутника</option>' +
    '</select>';

    map.getContainer().appendChild(container);
    document.getElementById('mapTypeControl').value = this.value;
    return container;
};

function changeMapType(mapType) {
    map.setMapType(getMapTypeByName(map, mapType));
}

MapTypeControl.prototype.getDefaultPosition = function() {
    return new GControlPosition(G_ANCHOR_TOP_RIGHT, new GSize(30, 6));
}


// ========================== Custom Marker ====================================


function DeviceMarker(device) {
    this.latlng = new LatLng(device.position.latitude, device.position.longitude);
    this.device = device;
    this.hidden = false;
}


DeviceMarker.prototype.initialize = function(map) {
    div = createDeviceMarkerDiv(this.device);
    map.getPane(G_MAP_FLOAT_SHADOW_PANE).appendChild(div);
    this.map_ = map;
    this.div_ = div;
}

//yandex implementation
DeviceMarker.prototype.onAddToMap = function (map, parentContainer) {
    div = createDeviceMarkerDiv(this.device);
    this.div_ = div;
    this.map_ = map;
    parentContainer.appendChild(div);
    this.onMapUpdate();
};


DeviceMarker.prototype.remove = function() {
    this.div_.parentNode.removeChild(this.div_);
}

DeviceMarker.prototype.onRemoveFromMap = function () {
    this.remove();
};

//yandex implementation
DeviceMarker.prototype.onMapUpdate = function () {
    var position = this.map_.converter.coordinatesToMapPixels(
            new YMaps.GeoPoint(this.latlng.lng(), this.latlng.lat())).moveBy(new YMaps.Point(-3, -33));

    this.div_.style.left = position.x + 'px';
    this.div_.style.top = position.y + 'px';
};

//google implementation
DeviceMarker.prototype.redraw = function() {
    var p = this.map_.fromLatLngToDivPixel(new GLatLng(this.latlng.lat(), this.latlng.lng()));
    var h = parseInt(this.div_.clientHeight);
    this.div_.style.left = (p.x) + "px";
    this.div_.style.top = (p.y - h + 2) + "px";
}

DeviceMarker.prototype.getLatLng = function() {
    return this.latlng;
}

DeviceMarker.prototype.show = function() {
    if (this.div_) {
        this.div_.style.display = "";
        this.redraw();
    }
    this.hidden = false;
}

DeviceMarker.prototype.hide = function() {
    if (this.div_) {
        this.div_.style.display = "none";
    }
    this.hidden = true;
}


function createDeviceMarkerDiv(device) {
    var div = document.createElement("div");
    div.style.position = "absolute";
    div.innerHTML = '<div style="' +
                    'font-size:85%;' +
                    'background-image:url(\'/img/marker/blue_1.png\');' +
                    'background-repeat:no-repeat;' +
                    'width:148px;height:33px;">' +
                    '   <div onclick="showInfoWindow(' + device.id + ')"' +
                    '       style="margin-top:4px;width:50px;cursor:pointer;margin-left:20px;padding-left:13px;padding-top:6px;" onclick=""><strong>' + device.name + '</strong></div>' +
                    '</div>';
    return div;
}

//===================== Labled Marker =========================





// NOTE: This code remains here for historical reasons, but it has been
// entirely superceded by the file found at:

// http://uwmike.com/maps/manhattan2/labeled_marker.js


function showLabels() {
    for (j = 0; j < markerLabels.length; j++) {
        if (markerLabels[j])
            markerLabels[j].show();
    }
}


/* Constructor for an extended Marker class */
function LabeledMarker(latlng, text, bold, color) {
    this.latlng = latlng;
    this.labelText = text;
    this.bold = bold;
    this.labelColor = color;
    this.labelClass = "markerLabel";
    this.labelOffset = new GSize(0, 0);
    GMarker.apply(this, arguments);
}


/* It's a limitation of JavaScript inheritance that we can't conveniently
 extend GMarker without having to run its constructor. In order for the
 constructor to run, it requires some dummy GLatLng. */
LabeledMarker.prototype = new GMarker(new GLatLng(0, 0));


LabeledMarker.prototype.getText = function() {
    return this.labelText;

};

LabeledMarker.prototype.setLatLng = function(latlng) {
    this.latlng = latlng;
    this.redraw(true);
};

LabeledMarker.prototype.setText = function(text) {
    this.labelText = text;
    this.div.innerHTML = "<nobr " + (this.bold ? "style=\"font-weight:bold;\"" : "") + ">" + this.labelText + "</nobr>";
};

// Creates the text div that goes over the marker.
LabeledMarker.prototype.initialize = function(map) {
    // Do the GMarker constructor first.
    //GMarker.prototype.initialize.call(this, map);

    var div = document.createElement("div");
    div.className = this.labelClass;
    div.innerHTML = "<nobr " + (this.bold ? "style=\"font-weight:bold;\"" : "") + ">" + this.labelText + "</nobr>";
    div.style.position = "absolute";
    if (this.labelColor) {
        div.style.backgroundColor = this.labelColor;
    }
    map.getPane(G_MAP_MARKER_PANE).appendChild(div);

    this.map = map;
    this.div = div;
}

LabeledMarker.prototype.show = function() {
    this.div.style.display = "";
}

LabeledMarker.prototype.hide = function() {
    this.div.style.display = "none";
}

LabeledMarker.prototype.getDiv = function() {
    return this.div;
}

LabeledMarker.prototype.bounce = function(div) {
    if (!animationDisabled) {
        $(div).animate({fontSize:22}, 400, "linear", function() {
            $(div).animate({fontSize:12});
        });
    }

}
// Redraw the rectangle based on the current projection and zoom level
LabeledMarker.prototype.redraw = function(force) {

    // We only need to do anything if the coordinate system has changed
    if (!force) return;

    // Calculate the DIV coordinates of two opposite corners of our bounds to
    // get the size and position of our rectangle
    var p = this.map.fromLatLngToDivPixel(this.latlng);
    var z = GOverlay.getZIndex(this.latlng.lat());

    // Now position our DIV based on the DIV coordinates of our bounds
    this.div.style.left = (p.x + this.labelOffset.width) + "px";
    this.div.style.top = (p.y + this.labelOffset.height) + "px";
    this.div.style.zIndex = z + 1; // in front of the marker
}

// Remove the main DIV from the map pane
LabeledMarker.prototype.remove = function() {
    this.div.parentNode.removeChild(this.div);
    this.div = null;
    GMarker.prototype.remove.call(this);
}


//======================= Circle Marker ===================================


// This file adds a new circle overlay to GMaps2
// it is really a many-pointed polygon, but look smooth enough to be a circle.
var CircleMarker = function(latLng, radius, strokeColor, strokeWidth, strokeOpacity, fillColor, fillOpacity) {
    this.latLng = latLng;
    this.radius = radius;
    this.strokeColor = strokeColor;
    this.strokeWidth = strokeWidth;
    this.strokeOpacity = strokeOpacity;
    this.fillColor = fillColor;
    this.fillOpacity = fillOpacity;
}

// Implements GOverlay interface
CircleMarker.prototype = new GOverlay;

CircleMarker.prototype.initialize = function(map) {
    this.map = map;
}

CircleMarker.prototype.clear = function() {
    if (this.polygon != null && this.map != null) {
        this.map.removeOverlay(this.polygon);
    }
}

// Calculate all the points and draw them
CircleMarker.prototype.redraw = function(force) {
    var d2r = Math.PI / 180;
    circleLatLngs = new Array();
    var circleLat = this.radius * 0.014483;  // Convert statute miles into degrees latitude
    var circleLng = circleLat / Math.cos(this.latLng.lat() * d2r);
    var numPoints = 40;

    // 2PI = 360 degrees, +1 so that the end points meet
    for (var i = 0; i < numPoints + 1; i++) {
        var theta = Math.PI * (i / (numPoints / 2));
        var vertexLat = this.latLng.lat() + (circleLat * Math.sin(theta));
        var vertexLng = this.latLng.lng() + (circleLng * Math.cos(theta));
        var vertextLatLng = new GLatLng(vertexLat, vertexLng);
        circleLatLngs.push(vertextLatLng);
    }

    this.clear();
    this.polygon = new GPolygon(circleLatLngs, this.strokeColor, this.strokeWidth, this.strokeOpacity, this.fillColor, this.fillOpacity);
    this.map.addOverlay(this.polygon);
}

CircleMarker.prototype.remove = function() {
    this.clear();
}

CircleMarker.prototype.containsLatLng = function(latLng) {
    // Polygon Point in poly
    if (this.polygon.containsLatLng) {
        return this.polygon.containsLatLng(latLng);
    }
}

CircleMarker.prototype.setRadius = function(radius) {
    this.radius = radius;
}

CircleMarker.prototype.setLatLng = function(latLng) {
    this.latLng = latLng;
}


//============================= Point Marker ========================

/* Constructor for an extended Marker class */
function PointMarker(latlng, label) {
    this.latlng = latlng;
    this.labelOffset = new GSize(-2, -2);
    this.labelText = label;
    GMarker.apply(this, arguments);
}


PointMarker.prototype = new GMarker(new GLatLng(0, 0));

PointMarker.prototype.initialize = function(map) {
    var div = document.createElement("div");
    div.style.width = "6px";
    div.style.height = "6px";
    div.style.backgroundColor = "red";
    div.style.opacity = 0.7;
    div.title = this.labelText;
    div.style.position = "absolute";
    map.getPane(G_MAP_MARKER_PANE).appendChild(div);
    this.map = map;
    this.div = div;
}

PointMarker.prototype.show = function() {
    this.div.style.display = "";
}

PointMarker.prototype.hide = function() {
    this.div.style.display = "none";
}

PointMarker.prototype.redraw = function(force) {
    if (!force) return;

    var p = this.map.fromLatLngToDivPixel(this.latlng);
    var z = GOverlay.getZIndex(this.latlng.lat());
    this.div.style.left = (p.x + this.labelOffset.width) + "px";
    this.div.style.top = (p.y + this.labelOffset.height) + "px";
    this.div.style.zIndex = z + 1;
}

PointMarker.prototype.remove = function() {
    this.div.parentNode.removeChild(this.div);
    this.div = null;
    GMarker.prototype.remove.call(this);
}


//============= stop point marker ======================


function StopPointMarker(latlng, label, small) {
    this.latlng = new GLatLng(latlng.lat(), latlng.lng());
    this.label = label;
    this.small = small;
    this.offset = small ? new GSize(-4, -4) : new GSize(-7, -7);
    GMarker.apply(this, arguments);
}
;

StopPointMarker.prototype = new GMarker(new GLatLng(0, 0));

StopPointMarker.prototype.initialize = function(map) {
    var div = createStopPointMarkerDiv(this.latlng, this.label, this.small);
    map.getPane(G_MAP_MARKER_PANE).appendChild(div);
    this.map = map;
    this.div = div;
};

StopPointMarker.prototype.show = function() {
    this.div.style.display = "";
};

StopPointMarker.prototype.hide = function() {
    this.div.style.display = "none";
}

StopPointMarker.prototype.remove = function() {
    this.div.parentNode.removeChild(this.div);
    this.div = null;
    GMarker.prototype.remove.call(this);
};


StopPointMarker.prototype.redraw = function(force) {
    if (!force) return;
    var p = this.map.fromLatLngToDivPixel(this.latlng);
    var z = GOverlay.getZIndex(this.latlng.lat());
    this.div.style.left = (p.x + this.offset.width) + "px";
    this.div.style.top = (p.y + this.offset.height) + "px";
    this.div.style.zIndex = z + 2;
};


function createStopPointMarkerDiv(latlng, label, small) {
    var div = document.createElement("div");
    div.style.position = "absolute";

    if (small) {
        div.innerHTML = '<div class="stopPointMarker" title="' + label + '" style="' +
                        'font-size:8px;width:10px;height:10px;padding:0">P' +
                        '</div>';
    } else {
        div.innerHTML = '<div class="stopPointMarker" title="' + label + '" style="' +
                        'font-size:11px">P' +
                        '</div>';
    }

    return div;
}


var arrowMarkerCounter;//unique id counter for SVG arrow head markers

function ArrowMarker(latlng1, latlng2, rotation, color, opacity, tooltip) {

    this.point_ = latlng2;
    this.p1 = map.fromLatLngToDivPixel(latlng1);
    this.p2 = map.fromLatLngToDivPixel(latlng2);
    this.dx_ = this.p1.x - this.p2.x;
    this.dy_ = this.p1.y - this.p2.y;
    this.rotation_ = rotation;
    var r = rotation + 90;//compass to math
    //  this.dx_ = 5*Math.cos(r*Math.PI/180);//other end of arrow line to point
    //  this.dy_ = 5*Math.sin(r*Math.PI/180);
    this.color_ = color || "#888888";
    this.opacity_ = opacity || 0.4;
    this.tooltip_ = tooltip;

    if (arrowMarkerCounter == null)
        arrowMarkerCounter = 0;
    else
        arrowMarkerCounter += 1;
    this.svgId_ = "ArrowMarker" + arrowMarkerCounter.toString();

}
ArrowMarker.prototype = new GOverlay();

ArrowMarker.prototype.getPoint = function() {
    return this.point_;
}

ArrowMarker.prototype.getTooltip = function() {
    return this.tooltip_;
}

ArrowMarker.prototype.clicked = function() {
    GEvent.trigger(this, "click");
}

// Creates the DIV representing this arrow.
ArrowMarker.prototype.initialize = function(map) {

    var div = document.createElement("DIV");
    div.title = this.tooltip_;
    div.style.cursor = "help";

    // Arrow is similar to a marker, so add to plane just below marker pane
    map.getPane(G_MAP_MARKER_SHADOW_PANE).appendChild(div);

    //save for later
    this.map_ = map;
    this.div_ = div;

    //set up arrow invariants
    if (navigator.userAgent.indexOf("MSIE") != -1) {

        var l = document.createElement("v:line");
        l.strokeweight = "3px";
        l.strokecolor = this.color_;
        var s = document.createElement("v:stroke");
        s.opacity = this.opacity_;
        if (this.rotation_ >= 0)
            s.startarrow = "classic";// or "block", "open" etc see VML spec
        l.appendChild(s);
        this.div_.appendChild(l);
        this.vmlLine_ = l;
    }
    else {

        // make a 40x40 pixel space centered on the arrow
        var svgNS = "http://www.w3.org/2000/svg";
        var svgRoot = document.createElementNS(svgNS, "svg");
        svgRoot.setAttribute("width", 40);
        svgRoot.setAttribute("height", 40);
        svgRoot.setAttribute("stroke", this.color_);
        svgRoot.setAttribute("fill", this.color_);
        svgRoot.setAttribute("stroke-opacity", this.opacity_);
        svgRoot.setAttribute("fill-opacity", this.opacity_);
        this.div_.appendChild(svgRoot);

        var svgNode = document.createElementNS(svgNS, "line");
        svgNode.setAttribute("stroke-width", 2);
        svgNode.setAttribute("x1", 20);
        svgNode.setAttribute("y1", 20);
        svgNode.setAttribute("x2", 20 + this.dx_);
        svgNode.setAttribute("y2", 20 + this.dy_);

        //make a solid arrow head, can't share these, as in SVG1.1 they can't get color from the referencing object, only their parent
        //a bit more involved than the VML
        if (this.rotation_ >= 0) {
            var svgM = document.createElementNS(svgNS, "marker");
            svgM.id = this.svgId_;
            svgM.setAttribute("viewBox", "0 0 10 10");
            svgM.setAttribute("refX", 0);
            svgM.setAttribute("refY", 5);
            svgM.setAttribute("markerWidth", 4);
            svgM.setAttribute("markerHeight", 3);
            svgM.setAttribute("orient", "auto");
            var svgPath = document.createElementNS(svgNS, "path");//could share this with 'def' and 'use' but hardly worth it
            svgPath.setAttribute("d", "M 10 0 L 0 5 L 10 10 z");
            svgM.appendChild(svgPath);
            svgRoot.appendChild(svgM);
            svgNode.setAttribute("marker-start", "url(#" + this.svgId_ + ")");
        }

        svgRoot.appendChild(svgNode);
        this.svgRoot_ = svgRoot;

    }

    //set up click handler
    var cb = GEvent.callback(this, this.clicked);
    this.clickH_ = GEvent.addDomListener(this.div_, "click", function(event) {
        cb()
    });

}

// Remove the main DIV from the map pane
ArrowMarker.prototype.remove = function() {
    GEvent.removeListener(this.clickH_);
    this.div_.parentNode.removeChild(this.div_);
}

// Copy our data to a new ArrowMarker
ArrowMarker.prototype.copy = function() {
    return new ArrowMarker(this.point_, this.rotation_, this.color_, this.opacity_, this.tooltip_);
}

// Redraw the arrow based on the current projection and zoom level

ArrowMarker.prototype.redraw = function(force) {

    // We only need to redraw if the coordinate system has changed
    if (!force) return;

    // Calculate the DIV coordinates of the ref point of our arrow
    var p = this.map_.fromLatLngToDivPixel(this.point_);
    var x2 = p.x + this.dx_;
    var y2 = p.y + this.dy_;

    if (navigator.userAgent.indexOf("MSIE") != -1) {
        this.vmlLine_.from = p.x + "px, " + p.y + "px";
        this.vmlLine_.to = x2 + "px, " + y2 + "px";
    }
    else {
        this.svgRoot_.setAttribute("style", "position:absolute; top:" + (p.y - 20) + "px; left:" + (p.x - 20) + "px");
    }

}







