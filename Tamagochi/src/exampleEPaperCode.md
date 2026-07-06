#include <Arduino.h>
#include <SPI.h>
#include <GxEPD2_BW.h>
#include <GxEPD2_3C.h>
#include <Fonts/FreeMonoBold9pt7b.h>
#include <Fonts/FreeSans9pt7b.h>
#include <Fonts/FreeSansBold12pt7b.h>

constexpr uint8_t PIN_MOSI = 11;
constexpr uint8_t PIN_SCK  = 12;
constexpr uint8_t PIN_CS   = 10;
constexpr uint8_t PIN_DC   = 7;
constexpr uint8_t PIN_RST  = 6;
constexpr uint8_t PIN_BUSY = 5;

#define ENABLE_GxEPD2_display 0

SPIClass spi(FSPI);

/**
 * MH-ET Live 2.9" e-Paper on ESP32-S3 Supermini
 * ─────────────────────────────────────────────
 * Library: GxEPD2 by ZinggJM
 *
 * The MH-ET Live 2.9" module uses the SSD1680 controller and is compatible
 * with the GxEPD2_290_BS driver (128 × 296 px, black/white).
 *
 * IMPORTANT: The ESP32-S3 Supermini does not expose the default SPI pins on
 * header, so we use Software SPI via GxEPD2. After display.init() we call
 * SPI.end() and SPI.begin() with our custom pin mapping — this is required!
 *
 * Demos in this sketch:
 *   1. Splash screen with centred text
 *   2. Simple shapes & lines
 *   3. A small bitmap logo (XBM format)
 *   4. Partial refresh counter (if the driver supports it)
 */

// ─── Driver selection ────────────────────────────────────────────────────────
// GxEPD2_290_BS  →  DEPG0290BS / SSD1680  (most MH-ET Live 2.9" BW units)
// If your display shows garbage, try GxEPD2_290_T5 or GxEPD2_290_BS.
// Resolution: 128 wide × 296 tall.
GxEPD2_3C<GxEPD2_290_C90c,GxEPD2_290_C90c::HEIGHT> 
    display(GxEPD2_290_C90c(PIN_CS, PIN_DC, PIN_RST, PIN_BUSY));
// ─── Small XBM bitmap (32×32 "Y" logo, generated from a 1-bit image) ────────
// To create your own: open a 32×32 BMP in GIMP → File → Export as → .xbm
// Then paste the uint8_t array here.
static const uint8_t logo_bits[] PROGMEM = {
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
    0x80,0x01,0x80,0x01,0xC0,0x03,0xC0,0x03,
    0xE0,0x07,0xE0,0x07,0xF0,0x0F,0xF0,0x0F,
    0xF8,0x1F,0xF8,0x1F,0xFC,0x3F,0xFC,0x3F,
    0xFE,0x7F,0xFE,0x7F,0xFF,0xFF,0xFF,0xFF,
    0xF0,0x0F,0xF0,0x0F,0xF0,0x0F,0xF0,0x0F,
    0xF0,0x0F,0xF0,0x0F,0xF0,0x0F,0xF0,0x0F,
    0xF0,0x0F,0xF0,0x0F,0x00,0x00,0x00,0x00,
};
static constexpr int LOGO_W = 32, LOGO_H = 32;

// ─── Helpers ─────────────────────────────────────────────────────────────────
static void initDisplay() {
    // 1. Init with baud 115200, full reset, 2 ms RST pulse, no fast partial
    display.init(115200, true, 2, false);

    // 2. Re-map SPI to our custom pins (REQUIRED on S3 Supermini)
    SPI.end();
    SPI.begin(PIN_SCK, -1, PIN_MOSI, PIN_CS);
}

static void centreText(const char* text, int16_t y, const GFXfont* font = nullptr) {
    if (font) display.setFont(font);
    int16_t x1, y1; uint16_t w, h;
    display.getTextBounds(text, 0, 0, &x1, &y1, &w, &h);
    display.setCursor((display.width() - (int16_t)w) / 2 - x1, y);
    display.print(text);
}

// ─── Demo scenes ─────────────────────────────────────────────────────────────

/** Scene 1: splash screen */
static void showSplash() {
    display.setFullWindow();
    display.firstPage();
    do {
        display.fillScreen(GxEPD_WHITE);
        display.setTextColor(GxEPD_BLACK);

        centreText("hogetoorn.com", 55, &FreeSansBold12pt7b);
        centreText("ESP32-S3 Supermini", 90, &FreeSans9pt7b);
        centreText("+ MH-ET Live 2.9\"", 110, &FreeSans9pt7b);
        centreText("E-Paper demo", 135, &FreeSans9pt7b);

        // Horizontal dividers
        display.drawLine(10, 65, 118, 65, GxEPD_BLACK);
        display.drawLine(10, 68, 118, 68, GxEPD_BLACK);
    } while (display.nextPage());
}

/** Scene 2: shapes & lines */
static void showShapes() {
    display.setFullWindow();
    display.firstPage();
    do {
        display.fillScreen(GxEPD_WHITE);
        display.setFont(nullptr);   // default 5×7 bitmap font
        display.setTextColor(GxEPD_BLACK);

        // Border
        display.drawRect(2, 2, display.width() - 4, display.height() - 4, GxEPD_BLACK);

        // Filled & empty rectangles
        display.fillRect(10, 20, 40, 30, GxEPD_BLACK);
        display.drawRect(60, 20, 40, 30, GxEPD_BLACK);

        // Filled & empty circles
        display.fillCircle(20, 80, 16, GxEPD_BLACK);
        display.drawCircle(65, 80, 16, GxEPD_BLACK);

        // Triangle
        display.drawTriangle(10, 120, 50, 100, 90, 120, GxEPD_BLACK);

        // Diagonal lines
        for (int i = 0; i < 5; i++) {
            display.drawLine(0, 140 + i * 10, 128, 140 + i * 10 + 20, GxEPD_BLACK);
        }

        display.setFont(&FreeSans9pt7b);
        centreText("Shapes demo", 210, &FreeSans9pt7b);
        centreText("GxEPD2 on S3", 230, &FreeSans9pt7b);
    } while (display.nextPage());
}

/** Scene 3: XBM bitmap */
static void showBitmap() {
    display.setFullWindow();
    display.firstPage();
    do {
        display.fillScreen(GxEPD_WHITE);
        display.setTextColor(GxEPD_BLACK);

        // Centre the bitmap horizontally, place at y=80
        int16_t bx = (display.width() - LOGO_W) / 2;
        display.drawXBitmap(bx, 80, logo_bits, LOGO_W, LOGO_H, GxEPD_BLACK);

        centreText("XBM bitmap", 145, &FreeSans9pt7b);
        centreText("32 x 32 px", 165, &FreeSans9pt7b);
    } while (display.nextPage());
}

/** Scene 4: partial-refresh counter (if supported by driver) */
static void showCounter(int count) {
    // Use a partial window: just the number area (centre strip)
    uint16_t wx = 0, wy = 120, ww = display.width(), wh = 60;
    display.setPartialWindow(wx, wy, ww, wh);
    display.firstPage();
    do {
        display.fillScreen(GxEPD_WHITE);
        display.setTextColor(GxEPD_BLACK);

        char buf[16];
        snprintf(buf, sizeof(buf), "%d", count);
        centreText(buf, 155, &FreeSansBold12pt7b);
    } while (display.nextPage());
}

// ─── Setup & loop ─────────────────────────────────────────────────────────────
void setup() {
    Serial.begin(115200);
    delay(500);
    Serial.println("[epaper] Starting up...");

    initDisplay();

    // Scene 3 – bitmap
    Serial.println("[epaper] Showing bitmap...");
    showBitmap();
    delay(4000);

    // Put display to sleep — image persists without power!
    Serial.println("[epaper] Hibernating display.");
    display.hibernate();
}

void loop() {
    // Nothing to do — e-paper holds the image without power.
    delay(10000);
}