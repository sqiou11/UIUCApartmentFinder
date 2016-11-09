import requests

cumtdAPIBase = "https://developer.cumtd.com/api/v2.2/json/"
cumtdAPIKey = "f6a8e3b691074f89b7b74a3a81379207"

def getRoutesNearLongLat(lon, lat, dist):
    method = "GetStopsByLatLon"
    nearestStops = requests.get(cumtdAPIBase + method, params={"key": cumtdAPIKey, "lat": lat, "lon": lon}).json()["stops"]
    nearestRoutes = set()

    method = "GetRoutesByStop"
    for stop in nearestStops:
        if stop["distance"] <= dist:
            routesAtThisStop = requests.get(cumtdAPIBase + method, params={"key": cumtdAPIKey, "stop_id": stop["stop_id"]}).json()["routes"]
            for route in routesAtThisStop:
                if route["route_long_name"] not in nearestRoutes:
                    nearestRoutes.add(route["route_long_name"])

    return nearestRoutes

print(getRoutesNearLongLat(-88.2390549, 40.107053, 1200))
