from bs4 import BeautifulSoup
from utils import executeParallel
import re, psycopg2, os, time, urllib2, requests

geocodingAPIKey = os.environ['GMAP_GEOCODING_API_KEY']
geocodingAPIRequestBase = "https://maps.googleapis.com/maps/api/geocode/json"
db_con = psycopg2.connect(database='aptFinderDB', user=os.environ['DB_USER'], password=os.environ['DB_PASS'])
cursor = db_con.cursor()

cumtdAPIBase = "https://developer.cumtd.com/api/v2.2/json/"
cumtdAPIKey = os.environ['CUMTD_API_KEY']

def getAptData(url):
    print("Starting process for " + url)

    aptSource = urllib2.urlopen(url).read()
    aptSoup = BeautifulSoup(aptSource, "lxml")
    roomTypesTable = aptSoup.find(id="room-type")
    roomTypesTableRows = roomTypesTable.find('tbody').find_all('tr')
    roomTypes = []
    for row in roomTypesTableRows:
        roomTypes.append(row.find('td').string)

    aptName = aptSoup.find(class_="pageTitle").string

    # grab longitude and latitude coordinates for this apartment
    geocodingData = requests.get(geocodingAPIRequestBase, params={"address": aptName, "key": geocodingAPIKey}).json()
    longLat = geocodingData['results'][0]['geometry']['location']
    longitude = longLat['lng']
    latitude = longLat['lat']

    aptData = {'name': aptName, 'url': url, 'longitude': longitude, 'latitude': latitude}
    cursor.execute("""
        INSERT INTO uiuc.apartments (company, name, url, longitude, latitude) VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (company, name) DO NOTHING
        """, ("CPM", aptData['name'], aptData['url'], aptData['longitude'], aptData['latitude']))
    db_con.commit()

    for roomType in roomTypes:
        cursor.execute("""
            INSERT INTO uiuc.room_types (apartment, room) VALUES (%s, %s)
            ON CONFLICT (apartment, room) DO NOTHING
            """, (aptData['name'], roomType))
        db_con.commit()

    distFromAllStops = requests.get(cumtdAPIBase + "GetStopsByLatLon", params={"key": cumtdAPIKey, "lat": aptData['latitude'], "lon": aptData['longitude'], "count": 30000}).json()["stops"]
    for stop in distFromAllStops:
        cursor.execute("""
            INSERT INTO uiuc.apartment_stop_distances (apartment, stop_id, distance) VALUES (%s, %s, %s)
            ON CONFLICT (apartment, stop_id) DO NOTHING
            """, (aptData['name'], stop['stop_id'], stop['distance']))
        db_con.commit()

    print("Exiting thread for " + url)

def scrape():
    domain = "http://cpm-apts.com"
    url = "http://cpm-apts.com/apartment/"
    start = time.clock()
    data = []
    aptUrls = []

    page_source = urllib2.urlopen(url).read()
    soup = BeautifulSoup(page_source, "lxml")
    apartments = soup.find_all(id=re.compile(r"idx\-\d+"))
    for apt in apartments:
        aptUrl = apt.find("a")['href']
        aptUrls.append(aptUrl)

    print("Finished collecting urls from " + url)
    executeParallel(getAptData, aptUrls, 4)

    db_con.close()
    print(time.clock() - start)

if __name__ == '__main__':
    scrape()
