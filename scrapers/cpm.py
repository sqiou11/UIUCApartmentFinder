from bs4 import BeautifulSoup
from utils import executeParallel
import re, psycopg2, os, time, urllib2, requests

geocodingAPIKey = "AIzaSyAs4i4EhejeZRHb2xV_EDmVoC-ByBa9T-4"
geocodingAPIRequestBase = "https://maps.googleapis.com/maps/api/geocode/json"
db_con = psycopg2.connect(database='aptFinderDB', user=os.environ['DB_USER'], password=os.environ['DB_PASS'])
cursor = db_con.cursor()

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

    for roomType in roomTypes:
        aptData = {'name': aptName, 'url': url, 'longitude': longitude, 'latitude': latitude, 'type': roomType}
        cursor.execute("""
            INSERT INTO public.apartments (company, name, url, longitude, latitude) VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (company, name) DO NOTHING
            """, ("CPM", aptData['name'], aptData['url'], aptData['longitude'], aptData['latitude']))
        cursor.execute("""
            INSERT INTO public.room_types (apartment, room) VALUES (%s, %s)
            ON CONFLICT (apartment, room) DO NOTHING
            """, (aptData['name'], aptData['type']))
        db_con.commit()
    print("Exiting thread for " + url)

def scrape():
    domain = "http://cpm-apts.com"
    url = "http://cpm-apts.com/apartment/"
    start = time.clock()
    data = []
    aptUrls = []

    page_source = urllib2.urlopen(url).read()
    with open("out", "w+") as f:
        f.write(page_source)
        f.close()
    soup = BeautifulSoup(page_source, "lxml")
    apartments = soup.find_all(id=re.compile(r"idx\-\d+"))
    for apt in apartments:
        aptUrl = apt.find("a")['href']
        aptUrls.append(aptUrl)

    print("Finished collecting urls from " + url)
    #print(aptUrls)
    executeParallel(getAptData, aptUrls, 4)

    db_con.close()
    print(time.clock() - start)

if __name__ == '__main__':
    scrape()
