import feedparser
import json
import os
from notifier import send_whatsapp

RSS_URL = "https://www.funda.nl/koop/almere/rss/"
MAX_PRICE = 450000
MIN_SIZE = 100

# Load previously seen listings
if os.path.exists("listings.json"):
    with open("listings.json") as f:
        seen = set(json.load(f))
else:
    seen = set()

new_listings = []

print("Starting Funda scraping via RSS feed...")

feed = feedparser.parse(RSS_URL)

for entry in feed.entries:
    link = entry.link
    if link in seen:
        continue

    # Example: extract price and size from title or summary
    title = entry.title  # e.g., "B. Merkelbachstraat 43, Almere - €425.000 k.k. - 103 m²"
    
    try:
        # Extract price
        price_str = title.split("€")[1].split(" ")[0].replace(".", "")
        price = int(price_str)
    except:
        price = 0

    try:
        # Extract size
        size_str = title.split("-")[-1].strip().replace("m²","")
        size = int(size_str)
    except:
        size = 0

    if price <= MAX_PRICE and size >= MIN_SIZE:
        new_listings.append({
            "link": link,
            "title": title,
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
        message += f"{idx}. {l['title']}\n   {l['link']}\n\n"
    send_whatsapp(message)
    print("Messages sent successfully.")
else:
    print("No new listings to send.")

