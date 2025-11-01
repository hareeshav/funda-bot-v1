from twilio.rest import Client
import os

ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER")
TO_NUMBER = os.getenv("MY_NUMBER")

client = Client(ACCOUNT_SID, AUTH_TOKEN)

def send_whatsapp(listings):
    for l in listings:
        message = f"New Funda listing:\n{l['link']}\nPrice: €{l['price']}\nSize: {l['size']} m²"
        client.messages.create(body=message, from_=FROM_NUMBER, to=TO_NUMBER)
