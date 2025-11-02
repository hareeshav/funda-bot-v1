import requests
from bs4 import BeautifulSoup
import json
import os
from notifier import send_whatsapp

BASE_URL = "https://www.funda.nl/koop/almere/p{page}/"

# Load previously seen listings
if os.path.exists("listings.json"):
    with open("listings.json") as f:
        seen = set(json.load(f))
else:
    seen = set()

new_listings = []

print("Starting Funda scraping...")

for page in range(1, 3):  # first 2 pages
    url = BASE_URL.format(page=page)
    print(f"Fetching page {page}: {url}")
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch page {page}, status code: {response.status_code}")
        continue

    soup = BeautifulSoup(response.text, "html.parser")
    listings = soup.select("section.search-result")  # Updated selector for current Funda

    print(f"Found {len(listings)} listings on page {page}")

    for listing in listings:
        # Extract link
        a_tag = listing.select_one("a.search-result__header-link")
        if not a_tag:
            continue
        link = "https://www.funda.nl" + a_tag['href']

        if link in seen:
            continue

        # Extract address
        address_tag = listing.select_one("h2.search-result__title")
        address = address_tag.text.strip() if address_tag else "Unknown"

        # Extract price
        price_tag = listing.select_one("span.search-result-price")
        try:
            price_text = price_tag.text.strip().replace("€", "").replace(".", "").split()[0]
            price = int(price_text)
        except:
            price = 0

        # Extract living area
        size_tag = listing.select_one("span.search-result-metrics__living-area")
        try:
            size_text = size_tag.text.strip().replace("m²", "").split()[0]
            size = int(size_text)
        except:
            size = 0

        # Apply criteria
        if price <= 450000 and size >= 100:
            new_listings.append({
                "link": link,
                "address": address,
                "price": price,
                "size": size
            })
            seen.add(link)

print(f"Total new listings found: {len(new_listings)}")

# Save updated seen listings
with open("listings.json", "w") as f:
    json.dump(list(seen), f)

# Send WhatsApp notifications
if new_listings:
    message = "New Funda listings in Almere:\n\n"
    for idx, l in enumerate(new_listings, start=1):
        message += f"{idx}. {l['address']}\n   €{l['price']}, {l['size']} m²\n   {l['link']}\n\n"
    send_whatsapp(message)
    print("Messages sent successfully.")
else:
    print("No new listings to send.")

