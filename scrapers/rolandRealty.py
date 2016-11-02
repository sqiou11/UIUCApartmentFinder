from bs4 import BeautifulSoup
import requests
import re, urlparse

from selenium import webdriver
from time import sleep

domain = "http://www.roland-realty.com"
urls = [
    "http://www.roland-realty.com/studio-apartments.html",
    #"http://www.roland-realty.com/1-bedroom-apartments.html",
    #"http://www.roland-realty.com/2-bedroom-apartments.html",
    #"http://www.roland-realty.com/3-bedroom-apartments.html",
    #"http://www.roland-realty.com/4-bedroom-apartments.html",
    #"http://www.roland-realty.com/5-bedroom-apartments.html"
]


for url in urls:
    data = []
    driver = webdriver.PhantomJS()
    driver.set_window_size(1120, 550)
    driver.get(url)

    soup = BeautifulSoup(driver.page_source, "lxml")
    table = soup.find("table", class_="wsite-multicol-table")
    apartments = table.find_all(class_="wslide-slide")

    for apt in apartments:
        aptUrl = domain + apt.find("a")['href']

        # start an apartment-specific PhantomJS instance to grab details about individual apartments
        aptDriver = webdriver.PhantomJS()
        aptDriver.set_window_size(1120, 550)
        aptDriver.get(aptUrl)
        aptSoup = BeautifulSoup(aptDriver.page_source, "lxml")
        aptName = aptSoup.find(class_="wsite-content-title").string
        aptMapSource = aptSoup.find(class_="wsite-map").find('iframe')['src']

        # grab longitude and latitude coordinates for this apartment
        longLatMatch = re.match(".*long=([\d.-]*)&lat=([\d.-]*).*", aptMapSource)
        longitude = longLatMatch.group(1)
        latitude = longLatMatch.group(2)

        aptDriver.quit()

        data.append({'name': aptName, 'url': aptUrl, 'longitude': longitude, 'latitude': latitude})

    print(data)
    driver.quit()
