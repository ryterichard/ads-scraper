from collections import defaultdict
from googlesearch import search
from openpyxl import Workbook
import yaml
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import re
import time

with open("config.yml", "r") as ymlfile:
     config = yaml.safe_load(ymlfile)

wb = Workbook()
dest_filename = 'web_scraper_data.xlsx'
ws = wb.active

options = Options()
options.headless = True
options.set_preference("browser.link.open_newwindow.restriction", 0)
options.set_preference("browser.link.open_newwindow", 1)
driver = webdriver.Firefox(options=options, executable_path = 'venv/bin/geckodriver')

columns = config['excel']['columns']
record = []
for column in columns:
    record.append(column)
ws.append(record)

attribute_mappings = {'class':By.CLASS_NAME, 'tag':By.TAG_NAME, 'name':By.NAME, 'id': By.ID,
'xpath':By.XPATH, 'css':By.CSS_SELECTOR}

try:
    for query in config['sites']:
        for term in config['searchTerms']:
            search_query = query['searchQuery'] + " " + term
            print(search_query)
            results = None
            try:
                results = search(search_query, pause=60)
            except Exception as e:
                print(e)
            for result in results:
                try:
                    print(result)
                    time.sleep(3)
                    driver.get(result)
                    data = {}
                    data['publisher'] = query['publisher']
                    data['url'] = result
                    data['title'] = driver.title
                    data['keyword'] = term

                    if 'url' in query:
                        url_data = re.search(query['url'],result)
                        data.update(url_data.groupdict())

                    if 'data' in query:
                        for element_type in query['data']:
                            for element in query['data'][element_type]:
                                for value in query['data'][element_type][element]:
                                    finds = driver.find_elements(attribute_mappings[element_type], value)
                                    for find in finds:
                                        if element in data:
                                            data[element]+=("\n"+find.text)
                                        else:
                                            data[element] = find.text

                    if 'attribute' in query:
                        for element_type in query['attribute']:
                            for element in query['attribute'][element_type]:
                                for value in query['attribute'][element_type][element]:
                                    finds = driver.find_elements(attribute_mappings[element_type], value)
                                    for find in finds:
                                        attribute = find.get_attribute(query['attribute'][element_type][element][value])
                                        if element in data:
                                            data[element]+=("\n"+attribute)
                                        else:
                                            data[element] = attribute
                    record = []
                    if not 'article' in data:
                        data['article'] = driver.find_element(By.TAG_NAME, 'body').text
                    for column in columns:
                        record.append(data.get(column,""))
                    ws.append(record)
                except Exception as e: 
                    print(e)
finally:
    wb.save(filename = dest_filename)
    driver.quit()

wb.save(filename = dest_filename)
driver.quit()