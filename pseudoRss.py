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
from urllib.parse import urljoin
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException

class WebPageHelper:
    CONTROL_CHR_PATTERN = re.compile('[\x00-\x1f\x7f]')

    def isSameDomain(url1, url2, baseUrl=""):
        isSame = urlparse(url1).netloc == urlparse(url2).netloc
        isbaseUrl =  ( (baseUrl=="") or url2.startswith(baseUrl) )
        return isSame and isbaseUrl

    def getLinksByFactor(driver, pageUrl, byFactor=By.TAG_NAME, element='a', sameDomain=False):
        result = {}

        try:
            tag_name_elements = driver.find_elements(byFactor, element)
            for element in tag_name_elements:
                url = element.get_attribute('href')
                title = str(element.text).strip()
                title = WebPageHelper.CONTROL_CHR_PATTERN.sub(' ', title)
                title = title.encode('utf-8', 'surrogatepass').decode('utf-8', 'ignore')
                if url:
                    if not sameDomain or WebPageHelper.isSameDomain(pageUrl, url, pageUrl):
                        result[url] = title
        except NoSuchElementException:
            pass

        return result

    def getLinks(driver, url, isSameDomain):
        result = {}

        driver.get(url)
        result = WebPageHelper.getLinksByFactor(driver, url, By.TAG_NAME, 'a', isSameDomain)
        result.update( WebPageHelper.getLinksByFactor(driver, url, By.CSS_SELECTOR, 'a.post-link', isSameDomain) )

        return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('pages', metavar='PAGE', type=str, nargs='+', help='Web pages')
    #parser.add_argument('-i', '--input', dest='inputPath', type=str, default='.', help='list.csv title,url,sameDomain true or false')
    parser.add_argument('-o', '--output', dest='outputPath', type=str, default='.', help='Output folder')
    parser.add_argument('-s', '--sameDomain', dest='sameDomain', action='store_true', default=False, help='Specify if you want to restrict in the same url')
    args = parser.parse_args()

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1920, 1080)

    for aUrl in args.pages:
        urlList = WebPageHelper.getLinks(driver, aUrl, args.sameDomain)
        for theUrl, theTitle in urlList.items():
            print(str(theUrl)+":"+str(theTitle))

    driver.quit()



