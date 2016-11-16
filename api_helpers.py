import requests

cumtdAPIBase = "https://developer.cumtd.com/api/v2.2/json/"
cumtdAPIKey = "f6a8e3b691074f89b7b74a3a81379207"

"""
Given a latitude and longitude coordinate pai for an apartment and a distance threshold,
return all bus stops at most "dist" feet away from the location
"""
def getRoutesNearLatLongWithinDist(lat, lon, dist):
    stopsWithinDist = []
    nearestStops = requests.get(cumtdAPIBase + "GetStopsByLatLon", params={"key": cumtdAPIKey, "lat": lat, "lon": lon}).json()["stops"]
    for stop in nearestStops:
        if stop["distance"] <= dist:
            stopsWithinDist.append(stop)

    return stopsWithinDist

"""
Given a list of stops and a list of preferred routes, group all the stops based on the preferred routes they serve,
or if no preferences are supplied, just group them based on routes they serve
"""
def groupStopsByPreference(stops, preferredRoutes):
    stopsWithPreferredRoutes = []
    for stop in stops:
        routesAtThisStop = requests.get(cumtdAPIBase + "GetRoutesByStop", params={"key": cumtdAPIKey, "stop_id": stop["stop_id"]}).json()["routes"]
        for route in routesAtThisStop:
            if preferredRoutes is None or preferredRoutes is not None and route["route_long_name"] in preferredRoutes:
                stopsWithPreferredRoutes.append(stop)

    return stopsWithPreferredRoutes

"""
Given a latitude and longitude coordinate pair for an apartment, a distance threshold, and a list of preferred bus lines
return all the preferred bus routes serving stops at most "dist" feet away from the location
"""
def getRoutesNearLatLong(lat, lon, dist, preferredRoutes=None):
    stopsWithinDist = getRoutesNearLatLongWithinDist(lat, lon, dist)
    stopsWithPreferredRoutes = groupStopsByPreference(stopsWithinDist, preferredRoutes)

    return stopsWithPreferredRoutes

#print(getRoutesNearLatLong(40.107227, -88.238197, 1000, ['Illini Evening']))
