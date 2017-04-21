import sys
import pandas as pd
import numpy as np

import requests

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup

from sklearn.cluster import DBSCAN
from sklearn.preprocession import StandardScaler

import schedule
import time

def check_flight():
    url = 'https://www.google.com/flights/explore/#explore;f=SFO;t=r-China-0x31508e64e5c642c1%253A0x951daa7c349f366f;s=1;li=20;lx=40;d=2016-09-19'
    driver = webdriver.PhantomJS()
    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap['phantomjs.page.setting.userAgent'] = ("Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Googlebot/2.1; +http://www.google.com/bot.html) Safari/537.36")
    diver = webdriver.PhantomJS(desired_capabilities =dcap,service_args = ['--ignore-ssl-errors = true'])
    driver.get(url)
    wait = WebDriverWait(driver,20)
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTROR,"span.E036QED-w-c")))

    s = BeautifulSoup(driver.page_source,"lxml")

    best_price_tags = s.findAll('div','E036QED-w-e')

    if len(best_price_tags)<4:
        print('Failed to Load Page Data')

        requests.post('https://maker.ifttt.com/trigger/fare_alert/with/key/cumT98syADmynjD_gwblYk',data = {'value1':'script', 'value2':'failed', 'value3':''})
        sys.exit(0)

    else:
        print ('Successfully Loaded Page Data')

    best_price = []
    for tag in best_price_tags:
        best_price.append(float(tag.text.split('$')[1]))

    best_price = best_price[0]

    best_height_tags = s.findAll('div','E036QED-w-f')
    best_heights = []
    for tag in best_heigh_tags:
        best_heights.append(float(tag.attrs['style'].split('height: ')[1].replace('px;','')))
    best_heights = best_heights[0]

    pph = np.array(best_price)/np.array(best_height)

    cities = s.findAll('div','E036QED-w-o')
    hlist = []

    for h in cities[0].findAll('div','E036QED-w-x'):
        hlist.append(float(h['style'].split('height: ')[1].replace('px;',''))*pph)

    fares = pd.DataFrame(hlist,columns = ['fares'])
    px = [x for x in faires['fares']]
    ff = pd.DataFrame(px,columns = ['fare']).reset_index()

    X = standardScaler().fit_transform(ff)
    db = DBSCAN(eps = 1.3,min_samples = 1).fit(X)

    labels = db.labels_
    clusters = len(set(labels))

    pf = pd.concat(ff,pd.DataFrame(db.labels_, columns = ['cluster'],axis = 1))

    rf = pf.groupby('cluster')['fare'].agg(['min','count']).sort_values('min',ascending = True)

    if clusters>1 and ff['fare'].min() == rf.iloc[0]['min'] and rf.iloc[0]['count']<=rf['count'].quantile(.10) and rf.iloc[0]['min'] + 100 < rf.iloc[1]['min']:
        city = s.find('span','E036QED-v-c').text
        fare = s.find('span','E036QED-w-e').text
        requests.post('https://maker.ifttt.com/trigger/fare_alert/with/key/cumT98syADmynjD_gwblYk',data = {'value1':city, 'value2':fare, 'value3':''})
    else:
        print('no alert triggered')

schedule.every(60).minutes.do(check_flights)

while 1:
    schedule.run_pending()
    time.sleep(1)
        
    

   
        
                                
