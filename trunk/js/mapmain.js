google.load('maps', '2');
google.load("jquery", "1.3.2");
google.load("jqueryui", "1");

function init(){
	var $map = $('#map');
	var map = new GMap2($map[0]);
	map.setCenter(new GLatLng(37.4419, -122.1419), 13);
	map.setUIToDefault();
}

function destroy(){
}

function resizeListContainer() {
        try {
            document.getElementById("devicesList").style.height =
            (document.getElementById("listContainer").offsetHeight - 35) + "px";
        } catch(e) {
        }
    }

function foo(){

	var map;
	var object1 = new google.maps.LatLng(48.408206, 35.048925);
	var points = 1;

	// Define a property to hold the Home state
	HomeControl.prototype.home_ = null;

	// Define setters and getters for this property
	HomeControl.prototype.getHome = function() {
		return this.home_;
	}

	HomeControl.prototype.setHome = function(home) {
		this.home_ = home;
	}

	function HomeControl(controlDiv, map, object) {

		var control = this;
		control.home_ = object;

		// Set CSS styles for the DIV containing the control
		// Setting padding to 5 px will offset the control
		// from the edge of the map
		controlDiv.style.padding = '5px';

		// Set CSS for the control border
		var controlUI = document.createElement('div');
		controlUI.setAttribute('class', 'MapNav');
		controlUI.title = 'Нажмите чтобы центровать на "объект №1"';
		controlDiv.appendChild(controlUI);

		// Set CSS for the control interior
		var controlText = document.createElement('div');
		controlText.setAttribute('class', 'MapNavText');
		controlText.innerHTML = 'Объект №1';
		controlUI.appendChild(controlText);

		var controlNav = document.createElement('div');
		controlNav.setAttribute('class', 'MapNav');
		controlNav.title = 'Click to set navigation';
		controlDiv.appendChild(controlNav);

		var navText = document.createElement('div');
		navText.setAttribute('class', 'MapNavText');
		navText.innerHTML = 'Слежение';
		controlNav.appendChild(navText);

		// Setup the click event listeners: simply set the map to
		// Chicago
		google.maps.event.addDomListener(controlUI, 'click', function() {
			map.setCenter(object);
		});
		google.maps.event.addDomListener(controlNav, 'click', function() {
			if(controlNav.style.backgroundColor == 'lime')
				controlNav.style.backgroundColor = 'white';
			else
				controlNav.style.backgroundColor = 'lime';
		});
	}

	var image = new google.maps.MarkerImage('stylesheets/marker1.png',
		// This marker is 20 pixels wide by 32 pixels tall.
		new google.maps.Size(32, 32),
		// The origin for this image is 0,0.
		new google.maps.Point(0,0),
		// The anchor for this image is the base of the flagpole at 0,32.
		new google.maps.Point(16, 16));
/*	var shadow = new google.maps.MarkerImage('stylesheets/beachflag_shadow.png',
		// The shadow image is larger in the horizontal dimension
		// while the position and offset are the same as for the main image.
		new google.maps.Size(37, 32),
		new google.maps.Point(0,0),
		new google.maps.Point(0, 32));
		// Shapes define the clickable region of the icon.
		// The type defines an HTML <area> element 'poly' which
		// traces out a polygon as a series of X,Y points. The final
		// coordinate closes the poly by connecting to the first
		// coordinate.
*/	var shape = {
//		coord: [1, 1, 1, 20, 18, 20, 18 , 1],
		coord: [0, 16, 0, 32, 32, 32, 32 ,16, 18, 0],
		type: 'poly'
	};

	var beaches = [
	  ['Bondi Beach', 48.408206, 35.048925, 4],
	  ['Coogee Beach', 48.409206, 35.049925, 5],
	  ['Cronulla Beach', 48.406206, 35.049925, 3],
	  ['Manly Beach', 48.407206, 35.046925, 2],
	  ['Maroubra Beach', 48.404206, 35.045925, 1]
	];

	function setMarkers(map, locations) {
		// Add markers to the map

		// Marker sizes are expressed as a Size of X,Y
		// where the origin of the image (0,0) is located
		// in the top left of the image.

		// Origins, anchor positions and coordinates of the marker
		// increase in the X direction to the right and in
		// the Y direction down.
/*		var image = new google.maps.MarkerImage('stylesheets/marker1.png',
			// This marker is 32 pixels wide by 32 pixels tall.
			new google.maps.Size(32, 32),
			// The origin for this image is 0,0.
			new google.maps.Point(0, 0),
			// The anchor for this image is the base of the flagpole at 0,32.
			new google.maps.Point(32, 32));
		var shadow = new google.maps.MarkerImage('stylesheets/beachflag_shadow.png',
			// The shadow image is larger in the horizontal dimension
			// while the position and offset are the same as for the main image.
			new google.maps.Size(37, 32),
			new google.maps.Point(0,0),
			new google.maps.Point(0, 32));
			// Shapes define the clickable region of the icon.
			// The type defines an HTML <area> element 'poly' which
			// traces out a polygon as a series of X,Y points. The final
			// coordinate closes the poly by connecting to the first
			// coordinate.
		var shape = {
			coord: [1, 1, 1, 20, 18, 20, 18 , 1],
			type: 'poly'
		};
*/
		for (var i = 0; i < locations.length; i++) {
			var beach = locations[i];
			var myLatLng = new google.maps.LatLng(beach[1], beach[2]);
			var marker = new google.maps.Marker({
				position: myLatLng,
				map: map,
//				shadow: shadow,
				icon: image,
				shape: shape,
				title: beach[0],
				zIndex: beach[3]
			});
		}
	}

	var pathCoordinates = [];
	var poly;
	var obj1x = 48.408206;
	var obj1y = 35.048925;

	google.load("jquery", "1.3.2");
	google.load("jqueryui", "1");

	function initialize() {
//		$(window).resize(function(){
//			alert("Stop it!");
//		});

		var myOptions = {
			zoom: 14,
			center: object1,
			mapTypeControl: true,
			mapTypeControlOptions: {style: google.maps.MapTypeControlStyle.DROPDOWN_MENU},
			navigationControl: true,
			navigationControlOptions: {style: google.maps.NavigationControlStyle.SMALL},
			mapTypeId: google.maps.MapTypeId.ROADMAP
		};
		map = new google.maps.Map(document.getElementById("map"), myOptions);

		var homeControlDiv = document.createElement('div');
		var homeControl = new HomeControl(homeControlDiv, map, object1);

		homeControlDiv.index = 1;
		map.controls[google.maps.ControlPosition.TOP_LEFT].push(homeControlDiv);

		setMarkers(map, beaches);

		// We create pathCoordinates as an MVCArray so we can
		// manipulate it using the insertAt() method
		pathCoordinates = new google.maps.MVCArray();

/*		var flightPlanCoordinates = [
			new google.maps.LatLng(48.408206, 35.048925),
			new google.maps.LatLng(48.409206, 35.047925),
			new google.maps.LatLng(48.410206, 35.049925),
			new google.maps.LatLng(48.411206, 35.047925),
			new google.maps.LatLng(48.412206, 35.047925),
			new google.maps.LatLng(48.413206, 35.047925),
			new google.maps.LatLng(48.414206, 35.047925),
			new google.maps.LatLng(48.415206, 35.047925),
			new google.maps.LatLng(48.416206, 35.047925),
		];
*/
		var polyOptions = {
			path: pathCoordinates,
			strokeColor: '#008000',
			strokeOpacity: 0.8,
			strokeWeight: 4
		}
		poly = new google.maps.Polyline(polyOptions);
		poly.setMap(map);

		var path = poly.getPath();
		path.insertAt(pathCoordinates.length, new google.maps.LatLng(obj1x, obj1y));

//		map.controls[google.maps.ControlPosition.TOP_RIGHT].push(homeControlDiv);
	}
		//google.load("maps", "2", {"language" : "uk"});
		//google.load("maps", "2", {"language" : "ru"});
		//google.load("search", "1");
		// Call this function when the page has been loaded
/*
		function initialize() {

			map = new google.maps.Map2(document.getElementById("map"));
//			map.setCenter(new google.maps.LatLng(37.4419, -122.1419), 13);

			var map_ctrl = new GSmallMapControl();
			var map_type_ctrl = new GMapTypeControl(); 
			var map_scale_ctrl = new GScaleControl();

			map.addControl(map_ctrl);
			map.addControl(map_type_ctrl);
			map.addControl(map_scale_ctrl);

			pntx = 48.40820667;
			pnty = 35.048925;
			var mcenter = new GLatLng(pntx, pnty);
			map.setCenter(mcenter, 14);

			map.addControl(new TextualZoomControl());

			var polyPoints = Array();
			var startX = 48.40820667;
			var startY = 35.048925;

			for(var a = 0; a<50; a++) {
				polyPoints.push(new GLatLng(startX, startY));
				startX += (Math.random()*0.002)-0.0005;
				startY += (Math.random()*0.002)-0.0005;
			}

			var line = new GPolyline(polyPoints,"#0000C0", 4, 1);
			map.addOverlay(line);


//			clockPoint = map.getCenter();
//			var mapNormalProj = G_NORMAL_MAP.getProjection();
//			var origoPixel = mapNormalProj.fromLatLngToPixel(clockPoint, map.getZoom());
//			for(var a = 0; a<10; a++) {
//				var pX = origoPixel.x + a;
//				var pY = origoPixel.y + a;
//				var npix = new GPoint(pX, pY);
//				var point = mapNormalProj.fromPixelToLatLng(origoPixel, map.getZoom());
//
//				polyPoints.push(point);
//			}
//
//			var line = new GPolyline(polyPoints,"#000000", 2, 1);
//			map.addOverlay(line);


//			marker = new GMarker(mcenter);
//			marker.setPoint(mcenter);
//			map.addOverlay(marker);

			var searchControl = new google.search.SearchControl();
			searchControl.addSearcher(new google.search.WebSearch());
			searchControl.addSearcher(new google.search.NewsSearch());
			searchControl.draw(document.getElementById("searchcontrol"));
		}
		google.setOnLoadCallback(initialize);
*/
		function periodicalApp() {
			//widget = document.getElementById('Time');
			//widget.value = "1234";
			//var map = new google.maps.Map2(document.getElementById("map"));
/*			var pntx = map.getCenter().lat() + 0.0001;
			var pnty = map.getCenter().lng();
			var zoom = map.getZoom();
			var mcenter = new GLatLng(pntx, pnty);
			map.setCenter(mcenter, zoom);
*/
			var path = poly.getPath();
			obj1x = obj1x + (Math.random()*0.001)-0.0007;
			obj1y = obj1y + (Math.random()*0.001)-0.0007;
			var pos = new google.maps.LatLng(obj1x, obj1y);
//			path.insertAt(pathCoordinates.length, pos);
			path.insertAt(path.length, pos);
			points = points + 1;
//			path.insertAt(points, pos);
			document.getElementById('points').innerHTML = path.length;

			var marker = new google.maps.Marker({
				position: pos,
				icon: image,
				shape: shape,
//				shadow: shadow,
				map: map,
			});
			marker.setTitle("#" + path.length)
			//marker.setTitle("#" + points)

		}

		function resizeApp() {
			widget = document.getElementById('Widget');

			//var width = document.documentElement.clientWidth - 200;
			var width = 0;

			if( typeof( window.innerWidth ) == 'number' ) {
				//Non-IE
				width = window.innerWidth;
				//height = window.innerHeight;
			} else if( document.documentElement && ( document.documentElement.clientWidth || document.documentElement.clientHeight ) ) {
				//IE 6+ in 'standards compliant mode'
				width = document.documentElement.clientWidth;
				//height = document.documentElement.clientHeight;
			} else if( document.body && ( document.body.clientWidth || document.body.clientHeight ) ) {
				//IE 4 compatible
				width = document.body.clientWidth;
				//height = document.body.clientHeight;
			}
			width = width - 200;
			if(width < 200) width = 200;
			widget.style.width = width + "px";
		}

		function loadApp() {
			resizeApp();
			initialize();
			setInterval(periodicalApp, 1000);

			$('#content').html('<div id="draggable-handle-div" style="width:300px;border:1px solid #999;-moz-border-radius:10px;-webkit-border-radius:10px;padding: 2px 2px 2px 2px;position:absolute;bottom:0px;left:0px;">' +
				'<div style="background-color:#999;-moz-border-radius:6px;-webkit-border-radius:6px;padding-left:10px;cursor: pointer;">Можно тягать</div>Объект №1</div>');
			$("#draggable-handle-div").draggable({"handle": "div"});

		}

		var scrollTID = null;
		function restoreScroll() {
			if( document.body && ( document.body.scrollLeft || document.body.scrollTop ) ) {
				//DOM compliant
//				scrOfY = document.body.scrollTop;
//				scrOfX = document.body.scrollLeft;
				document.body.scrollTop = 0;
			} else if( document.documentElement && ( document.documentElement.scrollLeft || document.documentElement.scrollTop ) ) {
				//IE6 standards compliant mode
//				scrOfY = document.documentElement.scrollTop;
//				scrOfX = document.documentElement.scrollLeft;
				document.documentElement.scrollTop = 0;
			}
			scrollTID = null;
		}


		function scrollApp(){
			if(scrollTID == null) scrollTID = setTimeout(restoreScroll, 1000);
//			document.documentElement.
			//alert("Scroll");
			if( document.body && ( document.body.scrollLeft || document.body.scrollTop ) ) {
				//DOM compliant
//				scrOfY = document.body.scrollTop;
//				scrOfX = document.body.scrollLeft;
				document.body.scrollTop = 0;
			} else if( document.documentElement && ( document.documentElement.scrollLeft || document.documentElement.scrollTop ) ) {
				//IE6 standards compliant mode
//				scrOfY = document.documentElement.scrollTop;
//				scrOfX = document.documentElement.scrollLeft;
				document.documentElement.scrollTop = 0;
			}
		}
		google.setOnLoadCallback(loadApp);
		//window.onresize = function() { alert("Resize"); };
		//window.onresize = function() {alert("Resize");};
		//$("body").resize(function() { alert("Resize"); });
		//$("#draggable-handle-div").draggable({"handle": "div"});
}