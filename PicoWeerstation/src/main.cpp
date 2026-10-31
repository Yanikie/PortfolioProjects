#include <Arduino.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <Wire.h>
#include <Adafruit_BMP280.h>

#include "secrets.h"

// -------- Config --------
const unsigned long intervalForPosting = 60000; // ms, so one reading per minute
const unsigned long wifiTimeout = 20000; // ms before giving up on a connection attempt
const uint8_t bmpAddress = 0x76; // I2C address
const char*api = "https://www.hogetoorn.com/api/sensor.php";
Adafruit_BMP280 bmp; // SDA = GP4, SCL = GP5

// -------- State --------
bool sensorsReady = false;
unsigned long timeSinceLastPost = 0;

// -------- Data --------
struct Reading { // Struct so all data is easily accessable
  float temperature;
  float pressure;
  float humidity;
};


// -------- Sensors --------
bool startSensors() {
  if (!bmp.begin(bmpAddress)) {
    Serial.println("BMP280 not found!");
    return false;
  }
  bmp.setSampling(Adafruit_BMP280::MODE_NORMAL,
                  Adafruit_BMP280::SAMPLING_X2, // temperature
                  Adafruit_BMP280::SAMPLING_X16, // pressure
                  Adafruit_BMP280::FILTER_X16,
                  Adafruit_BMP280::STANDBY_MS_500);
  return true;
}

Reading readSensors() {
  Reading reading;
  reading.temperature = bmp.readTemperature();
  reading.pressure = bmp.readPressure() / 100.0F; // Pa → hPa
  reading.humidity = 0; // No humidity sensor yet, server only accepts 0-100
  return reading;
}

// -------- WiFi --------
bool connectToWifi() { // Returns false when wifiTimeout
  Serial.print("Connecting to WiFi");
  WiFi.begin(networkSSID, networkPass);
  unsigned long start = millis();
  while (WiFi.status() != WL_CONNECTED) {
    if (millis() - start >= wifiTimeout) {
      Serial.println("\nWiFi failed, retrying later");
      return false;
    }
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected: " + WiFi.localIP().toString());
  return true;
}

// -------- Communication --------
void postReading(const Reading& reading) {
  WiFiClientSecure client;
  HTTPClient http;

  client.setInsecure(); // skip certificate verification
  http.begin(client, api);
  http.addHeader("Content-Type", "application/json");
  http.addHeader("X-API-Key", apiKey); // defined in secrets.h

  String body = "{\"temperature\":" + String(reading.temperature, 1)
              + ",\"humidity\":" + String(reading.humidity, 1)
              + ",\"pressure\":" + String(reading.pressure, 2) + "}";

  Serial.println("Posting: " + body);
  int httpCode = http.POST(body);
  Serial.println("Response: " + String(httpCode));

  if (httpCode > 0) {
    Serial.println(http.getString());
  }

  http.end();
}

// -------- Main --------
void setup(){
  Serial.begin(115200);
  Wire.begin();
  sensorsReady = startSensors();
  connectToWifi();
  timeSinceLastPost = millis() - intervalForPosting; // Post right away instead of after a minute
}

void loop() {
  if (millis() - timeSinceLastPost < intervalForPosting) return;
  timeSinceLastPost = millis();
  if (!sensorsReady) {
    sensorsReady = startSensors();
    if (!sensorsReady) return;
  }
  Reading reading = readSensors();

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi lost, reconnecting...");
    if (!connectToWifi()) return;
  }

  postReading(reading);
}