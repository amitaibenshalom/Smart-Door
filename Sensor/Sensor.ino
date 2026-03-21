#include <Arduino.h>
#include "consts.h"

String lastStatus = "";
unsigned long lastDebounceTime = 0;
unsigned long lastHeartbeatTime = 0;
int lastSensorState = LOW;

void setup() {
  Serial.begin(BAUDRATE);
  pinMode(SENSOR_IO, INPUT_PULLUP);
  
  int sensorValue = digitalRead(SENSOR_IO);
  lastStatus = (sensorValue == HIGH) ? "open" : "close";
}

void loop() {
  unsigned long currentMillis = millis();

  // --- Heartbeat Logic ---
  if (currentMillis - lastHeartbeatTime >= HEARTBEAT_INTERVAL) {
    Serial.println("ping");
    lastHeartbeatTime = currentMillis;
  }

  // --- Sensor Logic ---
  int reading = digitalRead(SENSOR_IO);

  if (reading != lastSensorState) {
    lastDebounceTime = currentMillis;
  }

  if ((currentMillis - lastDebounceTime) > DEBOUNCE_DELAY) {
    String currentStatus = (reading == HIGH) ? "open" : "close";
    
    if (currentStatus != lastStatus) {
      Serial.println(currentStatus);
      lastStatus = currentStatus;
    }
  }

  lastSensorState = reading;
}