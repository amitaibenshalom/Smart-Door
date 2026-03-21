from flask import Flask, render_template, jsonify
from datetime import datetime
import threading
import serial
import time
from config import SERIAL_PORT, BAUD_RATE, SPAM_WINDOW_SECONDS, DOMAIN_URL, HEARTBEAT_TIMEOUT, SPAM_MAX_MESSAGES
from whatsapp import send_whatsapp_message

app = Flask(__name__)

# -- STATE STORAGE --
door_state = {
    "status": "closed", 
    "last_change": datetime.now(),
    "last_heartbeat": time.time()
}

change_timestamps = []
spam_warning_sent = False


def is_spamming(current_time):
    global change_timestamps
    change_timestamps = [t for t in change_timestamps if current_time - t < SPAM_WINDOW_SECONDS]
    change_timestamps.append(current_time)
    return len(change_timestamps) >= SPAM_MAX_MESSAGES

def read_serial():
    while True:
        ser = None
        try:
            # Attempt to open the serial port
            ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
            ser.setDTR(False) # Release the ESP32 from reset
            ser.setRTS(False) # Release the ESP32 from bootloader mode
            print(f"SUCCESS: Connected to ESP32 on {SERIAL_PORT}")
            
            # Inner loop: Read data as long as the connection is alive
            while True:
                try:
                    if ser.in_waiting > 0:
                        line = ser.readline().decode('utf-8', errors='ignore').strip()
                        
                        if line == "ping":
                            door_state["last_heartbeat"] = time.time()
                        elif line in ["open", "close"]:
                            handle_door_change(line)
                            door_state["last_heartbeat"] = time.time()
                            
                except serial.SerialException as e:
                    print(f"ERROR: USB connection lost! ({e})")
                    break # Break inner loop to trigger the finally block and reconnect

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

def handle_door_change(new_status):
    global spam_warning_sent
    
    if new_status != door_state["status"]:
        door_state["status"] = new_status
        door_state["last_change"] = datetime.now()
        print(f"Serial Update: Door is now {new_status}")

        now = time.time()
        
        # If we hit 5 changes in 10 seconds...
        if is_spamming(now):
            print("Spamming detected!")
            # Only send the warning ONCE until the spamming stops
            if not spam_warning_sent:
                send_whatsapp_message("*⚠️ Spamming detected! Muting notifications until the door settles.*", force=True)
                spam_warning_sent = True
        
        # Normal behavior
        else:
            spam_warning_sent = False # Reset the mute toggle because the door settled down
            msg = "DOOR OPENED!!!" if new_status == "open" else "Door closed :)"
            send_whatsapp_message(msg, force=False)

@app.route('/')
def dashboard():
    is_connected = (time.time() - door_state["last_heartbeat"]) <= HEARTBEAT_TIMEOUT
    return render_template('index.html', door_state=door_state, is_connected=is_connected)

@app.route('/api/data')
def get_data():
    is_connected = (time.time() - door_state["last_heartbeat"]) <= HEARTBEAT_TIMEOUT
    return jsonify({
        "status": door_state["status"],
        "timestamp": door_state["last_change"].timestamp(),
        "is_connected": is_connected
    })

if __name__ == '__main__':
    threading.Thread(target=read_serial, daemon=True).start()
    send_whatsapp_message(f"*Smart Door Activated!*\n\n{DOMAIN_URL}")
    app.run(host='0.0.0.0', port=5000)