
var server_url = "http://ft1.mapsviewer.com,http://ft2.mapsviewer.com,http://ft3.mapsviewer.com,http://ft4.mapsviewer.com";


function getWebGISMapType(label, copyright, error_msg, quality, layers, map_tags, url_params)
{
	if (!quality)
		quality = "";
	if (!layers)
		layers = "";
	if (!error_msg)
		error_msg = "No map data available";
	if (!copyright)
		copyright = "";
	if (!map_tags)
		map_tags = "";
	if (!url_params)
		url_params = "";
	var arr = server_url.split(",");
	var urls = new Array;
	if (arr.length >= 2) {
		for (var i = 0; i < arr.length; i++)
			urls.push(arr[i]);
		server_url = arr[0];
	} else
		arr = new Array;
	// construct
	var cp_msg = "<a style='font-size: 8pt;font-weight: bolder; text-decoration: none;' href='http://www.gurtam.by'><font >POWERED BY:</font> <font color='black'>Gurtam WebGIS</font></a>";
	cp_msg += ", <a style='font-size: 7pt; text-decoration: none;' href='" + server_url + "/map_copyright?m=" + map_tags  + "'><font color='black'>&copy;&nbsp;map-data</font></a>"
	if (copyright != "")
		cp_msg += ", " + copyright;
	var cp1 = new GCopyright(1, new GLatLngBounds(new GLatLng(-90, -180), new GLatLng(90, 180)), 0, cp_msg);
	var cp_col = new GCopyrightCollection("");
	cp_col.addCopyright(cp1);
	var tilelayers = [new GTileLayer(cp_col, 1, 17)];
	tilelayers[0].getTileUrl = webgis_tile_url;
	// own params
	tilelayers[0].server_url = server_url;
	tilelayers[0].quality = quality;
	tilelayers[0].layers = layers;
	tilelayers[0].map_tags = map_tags;
	tilelayers[0].url_params = url_params;
	tilelayers[0].urls = arr;

	return new GMapType(tilelayers, new GMercatorProjection(20), label, {errorMessage:error_msg});
}

/**
	Get WebGIS map tile url.
	Internal function.
*/
function webgis_tile_url(pt, zoom) {
	var x = pt.x;
	var y = pt.y;
	var url = "";
	if (this.urls.length >= 2) {
		// select server
		var index = x % this.urls.length;
		url = this.urls[Math.floor(index)];
	} else
		url = this.server_url;

	url += "/map_gmaps?x=" + x + "&y=" + y + "&zoom=" + (17 - zoom) + "&v=" + this.layers + "&w=256&h=256&q=" + this.quality + "&m=" + this.map_tags;
	if (this.url_params != "")
		url += "&" + this.url_params;
	return url;
}
