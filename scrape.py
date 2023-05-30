# skrypt powstał jedynie w celach edukacyjnych

# dokumentacja BeautifulSoup: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
# dokumentacja selenium: https://selenium-python.readthedocs.io/index.html

import classes
from bs4 import BeautifulSoup as bfs
import requests
from csv import writer
import time
from selenium import webdriver

property_type = 'mieszkanie'
region = 'slaskie'
url = f'//link//{property_type}/{region}' # wklejamy tu link, z którego korzystaliśmy na zajęciach

# https://chromedriver.chromium.org/downloads
driver = webdriver.Chrome(r'miejsce na ścieżkę relatywną/absolutną do webdrivera')
# u mnie było to: 'C:\Users\krzys\Downloads\chromedriver'
ads_count = 0

def driver_scrape_page(url, wait_time = 0.5):
    driver.get(url)
    driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
    time.sleep(wait_time)
    parsed_page = bfs(driver.page_source, 'html.parser')
    return parsed_page

doc = driver_scrape_page(url)
last_page_number = 30
# last_page_number = doc.find(attrs= { 'data-cy' : 'search-list-pagination' }).find_all('button', class_ = classes.pagination_button_css_class)[-2].text //rzeczywista liczba wszystkich kart

with open(f'{property_type}_{region}.csv', 'w', encoding='utf-8', newline='') as file:
    csv_writer = writer(file)
    header = ['obszar', 'lokacja', 'cena', 'przestrzeń_m2', 'cena_m2', 'ilość_pokoi']
    csv_writer.writerow(header)

    for page in range(1, int(last_page_number) + 1):
        print(f'scraping page {page}')
        page_url = f'{url}?page={page}'
        parsed_page = driver_scrape_page(page_url)

        items_container = parsed_page.find(attrs= classes.items_container)
        listing_items = items_container.find_all('li', class_ = classes.container_li_tag_css_class)
        ads_count += len(listing_items)


        for listing_item in listing_items:
            item = listing_item.a
            link = item['href']
            location = item.find('p', class_ = classes.location_css_class).text

            description = list(item.find('div', class_ = classes.item_description_css_class))
            price = None if ("Zapytaj" in description[0].text or 'od' in description[0].text) else ''.join(description[0].text.split('\xa0')[:-1]).replace(',','.')
            sq_price = ''.join(description[1].text.split('\xa0')[:-1]).replace(',','.') if len(str(description[1].text).split('\xa0')[0]) > 0 else None
            num_rooms = description[2].text.split(' ')[0] if 2 in range(len(description)) else None
            sq_meters = description[3].text.split(' ')[0] if 3 in range(len(description)) else None

            csv_writer.writerow([region, location, price, sq_meters, sq_price, num_rooms])

driver.quit()
print(f'Number of advertisements: {ads_count}')