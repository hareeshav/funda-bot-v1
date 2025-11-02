import requests
from bs4 import BeautifulSoup
import json
import os
from notifier import send_whatsapp

BASE_URL = "https://www.funda.nl/en/koop/almere/huis/p{page}/"

# Load previously seen listings
if os.path.exists("listings.json"):
    with open("listings.json") as f:
        seen = set(json.load(f))
else:
    seen = set()

new_listings = []

print("Starting Funda scraping...")

for page in range(1, 6):  # scrape first 5 pages
    url = BASE_URL.format(page=page)
    print(f"Fetching page {page}: {url}")
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch page {page}, status code: {response.status_code}")
        continue

    soup = BeautifulSoup(response.text, "html.parser")
    listings_elements = soup.select("div.search-result__header a")

    print(f"Found {len(listings_elements)} listings on page {page}")

    for a in listings_elements:
        link = a['href']
        if link in seen:
            continue

        price_tag = a.find_next("span", class_="search-result-price")
        size_tag = a.find_next("span", class_="search-result-metrics__living-area")

        try:
            price_text = price_tag.text.strip().replace("€", "").replace(".", "").split()[0]
            price = int(price_text)
        except:
            price = 0

        try:
            size_text = size_tag.text.strip().replace("m²", "").split()[0]
            size = int(size_text)
        except:
            size = 0

        if price <= 450000 and size >= 100:
            new_listings.append({"link": link, "price": price, "size": size})
            seen.add(link)

print(f"Total new listings found: {len(new_listings)}")

# Save updated seen listings
with open("listings.json", "w") as f:
    json.dump(list(seen), f)

# Send WhatsApp notifications
if new_listings:
    print("Sending WhatsApp messages for new listings...")
    send_whatsapp(new_listings)
    print("Messages sent successfully.")
else:
    print("No new listings to send.")

# Optional: Send a test message to verify Twilio works
print("Sending test message to verify Twilio configuration...")
send_whatsapp([{"link": "https://funda.nl", "price": 100, "size": 120}])
print("Test message sent. Check your WhatsApp.")

