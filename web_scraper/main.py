import csv
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urlencode

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'}
base_parse_url = 'https://www.amazon.com/Nike-Force-Womens-Low-Top-Sneakers/product-reviews/B000SBYEG2/ref=cm_cr_arp_d_paging_btm_next_2?pageNumber='
reviews_titles = []
reviews = []
ratings = []

for page in range(1, 2):
    print(page)
    
    params = {'api_key': "a95ba7d6d66842c22f61b709617ca11b", 'url': base_parse_url + str(page)}
    response = requests.get('http://api.scraperapi.com/',   params=urlencode(params))
    soup = BeautifulSoup(response.text, 'html.parser')

    print(soup)

    for item in soup.find_all("span", {"data-hook": "review-body"}):
      data_string = item.get_text()
      reviews.append(data_string)

    time.sleep(3);

print(reviews)