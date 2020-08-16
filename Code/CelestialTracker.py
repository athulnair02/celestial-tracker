#!/usr/bin/env python
# coding: utf-8

# ## Web Scraping for Celestial Coordinates of Planets from TheSkyLive.com

# In[1]:


import bs4
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup as soup
import time
import argparse

parser = argparse.ArgumentParser(description="Get information on required celestial object.")
parser.add_argument('celestialObject', help='Which celestial object to look at.', type=str)

args = parser.parse_args()
celestialObject = args.celestialObject

# In[2]:
class CelestialBody:
    lastUpdate = time.localtime()
    
    def __init__(self, name, ra, dec):
        self.name = name
        self.ra = ra
        self.dec = dec
        
    def displayInfo(self):
        return "Name: " + self.name + " R.A: " + self.ra + " Dec: " + self.dec
    
    @classmethod
    def displayLastUpdate(CelestialBody):
        month = CelestialBody.lastUpdate.tm_mon
        day = CelestialBody.lastUpdate.tm_mday
        year = CelestialBody.lastUpdate.tm_year
        hour = CelestialBody.lastUpdate.tm_hour
        hour = "{0:0=2d}".format(hour)
        minute = CelestialBody.lastUpdate.tm_min
        minute = "{0:0=2d}".format(minute)
        sec = CelestialBody.lastUpdate.tm_sec
        sec = "{0:0=2d}".format(sec)
        return "Updated: " + str(month)+"/"+str(day)+"/"+str(year)+" "+str(hour)+":"+str(minute)+":"+str(sec)


# In[3]:

celestialBodiesDict = {}


# In[4]:


def reloadBodies():
    #celestialBodies = []
    celestialBodiesDict = {}
    #Opens website and dowloads html
    url = "https://theskylive.com/planets"
    uClient = urlopen(url)
    page_html = uClient.read()
    uClient.close()
    #HTML Parsing
    page_soup = soup(page_html, "html.parser")
    
    containers = page_soup.findAll("div", {"class":"object_container notvisible"})
    containers += page_soup.findAll("div", {"class":"object_container visible"})
    for container in containers:
        try:
            name = container["filter"]
        except:
            continue
        container_content = container.findAll("div", {"style":"text-align:center;vertical-align:center;"})
        info = container_content[0].text.replace('\n','')
        info = info.replace('\t','')
        info = info.replace('\xa0','')
        info = info.replace('\r','')
        info = info[0:info.index('Mag')]
        ra = info[info.index(':')+1 : info.index('s')+1]
        dec = info[info.index('Dec')+4:]
        celestialBodiesDict[name] = CelestialBody(name, ra, dec)
    CelestialBody.lastUpdate = time.localtime()
    return celestialBodiesDict 


# In[5]:


celestialBodiesDict = reloadBodies() 
for body in celestialBodiesDict:
    print(celestialBodiesDict[body].displayInfo())
CelestialBody.displayLastUpdate()


# ## Converting Celestial Coordinates into Alt-Az

# In[6]:


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import json
from datetime import datetime


# ### Finding my IP adress by Web Scraping Google

# In[12]:


chrome_options = Options()
chrome_options.add_argument("--headless")

PATH = '/usr/bin/chromedriver'
driver = webdriver.Chrome(executable_path=PATH, options=chrome_options)
url = 'https://whatismyipaddress.com'
driver.get(url)
ip = ''
try:
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "ipv4"))
    )
    ip = element.text
except:
    print('closed')
finally:
    driver.close()


# ### Long and Lat

# In[ ]:


#apiUrl = "http://api.ipstack.com/" +ip + "?access_key=0b762d0a0909e05254abb6c1278865c5"
#apiInfo = urlopen(apiUrl)
#data = json.load(apiInfo)
#lat = data["latitude"]
#lon = data['longitude']
#print(lat)
#print(lon)


# ### Return Alt-Az Co-ordinates

# In[9]:


def dd2ddm(value):
    deg = int(str(value).split('.')[0])
    minutes = float("0."+str(value).split('.')[-1])*60
    return (deg, minutes)


# In[10]:


lat = 29.740190505981445
lon = -95.8301773071289

if lon < 0:
    lonDir = 'W'
    lonAlt = float(str(lon)[1:])
else:
    lonDir = 'E'
    lonAlt = lon
    
if lat < 0:
    latDir = 'S'
    latAlt = float(str(lat)[1:])
else:
    latDir = 'N'
    latAlt = lat
    
print(latAlt, latDir)
print(lonAlt, lonDir)
latddm = dd2ddm(latAlt)
londdm = dd2ddm(lonAlt)
print(latddm, londdm)


# In[17]:


def getCelestialAltAz(celestialName):
    url = 'http://xjubier.free.fr/en/site_pages/astronomy/coordinatesConverter.html'
    driver = webdriver.Chrome(executable_path=PATH, options=chrome_options)
    driver.get(url)
    direction = ''
    celestialBodiesDict = reloadBodies()
    body = celestialBodiesDict[celestialName]
    try:
        rah = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "rah"))
        )

        ram = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "ram"))
        )

        ras = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "ras"))
        )
        raText = body.ra
        rahText = raText.split('h')[0].strip()
        ramText = raText.split('h')[-1].split('m')[0].strip()
        rasText = raText.split('h')[-1].split('m')[-1].split('s')[0].strip()

        rah.clear()
        ram.clear()
        ras.clear()
        rah.send_keys(rahText)
        ram.send_keys(ramText)
        ras.send_keys(rasText)
        print(rahText, ramText, rasText)

        decd = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "decd"))
        )

        decm = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "decm"))
        )

        decs = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "decs"))
        )
        decText = body.dec
        decdText = decText.split('°')[0].strip()
        decmText = decText.split('°')[-1].split('’')[0].strip()
        decsText = decText.split('°')[-1].split('’')[-1].split('”')[0].strip()

        decd.clear()
        decm.clear()
        decs.clear()
        decd.send_keys(decdText)
        decm.send_keys(decmText)
        decs.send_keys(decsText)
        print(decdText, decmText, decsText)

        day = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "day"))
        )

        month = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "month"))
        )

        year = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "year"))
        )
        today = datetime.utcnow()
        day.clear()
        day.send_keys(today.day)
        month.clear()
        month.send_keys(today.month)
        year.clear()
        year.send_keys(today.year)

        hour = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "hour"))
        )

        minute = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "minute"))
        )

        sec = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "second"))
        )
        hour.clear()
        minute.clear()
        sec.clear()
        hour.send_keys(today.hour)
        minute.send_keys(today.minute)
        sec.send_keys(today.second)

        latd = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "latd"))
        )
        latd.clear()
        latd.send_keys(latddm[0])

        latm = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "latm"))
        )
        latm.clear()
        latm.send_keys(str(latddm[1]))

        latx = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "latx"))
        )
        for option in latx.find_elements_by_tag_name('option'):
            if option.text == latDir:
                option.click() # select() in earlier versions of webdriver
                break

        lond = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "lond"))
        )
        lond.clear()
        lond.send_keys(londdm[0])

        lonm = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "lonm"))
        )
        lonm.clear()
        lonm.send_keys(str(londdm[1]))

        lonx = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "lonx"))
        )
        for option in lonx.find_elements_by_tag_name('option'):
            if option.text == lonDir:
                option.click() # select() in earlier versions of webdriver
                break
        updateBtn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='button']"))
        )
        updateBtn.click()

        alt = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[@id='altr']"))
        )
        altText = alt.text
        altitude = float(altText.split('°')[0])

        az = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[@id='azmr']"))
        )
        azText = az.text
        azimuth = float(azText.split('°')[0])
    except Exception as e:
        print(e)
        print('error')
    finally:
        driver.close()
        pass
    return (altitude, azimuth, body.name)


# In[18]:


getCelestialAltAz(celestialObject)
driver.quit()

# In[ ]:




