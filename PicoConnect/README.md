# Goal of folder
Folder shows how a pico can be deployed to be a sensor node while distributing information to a server.

# Board Properties

| Board | Chip | Role | WiFi |
|---|---|---|---|
| Raspberry Pi Pico W | RP2040 (dual M0+ @ 133 MHz, 264 KB RAM) | Sensor node | Yes |

### DHT11 wiring (confirmed working)

```
DHT11 pin    →    Pico W
─────────────────────────
VCC          →    3.3V (pin 36)
DATA         →    GP2  (pin 4)
GND          →    GND  (pin 38)
```
---

# Project phases

### Phase 1 — Pico W sensor reads 

**Goal:** Confirm the Pico W can read the DHT11 and print valid data.

**Completed steps:**
- PlatformIO project created in VS Code (Arduino framework, `rpipicow` board, Earle Philhower core)
- DHT11 wired to GP2 
- Serial output confirmed: `{"temperature":21.0,"humidity":55.0}`


**Libraries needed (add to `platformio.ini`):**
```ini
lib_deps =
    adafruit/DHT sensor library @ ^1.4.6
    adafruit/Adafruit Unified Sensor @ ^1.1.14
```

---

### Phase 2 — Pico W posts to local server

**Goal:** Replace `Serial.print` with an MQTT publish to a broker server. This proves the full sensor → server data pipeline before anything else is built.

**Steps:**
1. Add WiFi credentials and connect in `setup()`
2. Build a JSON string from the sensor readings
3. Publish the message to the mqtt broker on my server
4. Build the minimal server endpoint that receives and prints the data

---
