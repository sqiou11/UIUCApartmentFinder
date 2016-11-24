import psycopg2, os, requests

cumtdAPIBase = "https://developer.cumtd.com/api/v2.2/json/"
cumtdAPIKey = os.environ['CUMTD_API_KEY']

db_con = psycopg2.connect(database='aptFinderDB', user=os.environ['DB_USER'], password=os.environ['DB_PASS'])
cursor = db_con.cursor()

def createRouteAndShapeTables():
    bus_routes = requests.get(cumtdAPIBase + "GetRoutes", params={"key": cumtdAPIKey}).json()['routes']
    shapeIdSet = set()

    for route in bus_routes:
        cursor.execute("""
            INSERT INTO uiuc.bus_routes (id, short_name, long_name, color) VALUES (%s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
            """, (route['route_id'], route['route_short_name'], route['route_long_name'], route['route_color']))
        route_shapes = requests.get(cumtdAPIBase + "GetTripsByRoute", params={"key": cumtdAPIKey, "route_id": route['route_id']}).json()['trips']

        for shape in route_shapes:
            if shape['shape_id'] not in shapeIdSet:
                shapeIdSet.add(shape['shape_id'])
                cursor.execute("""
                    INSERT INTO uiuc.bus_route_shapes (route_id, shape_id) VALUES (%s, %s)
                    ON CONFLICT (route_id, shape_id) DO NOTHING
                    """, (route['route_id'], shape['shape_id']))
    db_con.commit()

def getAllBusStopData():
    all_stops = requests.get(cumtdAPIBase + "GetStops", params={"key": cumtdAPIKey}).json()['stops']
    for stop in all_stops:
        cursor.execute("""
            INSERT INTO uiuc.stops (stop_id, stop_name, code) VALUES (%s, %s, %s)
            ON CONFLICT (stop_id) DO NOTHING
            """, (stop['stop_id'], stop['stop_name'], stop['code']))
        for stop_point in stop['stop_points']:
            cursor.execute("""
                INSERT INTO uiuc.stop_points (stop_id, stop_name, code, stop_lat, stop_lon, parent_stop_id) VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (stop_id) DO NOTHING
                """, (stop_point['stop_id'], stop_point['stop_name'], stop_point['code'], stop_point['stop_lat'], stop_point['stop_lon'], stop['stop_id']))
    db_con.commit()

#createRouteAndShapeTables()
getAllBusStopData()
