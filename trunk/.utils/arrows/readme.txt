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
    if (animationDisabled) {
        $("#timePanel").css("width", 0);
    } else {
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
    'Êàðòà: <select id="mapTypeControl" onchange="changeMapType(this.value);return false">' +
    '<option value="Êàðòà">Google-Êàðòà</option>' +
    '<option value="Yandex" >Yandex-Êàðòà</option>' +
    '<option value="WebGIS" >WebGis-Êàðòà</option>' +
    '<option value="OpenStreet">OpenStreet-Êàðòà</option>' +
    '<option value="Ñïóòíèê">Âèä ñî ñïóòíèêà</option>' +
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
    if (this.div) {
        this.div.innerHTML = "<nobr " + (this.bold ? "style=\"font-weight:bold;\"" : "") + ">" + this.labelText + "</nobr>";
    }
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
    if (this.div) {
        this.div.style.left = (p.x + this.labelOffset.width) + "px";
        this.div.style.top = (p.y + this.labelOffset.height) + "px";
        this.div.style.zIndex = z + 1; // in front of the marker
    }

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
function PointMarker(latlng, color, label) {
    this.latlng = latlng;
    this.color=color;
    this.labelOffset = new GSize(-7, -10);
    this.labelText = label;
    GMarker.apply(this, arguments);
}


PointMarker.prototype = new GMarker(new GLatLng(0, 0));

PointMarker.prototype.initialize = function(map) {
    var div = document.createElement("div");
    div.style.width = "10px";
    div.style.height = "10px";
    div.style.color = this.color;
//    div.style.opacity = 0.7;
    div.title = this.labelText;
    div.style.position = "absolute";
//    div.style.textAlign = "center";
    div.style.fontSize = "20px";
    div.innerHTML="<img src=\"/img/bullet_dark_blue.png\" />";
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





// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

function BDCCArrowedPolyline(points, color, weight, opacity, opts, gapPx, headLength, headColor, headWeight, headOpacity)
{
    this.gapPx = gapPx;
    this.points = points;
    this.color = color;
    this.weight = weight;
    this.opacity = opacity;
    this.headLength = headLength;
    this.headColor = headColor;
    this.headWeight = headWeight;
    this.headOpacity = headOpacity;
    this.opts = opts;
    this.heads = new Array();
    this.line = null;
}

BDCCArrowedPolyline.prototype = new GOverlay();

BDCCArrowedPolyline.prototype.initialize = function(map)
{
    this.map = map;
    this.prj = map.getCurrentMapType().getProjection();
    rdrw = GEvent.callback(this,this.recalc);
    this.lstnMoveEnd = GEvent.addListener(map,"zoomend",function(){rdrw ();});
    this.lstnType = GEvent.addListener(map,"maptypechanged",function(){rdrw ();});

    this.recalc();//first draw
}

BDCCArrowedPolyline.prototype.remove = function()
{
    try
        {
        for(var i=0; i<this.heads.length; i++)
            this.map.removeOverlay(this.heads[i]);
        if (this.line)
            this.map.removeOverlay(this.line);
    }
    catch(ex)
    {
    }
      GEvent.removeListener(this.lstnMoveEnd);
      GEvent.removeListener(this.lstnType);
}

BDCCArrowedPolyline.prototype.redraw = function(force)
{
    return;
}

BDCCArrowedPolyline.prototype.copy = function(map)
{
    return new BDCCArrowedPolyline(this.points,this.color,this.weight,this.opacity,this.opts,this.gapPx, this.headLength, this.headColor, this.headWeight, this.headOpacity);
}

BDCCArrowedPolyline.prototype.recalc = function()
{
     this.remove();

   this.lstnMoveEnd = GEvent.addListener(map,"zoomend",function(){rdrw ();});
   this.lstnType = GEvent.addListener(map,"maptypechanged",function(){rdrw ();});

   var zoom = this.map.getZoom();

   //the main polyline
   this.line = new GPolyline(this.points,this.color,this.weight,this.opacity,this.opts);
   this.map.addOverlay(this.line);

   // the arrow heads
   this.heads = new Array();

   var p1 = this.prj.fromLatLngToPixel(this.points[0],  zoom);//first point
   var p2;//next point
   var dx;
   var dy;
   var sl;//segment length
   var theta;//segment angle
   var ta;//distance along segment for placing arrows

    
   for (var i=1; i<this.points.length; i++)
     {
      p2 = this.prj.fromLatLngToPixel(this.points[i],  zoom)
      dx = p2.x-p1.x;
      dy = p2.y-p1.y;

    if (Math.abs(this.points[i-1].lng() - this.points[i].lng()) > 180.0)
        dx = -dx;

      sl = Math.sqrt((dx*dx)+(dy*dy));
      theta = Math.atan2(-dy,dx);
      j=1;

    if(this.gapPx == 0)
    {
        //just put one arrow at the end of the line
            this.addHead(p2.x,p2.y,theta,zoom);
    }
    else if(this.gapPx == 1)
    {
    //  ta = this.gapPx;
        if((this.headLength * 3) < sl && i%3 == 0) // Ð¾Ñ‚Ð¼ÐµÑ‡Ð°ÐµÐ¼ Ñ‚Ð¾Ð»ÑŒÐºÐ¾ ÐºÐ°Ð¶Ð´Ñ‹Ð¹ 3-Ð¹ Ð¾Ñ‚Ñ€ÐµÐ·Ð¾Ðº, Ð´Ð»Ð¸Ð½Ð° ÐºÐ¾Ñ‚Ð¾Ñ€Ð¾Ð³Ð¾ Ð±Ð¾Ð»ÑŒÑˆÐµ Ð´Ð»Ð¸Ð½Ñ‹ ÑÑ‚Ñ€ÐµÐ»ÐºÐ¸
        {
        //just put one arrow in the middle of the line
            var x = p1.x + ((sl/2) * Math.cos(theta));
            var y = p1.y - ((sl/2) * Math.sin(theta));
            this.addHead(x,y,theta,zoom);
        }
    }
    else
    {
        //iterate along the line segment placing arrow markers
        //don't put an arrow within gapPx of the beginning or end of the segment
          ta = this.gapPx;
        while(ta < sl)
                {
            var x = p1.x + (ta * Math.cos(theta));
            var y = p1.y - (ta * Math.sin(theta));
            this.addHead(x,y,theta,zoom);
            ta += this.gapPx;
        }

        //line too short, put one arrow in its middle
//          if(ta == this.gapPx)
//              {
//              var x = p1.x + ((sl/2) * Math.cos(theta));
//              var y = p1.y - ((sl/2) * Math.sin(theta));
//              this.addHead(x,y,theta,zoom);
//          }
    }

      p1 = p2;
   }
}

BDCCArrowedPolyline.prototype.addHead = function(x,y,theta,zoom)
{
    //add an arrow head at the specified point
    var t = theta + (Math.PI/15) ;
    if(t > Math.PI)
        t -= 2*Math.PI;
    var t2 = theta - (Math.PI/15) ;
    if(t2 <= (-Math.PI))
        t2 += 2*Math.PI;
    var pts = new Array();
    var x1 = x-Math.cos(t)*this.headLength;
    var y1 = y+Math.sin(t)*this.headLength;
    var x2 = x-Math.cos(t2)*this.headLength;
    var y2 = y+Math.sin(t2)*this.headLength;
    pts.push(this.prj.fromPixelToLatLng(new GPoint(x1,y1), zoom));
    pts.push(this.prj.fromPixelToLatLng(new GPoint(x,y), zoom));
    pts.push(this.prj.fromPixelToLatLng(new GPoint(x2,y2), zoom));
    this.heads.push(new GPolyline(pts,this.headColor,this.headWeight,this.headOpacity,this.opts));
    this.map.addOverlay(this.heads[this.heads.length-1]);
}
