import requests
import urllib.parse
from config import USE_WHATSAPP, PHONE_NUMBER, API_KEY

def send_whatsapp_message(message, force=False):
    if not USE_WHATSAPP:
        return
    
    encoded_msg = urllib.parse.quote(message)
    url = f"https://api.callmebot.com/whatsapp.php?phone={PHONE_NUMBER}&apikey={API_KEY}&text={encoded_msg}"
    
    try:
        response = requests.post(url, timeout=5)
        if response.status_code == 200:
            print(f"WhatsApp message sent successfully")
        else:
            print(f"Error sending WhatsApp: {response.status_code}")
    except Exception as e:
        print(f"WhatsApp request failed: {e}")