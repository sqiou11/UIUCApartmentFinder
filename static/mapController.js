app.controller('MapController', ['$scope', '$http', function($scope, $http) {
    $scope.query = {};
    $scope.room_type_form = "";
    $scope.apartments = [];
    $scope.apartment_markers = [];
    $scope.bus_stop_markers = [];
    $scope.circles = [];

    $scope.search = function() {
        paramString = objectToStringURL($scope.query);
        console.log("Searching...");
        $http.get("http://localhost:5000/api/apartments?" + paramString)
            .success(function(response) {
                $scope.apartments = response['apartments'];
                console.log(response);
                $scope.removeAllMarkers();
                for (var i = 0; i < $scope.apartments.length; i++) {
                    var apartment = $scope.apartments[i];
                    var marker = new google.maps.Marker({
                        title: apartment['name'],
                        position: {lat: apartment['latitude'], lng: apartment['longitude']},
                        map: map
                    });
                    // Add circle overlay and bind to marker
                    var circle = new google.maps.Circle({
                      map: map,
                      radius: parseInt($scope.query.dist_from_stops) * 0.3048,
                      strokeColor: '#6B98FF',
                      strokeOpacity: 0.15,
                      fillOpacity: 0.15,
                      fillColor: '#6B98FF'
                    });
                    circle.bindTo('center', marker, 'position');
                    $scope.circles.push(circle);
                    $scope.apartment_markers.push(marker);
                }
                for (var i = 0; i < response['stops'].length; i++) {
                    var stop = response['stops'][i]
                    for (var j = 0; j < stop['stop_points'].length; j++) {
                        var stop_point = stop['stop_points'][j];
                        var marker = new google.maps.Marker({
                            title: stop_point['stop_name'],
                            position: {lat: stop_point['stop_lat'], lng: stop_point['stop_lon']},
                            map: map,
                            icon: "/static/images/map_markers/blue_markerB.png"
                        });
                        $scope.bus_stop_markers.push(marker);
                    }
                }
            });
    }

    $scope.removeAllMarkers = function() {
        for (var i = 0; i < $scope.apartment_markers.length; i++) {
            $scope.apartment_markers[i].setMap(null);
        }
        $scope.apartment_markers = [];
        for (var i = 0; i < $scope.bus_stop_markers.length; i++) {
            $scope.bus_stop_markers[i].setMap(null);
        }
        $scope.bus_stop_markers = [];
        for (var i = 0; i < $scope.circles.length; i++) {
            $scope.circles[i].setMap(null);
        }
        $scope.circles = [];
    }
}]);

var objectToStringURL = function(obj) {
    return Object.keys(obj).map(function(key){
        return encodeURIComponent(key) + '=' + encodeURIComponent(obj[key]);
    }).join('&');
}
