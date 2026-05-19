#include <Arduino.h>
#include <DHT.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <WiFiClient.h>

#include "secrets.h"

const int dhtPin = 2;
DHT dhtSensor(dhtPin, DHT11);

WiFiClient courier;
PubSubClient mug(courier);

void connectToWifi(){
  WiFi.begin(networkSSID,networkPass);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.println("\nConnected: " + WiFi.localIP().toString());
}

void connectMQTT(){
  Serial.print("Mosquitto connecting");
  while(!mug.connected()){
    Serial.print('.');
    String clientId = "PicoW_" + String(random(0xffff), HEX); // Add random suffix to avoid conflicts
    if(mug.connect(clientId.c_str())){Serial.println("Succes");}
    else {
      Serial.print(" Failed, rc=");
      Serial.print(mug.state()); // Print the error code
      Serial.println(" retrying in 2 seconds");
      delay(2000); // Wait before retrying
    }
  }
}

void setup(){
  Serial.begin(115200);
  connectToWifi();
  mug.setServer(serverIP, 1883);
  mug.setCallback(NULL); // Optional: for receiving messages

  dhtSensor.begin();
  delay(1000);
}

void loop(){
  if (!mug.connected()){connectMQTT();}
  mug.loop();
  float humidity = dhtSensor.readHumidity();
  float temperature = dhtSensor.readTemperature();

  if (!isnan(temperature) && !isnan(humidity)) {
    String message = "{\"temperature\":" + String(temperature,1) + ",\"humidity\":" + String(humidity,1) + "}";
    mug.publish("Dashboard/PicoW", message.c_str());
  }
  delay(1000);
}