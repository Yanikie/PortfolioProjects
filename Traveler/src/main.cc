#include <WiFi.h>
#include <DNSServer.h>
#include <WebServer.h>

// --- Configuration ---
const char* AP_SSID = "Traveler";
const char* AP_PASSWORD = "";       // empty = open network, easiest for testing
const byte DNS_PORT = 53;

// The ESP32 will always be reachable at this IP in AP mode
IPAddress apIP(192, 168, 4, 1);

DNSServer dnsServer;
WebServer server(80);

// Minimal HTML page — plain text, no build tools needed
const char* INDEX_HTML = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Tamagotcha</title>
</head>
<body>
  <h1>Hello from ESP32</h1>
</body>
</html>
)rawliteral";

void handleRoot() {
  server.send(200, "text/html", INDEX_HTML);
}

// Catch-all: any unknown path also gets the index page.
// This matters because iOS's captive portal check requests
// odd paths/domains — we want ALL of them to land on our page.
void handleNotFound() {
  handleRoot();
}

void setup() {
  Serial.begin(115200);

  // 1. Start the Access Point
  WiFi.mode(WIFI_AP);
  WiFi.softAP(AP_SSID, AP_PASSWORD);
  WiFi.softAPConfig(apIP, apIP, IPAddress(255, 255, 255, 0));

  Serial.print("AP started, IP = ");
  Serial.println(WiFi.softAPIP());

  // 2. Start DNS server: answer every query with our own IP
  dnsServer.start(DNS_PORT, "*", apIP);

  // 3. Register web routes
  server.on("/", handleRoot);
  server.onNotFound(handleNotFound);
  server.begin();
}

void loop() {
  dnsServer.processNextRequest();  // must be called repeatedly
  server.handleClient();          // must be called repeatedly
}