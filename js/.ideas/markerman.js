var MarkerManager = function(map){
	/*
	 * @author CTAPbIu_MABP
	 * @email CTAPbIuMABP@gmail.com
	 * @link http://mabp.kiev.ua/2010/03/01/google-map-api-v3-marker-manager/
	 * @license MIT, BSD, and GPL
	 */
	this.setMap(map);
}
MarkerManager.prototype = {


	markers : [],
	map : null,


	/**
	 * Set the map
	 * @access private
	 * @param {HTMLElement} map Div with map
	 */
	setMap : function(map){
		this.map = map;
	},


	/**
	 * Add new marker to the map
	 * @access public
	 * @param {google.maps.Marker} marker Marker to add
	 */
	addMarker : function(marker){
			this.markers.push(marker);
	},


	/**
	 * Add new markers to the map
	 * @access public
	 * @param {Array of google.maps.Marker} markers Array of markers to add
	 */
	addMarkers : function(markers){
			this.markers.concat(markers);
	},


	/**
	 * Get markers with latitude & longitude
	 * @access public
	 * @param {google.maps.LatLng} latlng Coordinates
	 * @return {Array of google.maps.Marker} Array of markers
	 */
	getMarkers : function(latlng){
		var array = [];
		for (var i in this.markers)
			if (this.markers[i].getPosition().equals(latlng))
				array.push(this.markers[i]);
		return array;
	},


	/**
	 * Remove marker
	 * @access public
	 * @param {google.maps.Marker} marker Marker to remove
	 * @return {google.maps.Marker} Removed marker
	 */
	removeMarker : function(marker){
		var index = this.inArray(marker, this.markers), current;
		if (index > -1){
			current = this.markers.splice(index,1);
			current[0].setMap(null);
		}
		return marker;
	},


	/**
	 * Remove all marker
	 * @access public
	 */
	clearMarkers : function(){
		// this.map.clearOverlays();
		for (var i in this.markers)
			this.markers[i].setMap(null);
		this.markers = [];
	},


	/**
	 * @access public
	 * @return {int} Count of markers on the map
	 */
	getMarkerCount : function(){
		return this.markers.length;
	},


	/**
	 * @access public
	 * @return {Array of google.maps.Marker} Return Array of visible markers
	 */
	getVisibleMarkers : function(){
		var array = [];
		for (var i in this.markers){
			if (this.isVisible(this.markers[i].getPosition()))
				array.push(this.markers[i]);
		}
		return array;
	},




	/**
	 * For more information about getBounds look at google groups discussion
	 * http://groups.google.com/group/google-maps-js-api-v3/browse_thread/thread/563ed63c2bd60749/2fd92dd62b833afd#anchor_d22c495c46a39f74
	 * @access public
	 * @param {google.maps.LatLng} latlng Coordinates of point
	 * @return {boolean} is point visible
	 */
	isVisible : function(latlng){
		this.map.getBounds.contains(latlng);
	},


	/**
	 * Search for item in array
	 * @access public
	 * @param {mixed} elem needle
	 * @param {array} array haystack
	 * @return {int} Index of item
	 */
	inArray : function(elem, array) {
		if (array.indexOf) {
			return array.indexOf(elem);
		}


		for (var i=0, length=array.length; i<length; i++){
			if (array[i]===elem) {
				return i;
			}
		}


		return -1;
	},


	/**
	 * Create a new marker and add it to map
	 * Not the best implementation
	 * It seems you should write your own
	 * @access public
	 * @param {google.maps.LatLng} position Coordinates
	 * @param {string} color Marker color [red,black,grey,orange,white,yellow,purple,green]
	 * @param {boolean} draggable Is marker draggable
	 * @return {google.maps.Marker} created marker
	 */
	createMarker : function(position, color, draggable){
		var marker = new google.maps.Marker({
			map: this.map,
			position : position,
			draggable : !!draggable,
			icon : new google.maps.MarkerImage('http://maps.google.com/mapfiles/marker'+(color=="red"||!color?"":"_"+color)+'.png',
				new google.maps.Size(32, 32),
				new google.maps.Point(0,0),
				new google.maps.Point(8, 32)),
			shadow : new google.maps.MarkerImage('http://maps.google.com/mapfiles/shadow50.png',
				new google.maps.Size(59, 32),
				new google.maps.Point(0,0),
				new google.maps.Point(10, 32)),
			shape : {
				coord: [9,0,6,1,4,2,2,4,0,8,0,12,1,14,2,16,5,19,7,23,8,26,9,30,9,34,11,34,11,30,12,26,13,24,14,21,16,18,18,16,20,12,20,8,18,4,16,2,15,1,13,0],
				type: 'poly'
			}
		});
		this.addMarker(marker);
		return marker;
	}
}
