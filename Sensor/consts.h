#ifndef CONSTS_H
#define CONSTS_H
#include <Arduino.h>

const int SENSOR_IO = 18; 
const int BAUDRATE = 115200;
const unsigned long DEBOUNCE_DELAY = 50; 
const unsigned long HEARTBEAT_INTERVAL = 5000; // Send a ping every 5 seconds

#endif