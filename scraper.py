import requests
from bs4 import BeautifulSoup
import json
import os
from notifier import send_whatsapp

BASE_URL = "https://www.funda.nl/en/koop/almere/huis/p{page}/"

if os.path.exists("listings.json"):
    with open("listings.json") as f:
        seen = set(json.load(f))
else:
    seen = set()

new_listings = []

for page in range(1,6):
    url = BASE_URL.format(page=page)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    listings_elements = soup.select("div.search-result__header a")

    for a in listings_elements:
        link = a['href']
        if link in seen:
            continue

        price_tag = a.find_next("span", class_="search-result-price")
        size_tag = a.find_next("span", class_="search-result-metrics__living-area")

        try:
            price_text = price_tag.text.strip().replace("€","").replace(".","").split()[0]
            price = int(price_text)
        except:
            price = 0

        try:
            size_text = size_tag.text.strip().replace("m²","").split()[0]
            size = int(size_text)
        except:
            size = 0

        if price <= 450000 and size >= 100:
            new_listings.append({"link": link, "price": price, "size": size})
            seen.add(link)

with open("listings.json", "w") as f:
    json.dump(list(seen), f)

if new_listings:
    send_whatsapp(new_listings)
