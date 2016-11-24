app.controller('MapController', ['$scope', '$http', function($scope, $http) {
    $scope.query = {};
    $scope.room_type_form = "";
    $scope.apartments = [];
    $scope.apartment_markers = [];
    $scope.bus_stop_markers = [];
    $scope.circles = [];
    $scope.bus_routes = {};
    $scope.seconds = 0;
    $scope.minutes = 0;

    $scope.updateTime = function() {
        var time = ($scope.query.dist_feet/5280)*(60/3);
        $scope.minutes = Math.floor(time);
        $scope.seconds = Math.round((time - $scope.minutes)*60);
    }

    $scope.updateFeet = function() {
        $scope.query.dist_feet = Math.round((parseInt($scope.minutes) + parseInt($scope.seconds)/60)*(3/60)*5280);
    }

    $scope.search = function() {
        paramString = objectToStringURL($scope.query);
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
                      radius: parseInt($scope.query.dist_feet) * 0.3048,    // convert feet to meters
                      strokeColor: '#6B98FF',
                      strokeOpacity: 0.15,
                      fillOpacity: 0.35,
                      fillColor: '#6B98FF',
                      center: {lat: apartment['latitude'], lng: apartment['longitude']}
                    });

                    circle.setVisible(false);
                    $scope.circles.push(circle);
                    $scope.apartment_markers.push(marker);
                    marker.addListener('mouseover', (function(index) {
                        return function(event) { $scope.circles[index].setVisible(true); };
                    }) (i));
                    marker.addListener('mouseout', (function(index) {
                        return function(event) { $scope.circles[index].setVisible(false); };
                    }) (i));
                }
                if(response['stops']) {
                    for (var i = 0; i < response['stops'].length; i++) {
                        var stop_point = response['stops'][i];
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
