from flask import Flask, request, render_template
from api_helpers import getRoutesNearLatLong
import psycopg2, os, json

db_con = psycopg2.connect(database='aptFinderDB', user=os.environ['DB_USER'], password=os.environ['DB_PASS'])
cursor = db_con.cursor()
app = Flask(__name__)

@app.route('/')
def index():

    return render_template('index.html')

@app.route('/api/apartments')
def apartments():
    room_type = request.args.get('room_type')
    cursor.execute("""SELECT * FROM public.apartments, public.room_types WHERE public.apartments.name = public.room_types.apartment AND room = %s""", (request.args.get('room_type'),))
    allApartments = queryResultsToDict(cursor)

    if request.args.get('dist_from_stops'):
        apartmentsWithBusStops = { 'apartments': [], 'stops': [] }
        stopsSeenSoFar = set()
        for apartment in allApartments:
            stopsWithPreferredRoutes = getRoutesNearLatLong(apartment['latitude'], apartment['longitude'], int(request.args.get('dist_from_stops')))
            print(stopsWithPreferredRoutes)
            if not stopsWithPreferredRoutes == []:
                apartmentsWithBusStops['apartments'].append(apartment)
                for stop in stopsWithPreferredRoutes:
                    if stop['stop_id'] not in stopsSeenSoFar:
                        apartmentsWithBusStops['stops'].append(stop)
                        stopsSeenSoFar.add(stop['stop_id'])
        return json.dumps(apartmentsWithBusStops)
    else:
        return json.dumps({ 'apartments': allApartments })

"""
Helper function to convert the list of tuples returned by PostgreSQL query to dict
Expects a call to cursor.execute() to have previously been made.
"""
def queryResultsToDict(cursor):
    return [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]

if __name__ == '__main__':
    app.run(debug=True)

# print(getRoutesNearLatLong(40.107053, -88.2390549, 500))
