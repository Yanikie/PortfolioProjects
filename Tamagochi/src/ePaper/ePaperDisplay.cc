#include "ePaperDisplay.h"
#include "bitmap.h"

ePaper::ePaper(const int baudrate)
    : baudRateSerialPort(baudrate),
      display(GxEPD2_290_C90c(ePaperCS, ePaperDC, ePaperRST, ePaperBusy)){
    startDisplay();
}

void ePaper::startDisplay() {
    SPIClass spi(FSPI);
    // Start display
    display.init(baudRateSerialPort, true, 2, false);
    // Reset SPI connection as this is necessary with the esp32 s3
    SPI.end();
    SPI.begin(ePaperSCK, -1, ePaperMosi, ePaperCS);
    // Rotate screen to use landscape mode
    // Topleft (0,0) bottomright (296,128)
    display.setRotation(1);
}

void ePaper::showPokemon() {
    display.setFullWindow();
    display.firstPage();
    do {
        display.fillScreen(GxEPD_WHITE);

        int widthMargin  = (display.width()  - bitmapWidth)  / 2;
        int heightMargin = display.height() - bitmapHeight;
        display.drawBitmap(widthMargin, heightMargin, stage0, bitmapWidth, bitmapHeight, GxEPD_BLACK);
    } while (display.nextPage());

    display.hibernate();
}

void ePaper::showNeutral(){
    display.setFullWindow();
    display.firstPage();
    do {
        display.fillScreen(GxEPD_WHITE);
        display.setCursor(0, 0);
        display.print("The pokemon is neutral");
    } while (display.nextPage());
    display.hibernate();
}

void ePaper::showHungry(){
    display.setFullWindow();
    display.firstPage();
    do {
        display.fillScreen(GxEPD_WHITE);
        display.setCursor(0, 0);
        display.print("The pokemon is Hungry");
    } while (display.nextPage());
    display.hibernate();
}

void ePaper::showExcited(){
    display.setFullWindow();
    display.firstPage();
    do {
        display.fillScreen(GxEPD_WHITE);
        display.setCursor(0, 0);
        display.print("The pokemon is Excited");
    } while (display.nextPage());
    display.hibernate();
}

void ePaper::showEvolve(){
    display.setFullWindow();
    display.firstPage();
    do {
        display.fillScreen(GxEPD_WHITE);
        display.setCursor(0, 0);
        display.print("The pokemon is Evolve");
    } while (display.nextPage());
    display.hibernate();
}