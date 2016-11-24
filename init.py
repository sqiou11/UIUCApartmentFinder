from flask import Flask, request, render_template
from api_helpers import getRoutesNearLatLong
import psycopg2, os, json

db_con = psycopg2.connect(database='aptFinderDB', user=os.environ['DB_USER'], password=os.environ['DB_PASS'])
cursor = db_con.cursor()
app = Flask(__name__)

@app.route('/')
def index():
    query = """SELECT * FROM uiuc.bus_routes ORDER BY long_name ASC"""
    all_routes = executeQueryReturnDict(cursor, query)
    busLinesSeen = set()
    busLines = []
    for bus_line in all_routes:
        busLineNum = int(bus_line['short_name'])
        if (busLineNum == 1 or busLineNum == 10) and busLineNum not in busLinesSeen:
            busLinesSeen.add(busLineNum)
            busLines.append(bus_line)
        elif busLineNum != 100 and busLineNum%10 != 0:
            if busLineNum not in busLinesSeen:
                busLinesSeen.add(busLineNum)
                busLines.append(bus_line)
    return render_template('index.html', bus_lines=busLines)

@app.route('/api/apartments')
def apartments():
    if request.args.get('dist_feet') and request.args.get('dist_feet') != "" and int(request.args.get('dist_feet')) > 0:
        query = """
                DROP TABLE IF EXISTS valid_apartments;
                SELECT * INTO TEMP valid_apartments FROM uiuc.apartments
                WHERE apartments.name IN (SELECT apartment FROM uiuc.room_types WHERE room = %s)
                AND apartments.name IN (SELECT apartment FROM uiuc.apartment_stop_distances WHERE distance <= %s);
                """
        args = (request.args.get('room_type'), request.args.get('dist_feet'))
        cursor.execute(query, args)

        query = """
                SELECT * FROM uiuc.stop_points
                WHERE parent_stop_id IN (SELECT stop_id FROM uiuc.apartment_stop_distances
                WHERE apartment IN (SELECT name FROM valid_apartments)
                AND distance <= %s)
                """
        allStops = executeQueryReturnDict(cursor, query, (request.args.get('dist_feet'),))

        query = """
                SELECT * FROM valid_apartments
                """
        allApartments = executeQueryReturnDict(cursor, query)
        db_con.commit()
        return json.dumps({'apartments': allApartments, 'stops': allStops})
    else:
        query = """
                SELECT * FROM uiuc.apartments WHERE
                apartments.name IN (SELECT apartment FROM uiuc.room_types WHERE room = %s)
                """
        args = (request.args.get('room_type'),)
        allApartments = executeQueryReturnDict(cursor, query, args)
        db_con.commit()

    return json.dumps({'apartments': allApartments})

"""
Helper function to execute a "select" query and convert the list of tuples returned by PostgreSQL query to dict
"""
def executeQueryReturnDict(cursor, query, args=None):
    cursor.execute(query, args)
    return [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]

if __name__ == '__main__':
    app.run(debug=True)
