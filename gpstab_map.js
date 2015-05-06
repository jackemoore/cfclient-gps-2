var map = L.map('map').setView([33.7674, -117.5008], 16);

L.tileLayer('http://otile{s}.mqcdn.com/tiles/1.0.0/map/{z}/{x}/{y}.png', {
      maxZoom: 18,
      attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, ' +
        'tiles Courtesy of <a href="http://www.mapquest.com/" target="_blank">MapQuest</a>',
      subdomains: '1234',
}).addTo(map);

var geojsonMarkerOptions = {
    radius: 8,
    fillColor: "#ff7800",
    color: "#000",
    weight: 1,
    opacity: 1,
    fillOpacity: 0.8
};

var geojsonFeature = {
    "type": "Feature",
    "properties": {
        "name": "Point_1",
        "show_on_map": true 
    },
    "geometry": {
        "type": "Point",
        "coordinates": [map.getCenter().lng, map.getCenter().lat]
    }
};

var myLayer = L.geoJson(geojsonFeature, {
    pointToLayer: function (feature, latlng) {
        return L.circleMarker(latlng, geojsonMarkerOptions);
    } 
});

function gpsPoint(lat,lng) {
    map.removeLayer(myLayer);  
//    map.panTo([lat, lng]);
    geojsonFeature.geometry.coordinates = [lng, lat];
    myLayer = L.geoJson(geojsonFeature, {
        pointToLayer: function (feature, latlng) {
            return L.circleMarker(latlng, geojsonMarkerOptions);
        } 
    });    
    map.addLayer(myLayer); 
};

if(typeof MapviewWidget != 'undefined') {
    var onMapMove = function() { MapviewWidget.onMapMove(map.getCenter().lat, map.getCenter().lng) };
    map.on('move', onMapMove);
//    onMapMove();

}
