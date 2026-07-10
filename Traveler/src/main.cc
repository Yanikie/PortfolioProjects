#include <WiFi.h>
#include <DNSServer.h>
#include <WebServer.h>
#include <Preferences.h>

// --- Configuration ---
const char* AP_SSID = "Traveler";
const char* AP_PASSWORD = "";       // empty = open network, easiest for testing
const byte DNS_PORT = 53;

// The ESP32 will always be reachable at this IP in AP mode
IPAddress apIP(192, 168, 4, 1);

DNSServer dnsServer;
WebServer server(80);
Preferences prefs;

// --- Helper: build the page HTML, injecting the current saved tag ---
String buildIndexHtml() {
  String currentTag = prefs.getString("tag", "");

  String html = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Tamagotcha</title>
</head>
<body>
  <h1>Tamagotcha</h1>
  <form action="/tag" method="POST">
    <label for="tag">Today's tag:</label><br>
    <input type="text" id="tag" name="tag" maxlength="40" value="%CURRENT_TAG%">
    <button type="submit">Save</button>
  </form>
</body>
</html>
)rawliteral";

  html.replace("%CURRENT_TAG%", currentTag);
  return html;
}

void handleRoot() {
  server.send(200, "text/html", buildIndexHtml());
}

void handleTagSubmit() {
  if (server.hasArg("tag")) {
    String newTag = server.arg("tag");
    prefs.putString("tag", newTag);
    Serial.print("Saved tag: ");
    Serial.println(newTag);
  }
  // After saving, redirect back to "/" so the page reloads
  // showing the newly saved value (and a fresh empty-vs-filled state)
  server.sendHeader("Location", "/");
  server.send(303); // 303 = "See Other", standard redirect-after-POST pattern
}

// Catch-all: any unknown path also gets the index page.
// This matters because iOS's captive portal check requests
// odd paths/domains — we want ALL of them to land on our page.
void handleNotFound() {
  handleRoot();
}

void setup() {
  Serial.begin(115200);

  prefs.begin("Traveler", false); // "Traveler" = namespace, false = read/write mode
  
  // 1. Start the Access Point
  WiFi.mode(WIFI_AP);
  WiFi.softAP(AP_SSID, AP_PASSWORD);
  WiFi.softAPConfig(apIP, apIP, IPAddress(255, 255, 255, 0));

  Serial.print("AP started, IP = ");
  Serial.println(WiFi.softAPIP());

  // 2. Start DNS server: answer every query with our own IP
  dnsServer.start(DNS_PORT, "*", apIP);

  // 3. Register web routes
  server.on("/", HTTP_GET, handleRoot);
  server.on("/tag", HTTP_POST, handleTagSubmit);
  server.onNotFound(handleNotFound);
  server.begin();
}

void loop() {
  dnsServer.processNextRequest();   // must be called repeatedly
  server.handleClient();            // must be called repeatedly
}