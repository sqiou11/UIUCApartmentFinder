from bs4 import BeautifulSoup
from selenium import webdriver
import re, psycopg2, os, time, multiprocessing, multiprocessing.dummy, socket, errno

db_con = psycopg2.connect(database='aptFinderDB', user=os.environ['DB_USER'], password=os.environ['DB_PASS'])
cursor = db_con.cursor()

domain = "http://www.roland-realty.com"
sources = [
    { "type": "studio", "url": "http://www.roland-realty.com/studio-apartments.html" },
    { "type": "1 bed", "url": "http://www.roland-realty.com/1-bedroom-apartments.html" },
    { "type": "2 bed", "url": "http://www.roland-realty.com/2-bedroom-apartments.html" },
    { "type": "3 bed", "url": "http://www.roland-realty.com/3-bedroom-apartments.html" },
    { "type": "4 bed", "url": "http://www.roland-realty.com/4-bedroom-apartments.html" },
    { "type": "5 bed", "url": "http://www.roland-realty.com/5-bedroom-apartments.html" }
]

def getAptData(aptTuple):
    aptType = aptTuple[0]
    url = aptTuple[1]

    print("Starting thread for " + str(aptTuple))
    try:
        aptDriver = webdriver.PhantomJS()
        aptDriver.get(url)
        aptSoup = BeautifulSoup(aptDriver.page_source, "lxml")
        aptName = aptSoup.find(class_="wsite-content-title").string.replace(u'\xa0', ' ')
        aptMapSource = aptSoup.find(class_="wsite-map").find('iframe')['src']

        # grab longitude and latitude coordinates for this apartment
        longLatMatch = re.match(".*long=([\d.-]*)&lat=([\d.-]*).*", aptMapSource)
        longitude = longLatMatch.group(1)
        latitude = longLatMatch.group(2)

        aptDriver.quit()
        #threadLock.acquire()
        data.append({'name': aptName, 'url': url, 'longitude': longitude, 'latitude': latitude, 'type': aptType})
        #threadLock.release()
        print("Exiting thread for " + url)
    except socket.error as error:
        if error.errno == errno.WSAECONNRESET:
            print("Socket connection closed unexpectedly for " + url + "! Retrying...")
            getAptData(aptTuple)

# parallel processing of all urls using a pool of threads
def processUrls(aptUrls, threads=2):
    pool = multiprocessing.dummy.Pool(threads)
    pool.map(getAptData, aptUrls)
    pool.close()
    pool.join()

start = time.clock()
data = []
aptUrls = []
threadLock = multiprocessing.Lock()

for source in sources:
    driver = webdriver.PhantomJS()
    driver.get(source['url'])

    soup = BeautifulSoup(driver.page_source, "lxml")
    table = soup.find("table", class_="wsite-multicol-table")
    apartments = table.find_all(class_="wslide-slide")

    for apt in apartments:
        aptUrl = apt.find("a")['href']
        if aptUrl != '/':
            aptUrls.append((source['type'], domain + aptUrl))
    driver.quit()
    print("Finished collecting urls from " + source['url'])

processUrls(aptUrls, 16)

for aptData in data:
    print(aptData)
    cursor.execute("""
        INSERT INTO public.apartments (company, name, url, longitude, latitude, type) VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (company, name, type) DO NOTHING
        """, ("Roland Realty", aptData['name'], aptData['url'], aptData['longitude'], aptData['latitude'], aptData['type']))
    db_con.commit()
db_con.close()
print(time.clock() - start)
