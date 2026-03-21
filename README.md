
# 🚪 Smart Door Monitor (Anti-Tzuf)

An IoT solution for real-time door state monitoring. This project uses an **Arduino Nano** with a magnetic reed sensor to detect door activity and a **Raspberry Pi** to host a Flask web dashboard and send instant WhatsApp notifications via CallMeBot API.

## **🌐 Live Demo:** [https://amitaibenshalom.com](https://amitaibenshalom.com)

---

> **🔌 Compatibility Note:** > You can use **any Arduino-compatible device** that supports serial communication (Arduino Uno, Nano, Mega, ESP8266, ESP32, etc.) for the sensor node. Similarly, the server can be hosted on any device capable of running Python (Raspberry Pi, old laptop, desktop).

---

## 🐕 Why "Anti-Tzuf"?

The project is named after my puppy, **Tzuf** (צוף). 

The motivation was simple: whenever my bedroom door is left open, Tzuf takes the opportunity to head inside and cause absolute chaos. To prevent my room from being turned upside down, I built this monitor to give me a real-time "early warning system". Now, I get an instant notification the second the door is breached, allowing me to intervene before the mess happens.

<p align="center">
  <img src="pictures/tzuf01.jpg" width="50%" title="Tzuf">
  <br>
  <i>Tzuf: The reason this project exists.</i>
</p>

---

## 🚀 Features
* **Real-time Dashboard:** A sleek web interface with live duration timers.
* **Intelligent Notifications:** Instant WhatsApp alerts via CallMeBot API.
* **Anti-Spam Logic:** Configurable cooldowns to prevent notification spam.
* **Resilient Connectivity:** Auto-reconnecting serial logic.

---

## 🛠 Tech Stack
* **Hardware:** Arduino Nano (or any other Arduino Microcontroller with serial communication support), Magnetic Reed Switch.
* **Backend:** Python 3, Flask, PySerial.
* **Frontend:** HTML5, CSS3 (Variables), JavaScript (Vanilla).
* **Communication:** USB Serial (UART), CallMeBot WhatsApp API.

---

## 📂 Project Structure
```text
.
├── Sensor/
│   ├── Sensor.ino       # Arduino Microcontroller Firmware
│   └── consts.h         # Hardware constants
└── Server/
    ├── app.py           # Main Flask server & Serial listener
    ├── config.py        # Centralized system configuration
    ├── whatsapp.py      # WhatsApp API integration
    ├── templates/       # Dashboard UI
    ├── .env.example     # Template for environment secrets
    └── requirements.txt # Python dependencies
````

-----

## 🔧 Setup & Installation

### 1\. Hardware Setup

1.  Flash the `Sensor.ino` to your microcontroller .
2.  Connect the magnetic reed sensor to the pins defined in `consts.h`.
3.  Connect the microcontroller to your Raspberry Pi (or other host) via USB.

### 2\. Server Configuration

1. Clone the repo and install dependencies:

```bash
git clone https://github.com/amitaibenshalom/Smart-Door.git
cd Smart-Door
pip install -r Server/requirements.txt
```

2. Set up [CallMeBot WhatsApp API](https://www.callmebot.com/blog/free-api-whatsapp-messages/) and get your API_KEY.

3. Set up your environment variables:

```bash
cp Server/.env.example Server/.env
nano Server/.env
```

*Add your `PHONE_NUMBER` and CallMeBot `API_KEY` to the `.env` file.*

### 3\. Running as a Service (optional)

To ensure the monitor starts automatically on boot:

1.  Copy `Server/door.service` to `/etc/systemd/system/`.
2.  Update the `user/group` and `ExecStart` path in the file to match your project location.
3.  Run:


```bash
sudo systemctl daemon-reload
sudo systemctl enable door.service
sudo systemctl start door.service
```

-----

## 🛡 Anti-Spam Logic

The system is designed to handle "noisy" sensors. If the door state changes more than `SPAM_MAX_MESSAGES` times within `SPAM_WINDOW_SECONDS`, the system will:

1.  Send a warning notification.
2.  Mute further alerts until the activity settles.
3.  Automatically resume normal operation once the window clears.

-----

## 📧 Contact

**Amitai Ben Shalom** [amitai@amitaibenshalom.com](mailto:amitai@amitaibenshalom.com)  