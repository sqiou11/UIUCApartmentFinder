from bs4 import BeautifulSoup
from selenium import webdriver
from utils import executeParallel
import re, psycopg2, os, time, requests

db_con = psycopg2.connect(database='aptFinderDB', user=os.environ['DB_USER'], password=os.environ['DB_PASS'])
cursor = db_con.cursor()

domain = "http://www.roland-realty.com"
sources = [
    { "type": "Studio", "url": "http://www.roland-realty.com/studio-apartments.html" },
    { "type": "1 BR", "url": "http://www.roland-realty.com/1-bedroom-apartments.html" },
    { "type": "2 BR", "url": "http://www.roland-realty.com/2-bedroom-apartments.html" },
    { "type": "3 BR", "url": "http://www.roland-realty.com/3-bedroom-apartments.html" },
    { "type": "4 BR", "url": "http://www.roland-realty.com/4-bedroom-apartments.html" },
    { "type": "5 BR", "url": "http://www.roland-realty.com/5-bedroom-apartments.html" }
]

cumtdAPIBase = "https://developer.cumtd.com/api/v2.2/json/"
cumtdAPIKey = os.environ['CUMTD_API_KEY']

def getAptData(aptTuple):
    aptType = aptTuple[0]
    url = aptTuple[1]

    print("Starting process for " + str(aptTuple))
    aptDriver = webdriver.PhantomJS()
    aptDriver.get(url)
    aptSoup = BeautifulSoup(aptDriver.page_source, "lxml")

    aptName = aptSoup.find(class_="wsite-content-title")
    aptName = ''.join(aptName.find_all(text=True))
    aptName = aptName.replace(u'\xa0', ' ')
    aptMapSource = aptSoup.find(class_="wsite-map").find('iframe')['src']

    # grab longitude and latitude coordinates for this apartment
    longLatMatch = re.match(".*long=([\d.-]*)&lat=([\d.-]*).*", aptMapSource)
    longitude = longLatMatch.group(1)
    latitude = longLatMatch.group(2)

    aptDriver.quit()
    aptData = {'name': aptName, 'url': url, 'longitude': longitude, 'latitude': latitude, 'type': aptType}
    cursor.execute("""
        INSERT INTO uiuc.apartments (company, name, url, longitude, latitude) VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (company, name) DO NOTHING
        """, ("Roland Realty", aptData['name'], aptData['url'], aptData['longitude'], aptData['latitude']))
    db_con.commit()
    cursor.execute("""
        INSERT INTO uiuc.room_types (apartment, room) VALUES (%s, %s)
        ON CONFLICT (apartment, room) DO NOTHING
        """, (aptData['name'], aptData['type']))
    db_con.commit()

    distFromAllStops = requests.get(cumtdAPIBase + "GetStopsByLatLon", params={"key": cumtdAPIKey, "lat": aptData['latitude'], "lon": aptData['longitude'], "count": 30000}).json()["stops"]
    for stop in distFromAllStops:
        cursor.execute("""
            INSERT INTO uiuc.apartment_stop_distances (apartment, stop_id, distance) VALUES (%s, %s, %s)
            ON CONFLICT (apartment, stop_id) DO NOTHING
            """, (aptData['name'], stop['stop_id'], stop['distance']))
        db_con.commit()
    print("Exiting process for " + url)

def scrape():
    start = time.clock()
    aptUrls = []

    driver = webdriver.PhantomJS()
    for source in sources:
        driver.get(source['url'])

        soup = BeautifulSoup(driver.page_source, "lxml")
        table = soup.find("table", class_="wsite-multicol-table")
        apartments = table.find_all(class_="wslide-slide")

        for apt in apartments:
            aptUrl = apt.find("a")['href']
            if aptUrl != '/':
                aptUrls.append((source['type'], domain + aptUrl))
        print("Finished collecting urls from " + source['url'])
    driver.quit()

    executeParallel(getAptData, aptUrls, 4)
    print(time.clock() - start)

    db_con.close()

if __name__ == '__main__':
    scrape()
