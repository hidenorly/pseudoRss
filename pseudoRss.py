#!/usr/bin/env python3
# coding: utf-8

#   Copyright 2023 hidenorly
#
#   Licensed baseUrl the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed baseUrl the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations baseUrl the License.

import argparse
import os
import re
import string
import time
import datetime
import json
from urllib.parse import urljoin
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException

class HashCache:
    def __init__(self, cacheDir):
        self.cacheDir = cacheDir

    def getCacheFilename(self, url):
        parsed_url = urlparse(url)
        filename = parsed_url.netloc + parsed_url.path
        filename = re.sub(r'[^a-zA-Z0-9\-_.]', '_', filename)
        return os.path.join(self.cacheDir, filename)

    def ensureCacheStorage(self):
        if not os.path.exists(self.cacheDir):
            os.makedirs(self.cacheDir)

    def store(self, url, data):
        self.ensureCacheStorage()
        cachePath = self.getCacheFilename(url)

        dt_now = datetime.datetime.now()
        data["lastUpdate"] = dt_now.strftime("%Y-%m-%d %H:%M:%S")
        with open(cachePath, 'w', encoding='UTF-8') as f:
            json.dump(data, f, indent = 4, ensure_ascii=False)
            f.close()
        del data["lastUpdate"]

    def restore(self, url):
        result = {}

        cachePath = self.getCacheFilename(url)
        if os.path.exists( cachePath ):
            with open(cachePath, 'r', encoding='UTF-8') as f:
                result = json.load(f)
                if "lastUpdate" in result:
                    del result["lastUpdate"]

        return result


class WebLinkEnumerater:
    CONTROL_CHR_PATTERN = re.compile('[\x00-\x1f\x7f]')

    @staticmethod
    def isSameDomain(url1, url2, baseUrl=""):
        isSame = urlparse(url1).netloc == urlparse(url2).netloc
        isbaseUrl =  ( (baseUrl=="") or url2.startswith(baseUrl) )
        return isSame and isbaseUrl

    @staticmethod
    def getLinksByFactor(driver, pageUrl, byFactor=By.TAG_NAME, element='a', sameDomain=False, onlyTextExists=False):
        result = {}

        try:
            tag_name_elements = driver.find_elements(byFactor, element)
            for element in tag_name_elements:
                url = element.get_attribute('href')
                title = str(element.text).strip()
                title = WebLinkEnumerater.CONTROL_CHR_PATTERN.sub(' ', title)
                title = title.encode('utf-8', 'surrogatepass').decode('utf-8', 'ignore')
                if url:
                    if not sameDomain or WebLinkEnumerater.isSameDomain(pageUrl, url, pageUrl):
                        if not onlyTextExists or title:
                            result[url] = title
        except NoSuchElementException:
            pass

        return result

    @staticmethod
    def getLinks(driver, url, isSameDomain, onlyTextExists):
        result = {}

        driver.get(url)
        result = WebLinkEnumerater.getLinksByFactor(driver, url, By.TAG_NAME, 'a', isSameDomain, onlyTextExists)
        result.update( WebLinkEnumerater.getLinksByFactor(driver, url, By.CSS_SELECTOR, 'a.post-link', isSameDomain, onlyTextExists) )

        return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Pseudo RSS', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('pages', metavar='PAGE', type=str, nargs='+', help='Web pages')
    #parser.add_argument('-i', '--input', dest='inputPath', type=str, default='.', help='list.csv title,url,sameDomain true or false')
    parser.add_argument('-o', '--output', dest='outputPath', type=str, default='.', help='Output folder')
    parser.add_argument('-c', '--cache', dest='cacheDir', type=str, default='~/.pseudoRss', help='Cache Dir')
    parser.add_argument('-s', '--sameDomain', dest='sameDomain', action='store_true', default=False, help='Specify if you want to restrict in the same url')
    parser.add_argument('-t', '--onlyTextExists', dest='onlyTextExists', action='store_true', default=False, help='Specify if you want to restrict text existing link')
    args = parser.parse_args()

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1920, 1080)

    cache = HashCache(os.path.expanduser(args.cacheDir))

    for aUrl in args.pages:
        urlList = WebLinkEnumerater.getLinks(driver, aUrl, args.sameDomain, args.onlyTextExists)
        cache.store(aUrl, urlList)
        for theUrl, theTitle in urlList.items():
            print(str(theUrl)+":"+str(theTitle))

    driver.quit()



