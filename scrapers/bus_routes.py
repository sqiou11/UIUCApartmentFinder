import psycopg2, os, requests

cumtdAPIBase = "https://developer.cumtd.com/api/v2.2/json/GetRoutes"
cumtdAPIKey = "f6a8e3b691074f89b7b74a3a81379207"

db_con = psycopg2.connect(database='aptFinderDB', user=os.environ['DB_USER'], password=os.environ['DB_PASS'])
cursor = db_con.cursor()

bus_routes = requests.get(cumtdAPIBase, params={"key": cumtdAPIKey}).json()['routes']

for route in bus_routes:
    cursor.execute("""
        INSERT INTO public.bus_routes (id, short_name, long_name, color) VALUES (%s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING
        """, (route['route_id'], route['route_short_name'], route['route_long_name'], route['route_color']))
    db_con.commit()
