
function OSMapTiles(a,b){
    return   "http://tile.openstreetmap.org/" + b + "/" + a.x + "/" + a.y + ".png";
}
                                         e
function getOSMType(label){
    var OSMapLayer = new GTileLayer(new GCopyrightCollection(''),0,17);
    OSMapLayer.getTileUrl = OSMapTiles;
    OSMapLayer.getCopyright = function(a,b) {return "OpenStreetMap: www.openstreetmap.org";};
    OSMapLayer.isPng = function() {return true;};
    var GH_OSMAP_MAP = new GMapType([OSMapLayer],
            G_SATELLITE_MAP.getProjection(), label,{errorMessage:"no maps here"});
    GH_OSMAP_MAP.getTextColor = function() {return "#0000FF";};
    return  GH_OSMAP_MAP;
}






function CustomGetTileUrl(a, b) {
    return "http://vec0" + ((a.x + a.y) % 5) + ".maps.yandex.ru/tiles?l=map&v=2.12.1&x=" + a.x + "&y=" + a.y + "&z=" + b + ".png";
}

function getYandexMapType(label) {
    var tilelayers = new Array();

    var cp1 = new GCopyright(1, new GLatLngBounds(new GLatLng(-90, -180), new GLatLng(90, 180)), 0,
            "<strong>POWERED BY</strong> <a href='http://maps.yandex.ru'>Yandex Карты</a>. © Роскартография, © ООО \"Резидент Консалтинг\", © ЗАО \"Геоцентр-Консалтинг\"");
	var cp_col = new GCopyrightCollection("");
	cp_col.addCopyright(cp1);
    
    tilelayers[0] = new GTileLayer(cp_col, 0, 22);
    tilelayers[0].getTileUrl = CustomGetTileUrl;

    var GMapTypeOptions = new Object();
    GMapTypeOptions.minResolution = 0;
    GMapTypeOptions.maxResolution = 22;
    GMapTypeOptions.errorMessage = "No map data available";


    var customProjection = new GMercatorProjection(22);
    customProjection.fromLatLngToPixel = CustomfromLatLngToPixel;
    customProjection.fromPixelToLatLng = CustomfromPixelToLatLng;

    var custommap = new GMapType(tilelayers, customProjection, label, GMapTypeOptions);
    custommap.getTextColor = function() {
        return "#000000";
    };
    return custommap;

}

function atanh(x)
{
    return 0.5 * Math.log((1 + x) / (1 - x));
}
function CustomfromLatLngToPixel(lotlan, zoom)
{
    var PixelsAtZoom = 256 * Math.pow(2, zoom);
    var exct = 0.0818197;
    var z = Math.sin(lotlan.latRadians());
    var c = (PixelsAtZoom / (2 * Math.PI));
    var x = Math.floor(PixelsAtZoom / 2 + lotlan.lng() * (PixelsAtZoom / 360));
    var y = Math.floor(PixelsAtZoom / 2 - c * (atanh(z) - exct * atanh(exct * z)));
    return new GPoint(x, y);
}
function CustomfromPixelToLatLng(pixel, zoom) {

    var PixelsAtZoom = 256 * Math.pow(2, zoom);
    var Lon = ((pixel.x) - PixelsAtZoom / 2) / (PixelsAtZoom / 360);
    var Lat = ((pixel.y) - PixelsAtZoom / 2) / -(PixelsAtZoom / (2 * Math.PI));
    Lat = Math.abs((2 * Math.atan(Math.exp(Lat)) - Math.PI / 2) * 180 / Math.PI);

    var Zu = Lat / (180 / Math.PI);
    var Zum1 = Zu + 1;
    var exct = 0.0818197;
    var yy = -Math.abs(((pixel.y) - PixelsAtZoom / 2));
    while (Math.abs(Zum1 - Zu) > 0.0000001)
    {
        Zum1 = Zu;
        Zu = Math.asin(1 - ((1 + Math.sin(Zum1)) * Math.pow(1 - exct * Math.sin(Zum1), exct))
                / (Math.exp((2 * yy) / -(PixelsAtZoom / (2 * Math.PI))) * Math.pow(1 + exct * Math.sin(Zum1), exct)));
    }
    if (pixel.y > PixelsAtZoom / 2) {
        Lat = -Zu * 180 / Math.PI
    }
    else {
        Lat = Zu * 180 / Math.PI
    }
    return new GLatLng(Lat, Lon, false);
}
