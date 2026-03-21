import os
from dotenv import load_dotenv

# Load the hidden secrets from the .env file into memory
load_dotenv()

# --- Serial Port Settings ---
SERIAL_PORT = '/dev/ttyUSB0' 
BAUD_RATE = 115200

# --- System Settings ---
SPAM_WINDOW_SECONDS = 10
SPAM_MAX_MESSAGES = 5
HEARTBEAT_TIMEOUT = 15 

# --- WhatsApp Settings ---
USE_WHATSAPP = True
DOMAIN_URL = "https://amitaibenshalom.com"

# Securely grab the secrets
PHONE_NUMBER = os.getenv("PHONE_NUMBER")
API_KEY = os.getenv("API_KEY")

# Safety check so the server won't start if secrets are missing
if USE_WHATSAPP and (not PHONE_NUMBER or not API_KEY):
    raise ValueError("Missing WhatsApp credentials! Check your Server/.env file.")