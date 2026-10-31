# PicoWeerstation
Weather station built on a Raspberry Pi Pico W. Every minute it measures the temperature and air pressure and posts them to my website, where they are shown on a dashboard.

# Hardware

| Part | Role |
|---|---|
| Raspberry Pi Pico W | Sensor node with WiFi |
| BMP280 | Temperature and air pressure (I2C) |

### BMP280 wiring

```
BMP280    →    Pico W
─────────────────────────
VCC       →    3.3V  (pin 36)
GND       →    GND   (pin 38)
SCL       →    GP5   (pin 7)
SDA       →    GP4   (pin 6)
CSB       →    3.3V  (selects I2C instead of SPI)
SDO       →    GND   (sets the I2C address to 0x76)
```

# Setup
1. Open the folder in VS Code with the PlatformIO extension
2. Create `include/secrets.h` (not in git):
   ```cpp
   #define networkSSID "..."
   #define networkPass "..."
   #define apiKey "..."
   ```
3. Close the serial monitor and press **Upload**. PlatformIO resets the Pico into BOOTSEL by itself and copies the firmware to the `RPI-RP2` drive, so no button press is needed.
4. Open the serial monitor at **115200** baud.

# How it works
1. `setup()` starts the sensor and connects to WiFi
2. Every 60 seconds `loop()` reads the sensor and posts a JSON message to `https://www.hogetoorn.com/api/sensor.php`:
   ```json
   {"temperature":21.8,"humidity":0.0,"pressure":1031.80}
   ```
3. The server checks the `X-API-Key` header, stores the reading and keeps 7 days of data
4. When WiFi or the sensor drops out, the Pico retries on the next interval instead of hanging

# Expand
- SCD40/41 for CO2 
- SHT40 for Humidity
- BH1750 for Light 

- OTA updates
- Push notifications

- Tamagotchi project integration