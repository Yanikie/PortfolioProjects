#include <Arduino.h>
#include <DHT.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <WiFiClient.h>
#include <Adafruit_BMP280.h>
#include <Wire.h>

#include "secrets.h"

const int dhtPin = 2;
const int intervalForPosting = 60000; // This gets implemented as a ms count so this takes 1m
const char* api = "https://www.hogetoorn.com/api/sensor.php";
int timeSinceLastPost = 0;

DHT dhtSensor(dhtPin, DHT11);
Adafruit_BMP280 bmp;
WiFiClient courier;

void connectToWifi(){
  WiFi.begin(networkSSID,networkPass);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.println("\nConnected: " + WiFi.localIP().toString());
}

void postReading(float temperature, float humidity, float pressure) {
  WiFiClientSecure client;
  HTTPClient http;

  client.setInsecure();   // skip certificate verification
  http.begin(client, api);
  http.addHeader("Content-Type", "application/json");
  http.addHeader("X-API-Key", apiKey);   // defined in secrets.h

  String body = "{\"temperature\":" + String(temperature, 1)
              + ",\"humidity\":"    + String(humidity, 1)
              + ",\"pressure\":"    + String(pressure, 2)
              + "}";

  Serial.println("Posting: " + body);
  int httpCode = http.POST(body);
  Serial.println("Response: " + String(httpCode));

  if (httpCode > 0) {
    Serial.println(http.getString());
  }

  http.end();
}


void setup(){
  Serial.begin(115200);
  Wire.begin();
  connectToWifi();
  bmp.begin(0x76);
  dhtSensor.begin();
  bmp.setSampling(Adafruit_BMP280::MODE_NORMAL,
                  Adafruit_BMP280::SAMPLING_X2,   // temperature
                  Adafruit_BMP280::SAMPLING_X16,  // pressure
                  Adafruit_BMP280::FILTER_X16,
                  Adafruit_BMP280::STANDBY_MS_500);
  delay(100);
}

void loop(){
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi lost, reconnecting...");
    connectToWifi();
  }
  if (millis() - timeSinceLastPost >= intervalForPosting) {
    timeSinceLastPost = millis();

    float humidity    = dhtSensor.readHumidity();
    float temperature = dhtSensor.readTemperature();
    float pressure    = bmp.readPressure() / 100.0F;  // Pa → hPa

    Serial.print(humidity);
    Serial.print(" ");
    Serial.print(temperature);
    Serial.print(" ");
    Serial.println(pressure);
    if (isnan(temperature) || isnan(humidity)) {
      Serial.println("DHT11 read failed, skipping");
      return;
    }

    postReading(temperature, humidity, pressure);
  }
}