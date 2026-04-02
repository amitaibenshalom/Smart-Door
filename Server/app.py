import os
import threading
import time
from datetime import datetime

import requests
import serial
from config import (
    BAUD_RATE,
    DOMAIN_URL,
    HEARTBEAT_TIMEOUT,
    REGISTER_TOKENS_API_KEY,
    SERIAL_PORT,
    SPAM_MAX_MESSAGES,
    SPAM_WINDOW_SECONDS,
)
from flask import Flask, jsonify, render_template, request, send_from_directory
from whatsapp import send_whatsapp_message

app = Flask(__name__)

# -- STATE STORAGE --
door_state = {
    "status": "closed",
    "last_change": datetime.now(),
    "last_heartbeat": time.time(),
}

# used for push notifications on "TzufGuard", you can ignore this line
TOKEN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".tokens.txt")

change_timestamps = []
spam_warning_sent = False


def is_spamming(current_time):
    global change_timestamps
    change_timestamps = [
        t for t in change_timestamps if current_time - t < SPAM_WINDOW_SECONDS
    ]
    change_timestamps.append(current_time)
    return len(change_timestamps) >= SPAM_MAX_MESSAGES


def read_serial():
    while True:
        ser = None
        try:
            # Attempt to open the serial port
            ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
            ser.setDTR(False)  # Release the ESP32 from reset
            ser.setRTS(False)  # Release the ESP32 from bootloader mode
            print(f"SUCCESS: Connected to ESP32 on {SERIAL_PORT}")

            # Inner loop: Read data as long as the connection is alive
            while True:
                try:
                    if ser.in_waiting > 0:
                        line = ser.readline().decode("utf-8", errors="ignore").strip()

                        if line == "ping":
                            door_state["last_heartbeat"] = time.time()
                        elif line in ["open", "close"]:
                            handle_door_change(line)
                            door_state["last_heartbeat"] = time.time()

                except serial.SerialException as e:
                    print(f"ERROR: USB connection lost! ({e})")
                    break  # Break inner loop to trigger the finally block and reconnect

        except serial.SerialException as e:
            print(f"CONNECTION FAILED: Cannot open {SERIAL_PORT} -> {e}")
            time.sleep(2)

        except Exception as e:
            print(f"CRITICAL ERROR: {e}")
            time.sleep(2)

        finally:
            # Always close the dead port
            if ser is not None and ser.is_open:
                ser.close()


# used for push notifications of "TzufGuard" app, you can ignore
def notify_all_users(door_status):
    # Only run if we actually have saved tokens
    if not os.path.exists(TOKEN_FILE):
        return

    with open(TOKEN_FILE, "r") as f:
        tokens = f.read().splitlines()

    url = "https://exp.host/--/api/v2/push/send"

    # Customize the message based on the door status
    title = "Door Alert 🚨" if door_status == "open" else "Door Update 🚪"
    message = (
        "Someone opened the door!" if door_status == "open" else "Door is closed :)"
    )

    # Loop through every user and send the push!
    for token in tokens:
        payload = {"to": token, "title": title, "body": message, "sound": "default"}

        try:
            response = requests.post(url, json=payload)
            print(f"Sent to {token}: {response.status_code}")
        except Exception as e:
            print(f"Failed to send to {token}: {e}")


def handle_door_change(new_status):
    global spam_warning_sent

    if new_status != door_state["status"]:
        door_state["status"] = new_status
        door_state["last_change"] = datetime.now()
        print(f"Serial Update: Door is now {new_status}")
        notify_all_users(door_state["status"])

        now = time.time()

        # If we hit 5 changes in 10 seconds...
        if is_spamming(now):
            print("Spamming detected!")
            # Only send the warning ONCE until the spamming stops
            if not spam_warning_sent:
                send_whatsapp_message(
                    "*⚠️ Spamming detected! Muting notifications until the door settles.*",
                    force=True,
                )
                spam_warning_sent = True

        # Normal behavior
        else:
            spam_warning_sent = (
                False  # Reset the mute toggle because the door settled down
            )
            msg = "DOOR OPENED!!!" if new_status == "open" else "Door closed :)"
            send_whatsapp_message(msg, force=False)


@app.route("/")
def dashboard():
    is_connected = (time.time() - door_state["last_heartbeat"]) <= HEARTBEAT_TIMEOUT
    return render_template(
        "index.html", door_state=door_state, is_connected=is_connected
    )


# for registering push-notification tokens for "TzufGuard" app, you can ignore this method
@app.route("/api/register-token", methods=["POST"])
def register_token():
    # 1. Check the bouncer! Look for the key in the headers
    client_key = request.headers.get("X-API-Key")

    if client_key != REGISTER_TOKENS_API_KEY:
        print("🚨 Blocked an unauthorized register token request!")
        return jsonify({"error": "Unauthorized."}), 401

    # 2. If they pass the check, process the token
    data = request.json
    token = data.get("token")

    if not token:
        return jsonify({"error": "No token provided"}), 400

    existing_tokens = set()
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            existing_tokens = set(f.read().splitlines())

    if token not in existing_tokens:
        with open(TOKEN_FILE, "a") as f:
            f.write(f"{token}\n")
        print(f"✅ Saved new token: {token}")

    return jsonify(
        {"message": "Token for push notification registered successfully!"}
    ), 200


# for unregistering push-notification tokens for "TzufGuard" app, you can ignore this method
@app.route("/api/unregister-token", methods=["POST"])
def unregister_token():
    # 1. Bouncer check!
    client_key = request.headers.get("X-API-Key")
    if client_key != REGISTER_TOKENS_API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    token = data.get("token")

    if not token:
        return jsonify({"error": "No token provided"}), 400

    # 2. Read the file, remove the token, and rewrite the file
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            tokens = f.read().splitlines()

        if token in tokens:
            tokens.remove(token)

            # Write the list back to the file without the deleted token
            with open(TOKEN_FILE, "w") as f:
                for t in tokens:
                    f.write(f"{t}\n")
            print(f"🗑️ Removed token: {token}")

    return jsonify({"message": "Token removed successfully!"}), 200


@app.route("/api/data")
def get_data():
    is_connected = (time.time() - door_state["last_heartbeat"]) <= HEARTBEAT_TIMEOUT
    return jsonify(
        {
            "status": door_state["status"],
            "timestamp": door_state["last_change"].timestamp(),
            "is_connected": is_connected,
        }
    )


@app.route("/sw.js")
def serve_sw():
    # This serves the service worker from the root URL /sw.js
    return send_from_directory("static", "sw.js")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


if __name__ == "__main__":
    threading.Thread(target=read_serial, daemon=True).start()
    send_whatsapp_message(f"*Smart Door Activated!*\n\n{DOMAIN_URL}")
    app.run(host="0.0.0.0", port=5000)
