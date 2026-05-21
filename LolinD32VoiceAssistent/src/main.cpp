#include <Arduino.h>
#include "driver/i2s.h"
#include "secrets.h"

// I2S config
// ---------------------
const int i2sWordSelect = 25;
const int i2sBitClock = 26;
const int i2sMicrophoneIn = 33;
const int i2sSpeakerOut = 22;

const int sampleRate = 16000;

// WiFi Config
// ---------------------
const String WiFiName = wifiName;
const String WiFiPass = wifiPass;
const String serverIp = serverIP;

// Using the ESP32 I2S library
// ---------------------
static const i2s_config_t i2sConfig{
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX | I2S_MODE_TX),
    .sample_rate = sampleRate,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,
    .channel_format = I2S_CHANNEL_FMT_RIGHT_LEFT,
    .communication_format = I2S_COMM_FORMAT_I2S,
    .intr_alloc_flags = 0,
    .dma_buf_count = 8,
    .dma_buf_len = 64,
    .tx_desc_auto_clear = true
};
static const i2s_pin_config_t pinConfig = {
    .bck_io_num = i2sBitClock,
    .ws_io_num = i2sWordSelect,
    .data_out_num = i2sSpeakerOut,
    .data_in_num = i2sMicrophoneIn
};
const i2s_port_t i2sPortNumber = I2S_NUM_0;

// State machine
// ---------------------
enum states{Streaming,Listening,Muted};
static states currentState = Listening;

// WiFi config
// ---------------------

// Beep to confirm listening
// ---------------------
// In order to keep the beep from interupting the microphone listening we pregenerate the beep
const int durationInMs = 300;
static int16_t beepBuffer[sampleRate * durationInMs / 1000];
static int  beepSamples = 0;

void generateBeep(){
    int pitch = 523;  // C5 - mellow
    beepSamples = sizeof(beepBuffer) / sizeof(int16_t);
    
    for(int i = 0; i < beepSamples; i++){
        float time = (float)i / sampleRate;
        
        // Gentle Gaussian-like envelope
        float t = time / (durationInMs / 1000.0);
        float env = sinf(t * M_PI);  // Half sine envelope
        
        // Soft clipping for warmth
        float signal = sinf(2.0 * M_PI * pitch * time);
        signal = signal * (1.0 - 0.3 * fabs(signal));  // Softens harshness
        
        beepBuffer[i] = (int16_t)(signal * env * sampleRate * 0.25);
    }
}

void playBeep(){
    size_t written = 0;
    size_t offset  = 0;
    while (offset < beepSamples) {
        size_t toWrite = min((size_t)256, beepSamples - offset);
        i2s_write(i2sPortNumber, &beepBuffer[offset], toWrite * sizeof(int16_t), &written, portMAX_DELAY);
        offset += written / sizeof(int16_t);
    }
    // Brief silence to flush DMA
    int16_t silence[64] = {0};
    i2s_write(i2sPortNumber, silence, sizeof(silence), &written, 100);
}


// Arduino Template
// ---------------------

void setup(){
    Serial.begin(115200);
    i2s_driver_install(i2sPortNumber, &i2sConfig, 0,NULL);
    i2s_set_pin(i2sPortNumber, &pinConfig);
    i2s_zero_dma_buffer(i2sPortNumber);
    // Pregenerate beep. Later only call
    generateBeep();
    Serial.println("Setup was cleared");
}

void loop(){
    playBeep();
    delay(20000);
}