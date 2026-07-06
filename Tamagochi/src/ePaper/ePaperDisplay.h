#pragma once
#include <Arduino.h>
#include <GxEPD2_3C.h>
#include <SPI.h>

class ePaper{
public:
    ePaper(const int baudrate = 115200);
    void showPokemon();
    void showNeutral();
    void showHungry();
    void showExcited();
    void showEvolve();
private:
    // System settings
    const int baudRateSerialPort;

    // E-Paper hardware connection
    const uint8_t ePaperBusy = 5;
    const uint8_t ePaperRST = 6;
    const uint8_t ePaperDC = 7;
    const uint8_t ePaperCS = 10;
    const uint8_t ePaperMosi = 11;
    const uint8_t ePaperSCK = 12;

    const int bitmapWidth = 96;
    const int bitmapHeight = 96;

    // Display object
    GxEPD2_3C<GxEPD2_290_C90c,GxEPD2_290_C90c::HEIGHT> display;
    void startDisplay();
};