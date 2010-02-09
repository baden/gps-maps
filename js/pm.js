var trackInfos = [];
var deviceInfos = [];

var activeMarker;
var activeMarkerLabel;

var markers = [];
var transparentMarkers = [];
var markerLabels = [];
var markerInfos = [];

var points_ = [];
var timeFrom = null;
var timeTo = null;
var selectedDeviceId;

var WEB_GIS_MAP = "WebGIS";
var YANDEX_MAP = "Yandex";
var OPEN_STREET_MAP = "OpenStreet";

var markerManager;


function createMiniMap(canvas, center, zoom) {
    try {
        if (GBrowserIsCompatible()) {
            div = document.getElementById(canvas);

            var miniMap = new GMap2(div);
            miniMap.addControl(new GSmallZoomControl());
            miniMap.removeMapType(G_HYBRID_MAP);
            //miniMap.addControl(new GMapTypeControl());
            miniMap.setMapType(map.getCurrentMapType());
            miniMap.setCenter(new GLatLng(center.lat(), center.lng()), zoom);
            var CopyrightDiv = div.firstChild.nextSibling;
            var CopyrightImg = div.firstChild.nextSibling.nextSibling;
            CopyrightDiv.style.display = "none";
            CopyrightImg.style.display = "none";

            for (i = 0; i < devices.length; i++) {
                if (devices[i].position) {
                    miniMap.addOverlay(createGMarker(devices[i]));
                }
            }

            return miniMap;
        }
    } catch (e) {
        alert(e);
    }
    return null;
}

function hideTrack() {
    for (var i = 0; i < trackInfos.length; i++) {
        if (trackInfos[i])
            trackInfos[i].hide(map);
    }
}


function showMessages(deviceId) {

    $("#viewMessagesLink").html('<a href="" title="Свернуть историю" ' +
                                'onclick="hideMessages(' + deviceId + ');return false"><img ' +
                                'src="/img/minus.png" alt="" class="ico" /></a>');

    var deviceInfo = deviceInfos[deviceId];

    if (!deviceInfo) {
        deviceInfo = new DeviceInfo(deviceId);
        deviceInfo.initialize(function () {
            deviceInfos[deviceId] = deviceInfo;
            displayMessagesDiv(deviceId);
        });
    } else {
        displayMessagesDiv(deviceId);
    }


    hideDeviceMarkers(true);
}



function hideMessages(deviceId) {

    
        $("#viewMessagesLink").html('<a href="" title="Развернуть историю сообщений" '+
                            'onclick="showMessages('+deviceId+');return false"><img '+
                            'src="/img/plus.png" alt="" class="ico" /></a>');
        
        if(animationDisabled){
            $("#messagesRow" + deviceId).hide();
            $('#messagesRow' + deviceId).html("");
        }else {
            $("#messagesRow" + deviceId).hide("blind", {}, 1000,
                function() {
                    $('#messagesRow' + deviceId).html("");
                });
        }

}

function displayMessagesDiv(deviceId) {
    $('#messagesRow' + deviceId).html(deviceInfos[deviceId].getMessagesDiv());

    if (animationDisabled) {
        $("#messagesRow" + deviceId).show();
        document.getElementById('devicesList').scrollTop = document.getElementById("deviceRow" + deviceId).offsetTop - 33;
    } else {
        $("#messagesRow" + deviceId).show("blind", {}, 1000, function () {
            $("#devicesList").animate({scrollTop:document.getElementById("deviceRow" + deviceId).offsetTop - 33});
        });
    }


}

function selectTrack(deviceId, update) {

    hideTrack();
    hideDeviceMarkers(true);

    if (update && trackInfos[deviceId]) {
        trackInfos[deviceId].clear();
        trackInfos[deviceId] = null;
    }

    var trackInfo = trackInfos[deviceId];

    if (trackInfo) {
        trackInfo.show(map);
    } else {
        loadTrackInfo(deviceId, function(data) {
            trackInfos[deviceId] = new TrackInfo(data);
            trackInfos[deviceId].show(map);
        });
    }
}

function loadTrackInfo(deviceId, callback) {
    $.getJSON(GET_TRACK_URL + "?json&device=" + deviceId + (timeFrom ? "&timeFrom=" + timeFrom + "&timeTo=" + timeTo : ""), null,
            function(data) {
                callback(data);
            });
}


function initMap(canvas, mapType, zoom) {
    try {
        if (GBrowserIsCompatible()) {
            var map = new GMap2(document.getElementById(canvas));

            map.enableContinuousZoom();
            map.enableScrollWheelZoom();
            map.enableDoubleClickZoom();
            //  map.addControl(new GMapTypeControl());
            map.addControl(new GLargeMapControl());

            map.removeMapType(G_HYBRID_MAP);
            try {
                map.addMapType(getWebGISMapType(WEB_GIS_MAP));
            } catch(e1) {
                //
            }

            try {
                map.addMapType(getYandexMapType(YANDEX_MAP));
            } catch(e2) {
                //
            }

            try {
                map.addMapType(getOSMType(OPEN_STREET_MAP));
            } catch(e2) {
                //
            }

            if (mapType) {
                if (getMapTypeByName(map, mapType) != null) {
                    map.setMapType(getMapTypeByName(map, mapType));
                }
            }

            map.setCenter(new GLatLng(mapCenter.lat(), mapCenter.lng()), zoom ? zoom : 10);

            try {
                GEvent.addListener(map, "moveend", function() {
                    mapCenter = new LatLng(map.getCenter().lat(), map.getCenter().lng());
                    $.get(UPDATE_MAP_URL + "?device=" + selectedDeviceId + "&lat=" + map.getCenter().lat() + "&lng=" + map.getCenter().lng() +
                          "&zoom=" + map.getZoom());
                    if (map.getBounds().containsBounds(getBounds())) {
                        fitControl.disable();
                    } else {
                        fitControl.enable();
                    }
                });

                GEvent.addListener(map, "maptypechanged", function() {
                    $.get(UPDATE_MAP_URL + "?map=" + getMapProviderName());
                });

                GEvent.addListener(map, "maptypechanged", function() {
                    //                miniMap.setMapType(map.getCurrentMapType());
                    $.get(UPDATE_MAP_URL + "?map=" + getMapProviderName());
                });

                GEvent.addListener(map, "infowindowopen", function() {
                    map.panTo(map.getInfoWindow().getPoint());
                    //miniMap = createMiniMap("miniMap", map.getInfoWindow().getPoint(), 16);
                });

                markerManager = new MarkerManager(map);
            } catch(e) {

            }
            return map;

        }
    } catch (e) {
        alert(e);
    }
    return null;
}


function getMapTypeByName(map, name) {
    types = map.getMapTypes();
    for (i = 0; i < types.length; i++) {
        if (types[i].getName() == name) {
            return types[i];
        }
    }
    return null;
}

function getMapProviderName() {
    if (map.getCurrentMapType().getName() == YANDEX_MAP) {
        return "yandex";
    }

    if (map.getCurrentMapType().getName() == OPEN_STREET_MAP) {
        return "osm";
    }
    
    if (map.getCurrentMapType().getName() == WEB_GIS_MAP) {
        return "webgis";
    }
    return "google";
}

function initMarkers(devices) {
    map.clearOverlays();
    trackInfos = [];
    markerInfos = [];
    points_ = [];

    for (i = 0; i < devices.length; i++) {
        if (devices[i].position) {
            var marker = createGMarker(devices[i]);
            var tmarker = createGMarker(devices[i], true);
            markerLabel = new LabeledMarker(new GLatLng(devices[i].position.latitude, devices[i].position.longitude), devices[i].name, true);
            markers[devices[i].id] = marker;
            transparentMarkers[devices[i].id] = tmarker;
            markerLabels[devices[i].id] = markerLabel;
            map.addOverlay(tmarker);
            map.addOverlay(marker);
            map.addOverlay(markerLabel);
            points_.push(new GLatLng(devices[i].position.latitude, devices[i].position.longitude));
        }
    }

}


function updateActiveMarker(name, latlng) {
    if (activeMarker && activeMarkerLabel) {
        activeMarker.setLatLng(latlng);
        activeMarkerLabel.setLatLng(latlng);
        if (name) {
            activeMarkerLabel.setText(name);
        }
        activeMarkerLabel.bounce(activeMarkerLabel.getDiv());
    } else {
        activeMarkerLabel = new LabeledMarker(latlng, name, true);
        map.addOverlay(activeMarkerLabel);
        var icon = new GIcon();
        icon.image = "/img/marker/blue-dot.png";
        icon.shadow = "/img/marker/msmarker.shadow.png";
        icon.iconSize = new GSize(32, 32);
        icon.shadowSize = new GSize(59, 32);
        icon.iconAnchor = new GPoint(16, 32);
        activeMarker = new GMarker(latlng, {icon:icon});
        map.addOverlay(activeMarker);
        activeMarkerLabel.bounce(activeMarkerLabel.getDiv());
    }
}

function getMarker(deviceId) {
    return markers[deviceId];
}


function showMessage(id, lat, lng) {
    deviceInfos[selectedDeviceId].selectMessage(id);

    if (lat > 0 && lng > 0) {
        if (animationDisabled) {
            map.setCenter(new GLatLng(lat, lng));
        } else {
            map.panTo(new GLatLng(lat, lng));
        }
        updateActiveMarker(null, new GLatLng(lat, lng));
    }

}

var showMessagesAfterLoad= false;

function selectDevice(deviceId) {

    selectedDeviceId = deviceId;
    hideDeviceMarkers();
    updateDeviceList();
    hideTrack();

    var marker = getMarker(deviceId);
    if (marker) {
        var latlng = marker.getLatLng();
        updateActiveMarker(markerLabels[deviceId].getText(), latlng);

        if (animationDisabled) {
            map.setCenter(latlng);
        } else {
            map.panTo(latlng);
        }
    }

    $("#timePanel").load(GET_TIME_LINE_URL + "?deviceId=" + selectedDeviceId,
            function() {
                showTimePanel();
            });


}

var timePanelEnabled;
function showTimePanel() {
    if (!timePanelEnabled) {
        timePanelEnabled = true;
        if(animationDisabled){
            document.getElementById('timePanel').style.width=map.getContainer().offsetWidth - 7;            
        }else {
            $("#timePanel").animate({width:map.getContainer().offsetWidth - 7});
        }

    }
}


function showMarkerInfo(deviceId, callback) {
    if (markerInfos[deviceId]) {
        callback(markerInfos[deviceId]);

    } else {
        $.get(GET_DEVICE_URL + "?device=" + deviceId + "&html", function(data) {
            var div = document.createElement("div");
            div.innerHTML = data;
            markerInfos[deviceId] = div;
            callback(div);
        });

    }
}

function getBounds() {
    p = new GPolyline(points_);
    return p.getBounds();
}

function showAllMarkers() {
    for (var i = 0; i < markers.length; i++) {
        var marker = markers[i];
        if (marker) {
            marker.show();
        }
    }

    for (i = 0; i < transparentMarkers.length; i++) {
        marker = transparentMarkers[i];
        if (marker) {
            marker.show();
        }
    }

}


function hideDeviceMarkers(full) {
    for (var i = 0; i < markers.length; i++) {
        var marker = markers[i];
        if (marker) {
            marker.hide();
        }
    }

    for (i = 0; i < markerLabels.length; i++) {
        marker = markerLabels[i];
        if (marker) {
            marker.hide();
        }
    }

    if (full)
        for (i = 0; i < transparentMarkers.length; i++) {
            marker = transparentMarkers[i];
            if (marker && selectedDeviceId != i) {
                marker.hide();
            }
        }
}

function createGMarker(device, transparent) {
    try {

        var icon = new GIcon();
        color = "blue";
        if (device.online) {
            color = "green";
        }
        if (device.requestProccess) {
            color = "orange";
        }
        if (device.longTimeNotActive) {
            color = "gray";
        }

        icon.image = "/img/marker/" + color + "-dot" + (transparent ? "-t" : "") + ".png";
        icon.shadow = "/img/marker/msmarker.shadow" + (transparent ? "-t" : "") + ".png";

        icon.iconSize = new GSize(32, 32);
        icon.shadowSize = new GSize(59, 32);

        icon.iconAnchor = new GPoint(16, 32);

        var marker = new GMarker(new GLatLng(device.position.latitude, device.position.longitude),
        {icon:icon, title:device.name});


        GEvent.addListener(marker, "click", function() {
            selectDevice(device.id);
        });

        return marker;
    } catch (e) {
        return null;
    }
}

GLatLng.prototype.distance = function(point) {
    if (point == null) return 0;
    return Math.sqrt(Math.abs((this.lng() - point.lng()) * (this.lng() - point.lng()) + (this.lat() - point.lat()) * (this.lat() - point.lat())));
}

GLatLng.prototype.toString = function() {
    return "(" + this.lat() + "," + this.lng() + ")";
}


function LatLng(lat, lng) {
    this._lat = lat;
    this._lng = lng;

    LatLng.prototype.lat = function() {
        return this._lat;
    }

    LatLng.prototype.lng = function() {
        return this._lng;
    }

    LatLng.prototype.distance = function(point) {
        if (point == null) return 0;
        return Math.sqrt((this.lng - point.lng()) * (this.lng - point.lng()) + (this.lat - point.lat()) * (this.lat - point.lat()));
    }
}


function formatDate(date, format) {
    if (date) {
        var h = date.getHours();
        var m = date.getMinutes();
        return (h >= 10 ? h : "0" + h) + ":" + (m >= 10 ? m : "0" + m);
    } else {
        return "";
    }
}
