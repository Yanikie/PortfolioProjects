#include <Arduino.h>
#include <WiFi.h>
#include "driver/i2s.h"
#include "secrets.h"

#include <Hey_Porygon_inferencing.h>

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"


// I2S config
// ---------------------
const int i2sWordSelect = 25;
const int i2sBitClock = 26;
const int i2sSpkWordSelect = 19;
const int i2sSpkBitClock = 18;

const int i2sMicrophoneIn = 33;
const int i2sSpeakerOut = 22;

const int sampleRate = 16000;

// WiFi Config
// ---------------------
const String WiFiName = wifiName;
const String WiFiPass = wifiPass;
const String serverIp = serverIP;
const int accessPort = voiceAssistentPort;

// Using the ESP32 I2S library
// ---------------------
static const i2s_config_t i2sSpkConfig{
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_TX),
    .sample_rate = sampleRate,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
    .channel_format = I2S_CHANNEL_FMT_ONLY_RIGHT,
    .communication_format = I2S_COMM_FORMAT_I2S,
    .intr_alloc_flags = 0,
    .dma_buf_count = 8,
    .dma_buf_len = 64,
    .tx_desc_auto_clear = true
};
static const i2s_pin_config_t i2sSpkPins = {
    .bck_io_num = i2sSpkBitClock,
    .ws_io_num = i2sSpkWordSelect,
    .data_out_num = i2sSpeakerOut,
    .data_in_num = I2S_PIN_NO_CHANGE
};

static const i2s_config_t i2sMicConfig = {
    .mode               = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
    .sample_rate        = sampleRate,
    .bits_per_sample    = I2S_BITS_PER_SAMPLE_32BIT,
    .channel_format     = I2S_CHANNEL_FMT_ONLY_RIGHT,   // Mono microphone
    .communication_format = I2S_COMM_FORMAT_I2S,
    .intr_alloc_flags   = 0,
    .dma_buf_count      = 8,
    .dma_buf_len        = 512,
    .tx_desc_auto_clear = false,
    .fixed_mclk         = -1,
};
static const i2s_pin_config_t i2sMicPins = {
    .bck_io_num   = i2sBitClock,
    .ws_io_num    = i2sWordSelect,
    .data_out_num = I2S_PIN_NO_CHANGE,   // Not connected: RX only
    .data_in_num  = i2sMicrophoneIn
};

const i2s_port_t i2sSpkPort = I2S_NUM_0;
const i2s_port_t i2sMicPort = I2S_NUM_1;

// State machine
// ---------------------
enum states{Streaming,Listening,Muted};
static states currentState = Listening;

// WiFi config
// ---------------------
void wifiConnect(){
    WiFi.begin(WiFiName, WiFiPass);
    while (WiFi.status() != WL_CONNECTED) {
        Serial.print("."); delay(500);
    }
    Serial.printf("\n[WiFi] Connected. IP: %s\n", WiFi.localIP());
}

// Beep to confirm listening
// ---------------------
// In order to keep the beep from interupting the microphone listening we pregenerate the beep
static const int durationInMs = 300;
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
        i2s_write(i2sSpkPort, &beepBuffer[offset], toWrite * sizeof(int16_t), &written, portMAX_DELAY);
        offset += written / sizeof(int16_t);
    }
    // Brief silence to flush DMA
    int16_t silence[64] = {0};
    i2s_write(i2sSpkPort, silence, sizeof(silence), &written, 100);
}

// Incoming audio listening
// ---------------------
const int incommingAudioBufferSize = 1024;
uint8_t audioChunkBuf[incommingAudioBufferSize];

bool bytesRead(WiFiClient &client, uint8_t *buf, size_t len){
    size_t index = 0; // Because the amount of bytes is unclear we choose a big int
    while(index < len){
        if(!client.connected()){return false;}
        int available = client.available(); // length of message
        if(available <= 0){continue;}
        int nextToRead = min((size_t)available, len-index); // The next byte
        int received = client.read(buf + index, nextToRead);
        if(received <= 0){return false;}
        index += received;
    }
    return true;
}

uint32_t readChunkSize(WiFiClient &client) {
    // We only want to read 4 bytes since otherwise we get a dram overload
    uint8_t sizeBuf[4];
    if (!bytesRead(client, sizeBuf, 4)) return 0;
    return (uint32_t)sizeBuf[0] | ((uint32_t)sizeBuf[1] << 8)
         | ((uint32_t)sizeBuf[2] << 16) | ((uint32_t)sizeBuf[3] << 24);
}

void playPCMStream(WiFiClient &client, uint32_t size) {
    uint32_t remaining = size;
    while (remaining > 0 && client.connected()) {
        int chunkSize = min((uint32_t)incommingAudioBufferSize, remaining);
        if (!bytesRead(client, audioChunkBuf, chunkSize)) break;
        size_t written;
        i2s_write(i2sSpkPort, audioChunkBuf, chunkSize, &written, portMAX_DELAY);
        remaining -= chunkSize;
    }
}

// Wake Word
// ---------------------
struct inferenceStruct {
    signed short *buffers[2];
    unsigned char bufSelect;
    unsigned char bufReady;
    unsigned int bufCount;
    unsigned int nSamples;
};

static inferenceStruct inference;
static const uint32_t sampleBufferSize = 2048;
static signed short sampleBuffer[sampleBufferSize];
static bool debug_nn = false; // Set this to true to see e.g. features generated from the raw signal
static int processedSlices = -(EI_CLASSIFIER_SLICES_PER_MODEL_WINDOW);
static bool record_status = true;



void audioInferenceCallback(uint32_t numberOfBytes){
    for(int readByte = 0; readByte < (int)numberOfBytes >> 1; readByte ++){
        inference.buffers[inference.bufSelect][inference.bufCount++] = sampleBuffer[readByte];
        if(inference.bufCount >= inference.nSamples){
            inference.bufSelect ^= 1; // Switch using XOR operator to different buffer
            inference.bufCount = 0; // Reset buffer count so next buffer can be filled
            inference.bufReady = 1; // Become 1 when buffer is full
        }
    }
}

void captureSamples(void* arg){
    const int32_t bytesToRead = (uint32_t)arg;
    size_t bytesRead = bytesToRead;

    while (record_status) {
        i2s_read(i2sMicPort, (void *)sampleBuffer, bytesToRead, &bytesRead, 100);

        if (bytesRead <= 0) {ei_printf("I2S read error: %d\n", bytesRead);} 
        else {
            // Read as 32-bit then extract the useful bits
            int32_t *buf32 = (int32_t *)sampleBuffer;
            for(int x = 0; x < (int)(bytesRead / 4); x++){sampleBuffer[x] = (int16_t)(buf32[x] >> 11);}
            if(record_status){audioInferenceCallback(bytesRead/2);}
        }
    }
    // When record_status goes false the task deletes itself cleanly.
    vTaskDelete(NULL);
}

bool microphoneStart(uint32_t samples){
    // Allocate the two ping-pong buffers on the heap
    inference.buffers[0] = (signed short *)malloc(samples * sizeof(signed short));
    if (!inference.buffers[0]) return false;

    inference.buffers[1] = (signed short *)malloc(samples * sizeof(signed short));
    if (!inference.buffers[1]) {
        ei_free(inference.buffers[0]);
        return false;
    }
    inference.bufSelect = 0;
    inference.bufReady = 0;
    inference.bufCount = 0;
    inference.nSamples = samples;
    
    delay(100);

    record_status = true;
    xTaskCreate(captureSamples,"CaptureSamples",1024 * 32,
        (void *)sampleBufferSize,1,NULL);
    return true;
}

// It just waits for the capture task to signal buf_ready.
bool microphoneRecord(void) {
    if (inference.bufReady == 1) {Serial.println("Warning: buffer overrun — inference too slow\n");}
    while (inference.bufReady == 0){delay(1);}
    inference.bufReady = 0;
    return true;
}

// Uses a xor function to turn the right buffer into readable data
int getMicData(size_t offset, size_t length, float *out_ptr) {
    numpy::int16_to_float(&inference.buffers[inference.bufSelect ^ 1][offset],out_ptr,length);
    return 0;
}


// Communication
// ---------------------
const int recordSeconds = 5;
const int recordSamples = sampleRate * recordSeconds;  // 80 000 samples
const int streamChunk   = 128;  // 128 samples × 2 bytes (we use 16 bit mic) = 256 bytes per write

// Sends microphone audio to the server, receives a JSON transcript, then
// reads back server-sent PCM audio chunks and plays them over I2S.
String recordAndStream() {
    WiFiClient client;

    Serial.printf("Connecting to %s:%d\n", serverIp.c_str(), accessPort);
    if(!client.connect(serverIp.c_str(), accessPort)){Serial.println("Connection failed.");return "";}
    Serial.println("Connected. Streaming audio...");

    // Send byte count. This way the server knows how much it needs to wait for
    uint32_t totalBytes = (uint32_t)recordSamples * sizeof(int16_t);
    client.write((uint8_t *)&totalBytes, 4);

    // Now the actual data
    int samplesSent = 0;
    int16_t chunk[streamChunk];
    // As long as bytes to sent
    while (samplesSent < recordSamples) {
        // Wait for the mic to record
        while(inference.bufReady == 0){delay(1);}
        // Immediately resume recording
        inference.bufReady = 0;
        // Read filled buffer
        int src = inference.bufSelect ^ 1;
        int sliceOffset = 0;

        while (sliceOffset < (int)inference.nSamples && samplesSent < recordSamples) {
            int toCopy = min(streamChunk, (int)inference.nSamples - sliceOffset);
            toCopy = min(toCopy, recordSamples - samplesSent);
            memcpy(chunk, &inference.buffers[src][sliceOffset], toCopy * sizeof(int16_t));
            client.write((uint8_t *)chunk, toCopy * sizeof(int16_t));
            sliceOffset += toCopy;
            samplesSent += toCopy;
        }
    }
    Serial.printf("Streamed %d samples. Waiting for response...\n", samplesSent);

    // Wait for reply
    unsigned long t0 = millis();
    while (client.available() == 0) {
        if (millis() - t0 > 15000) {
            Serial.println("Timeout waiting for transcript.");
            client.stop();
            return "";
        }
        delay(10);
    }

    // Read response from server character by character
    String response = "";
    while (client.available()) {
        char c = client.read();
        if (c == '\n') break;
        response += c;
    }
    Serial.printf("Raw response: %s\n", response.c_str());


    // Now we listen to audio sent by server
    while(client.connected() || client.available()) {
        // Wait for the size header
        unsigned long waiting = millis();
        while(client.available() < 4){
            if(!client.connected())goto done_playing;
            if(millis() - waiting > 10000){
                Serial.println("Timeout waiting for audio chunk.");
                goto done_playing;
            }
            delay(5);
        }
        // The last audio byte is an empty byte. This is by design
        uint32_t chunkSize = readChunkSize(client);
        if (chunkSize == 0) {
            Serial.println("End-of-audio marker received.");
            break;
        }
        playPCMStream(client, chunkSize);
    }
    done_playing:

    client.stop();

    // For debugging purposes
    int start = response.indexOf("\"transcript\": \"");
    if (start == -1) { Serial.println("No transcript in response."); return ""; }
    start += 15;
    int end = response.indexOf("\"", start);
    if (end == -1) return "";

    return response.substring(start, end);
}


// Arduino Template
// ---------------------

void setup(){
    Serial.begin(115200);

    // Wifi Config
    wifiConnect();
    // Edge impulse config
    run_classifier_init();

    // Set I2S protocol up
    i2s_driver_install(i2sSpkPort, &i2sSpkConfig, 0,NULL);
    i2s_set_pin(i2sSpkPort, &i2sSpkPins);
    i2s_zero_dma_buffer(i2sSpkPort);
    i2s_driver_install(i2sMicPort, &i2sMicConfig, 0,NULL);
    i2s_set_pin(i2sMicPort, &i2sMicPins);
    i2s_zero_dma_buffer(i2sMicPort);

    // Pregenerate beep. Later only call
    generateBeep();

    // Edge Impulse config
    delay(500);

    if (!microphoneStart(sampleRate / EI_CLASSIFIER_SLICES_PER_MODEL_WINDOW)) {
        ei_printf("ERR: Could not allocate audio buffer (size %d), this could be due to the window length of your model\r\n", EI_CLASSIFIER_RAW_SAMPLE_COUNT);
        return;
    }

    Serial.println("Setup was cleared");
}

void loop(){
    if (!microphoneRecord()) {
        ei_printf("ERR: Failed to record audio\n");
        return;}

    signal_t signal;
    signal.total_length = EI_CLASSIFIER_SLICE_SIZE;
    signal.get_data = &getMicData;

    // Run classifier runs the Edge impulse machine. Continuous makes it none blocking
    ei_impulse_result_t result = {0};
    EI_IMPULSE_ERROR err = run_classifier_continuous(&signal, &result, debug_nn);
    if (err != EI_IMPULSE_OK) {
        ei_printf("Classifier error: %d\n", err);
        return;
    }

    // Only act once we have processed enough slices for a full model window
    if (++processedSlices < 0) return;
    processedSlices = 0;

    // Find the label with the highest score 
    int   bestIndex = 0;
    float bestScore = 0.0f;
    for (size_t i = 0; i < EI_CLASSIFIER_LABEL_COUNT; i++) {
        ei_printf("[%s: %.2f] ",result.classification[i].label,result.classification[i].value);
        if (result.classification[i].value > bestScore) {
            bestScore = result.classification[i].value;
            bestIndex = i;
        }
    }
    Serial.print("\n");

    // My wake word has index 0. If this is the best index it has deemed it to be the wake word
    bool wakeWordDetected = bestIndex == 0;

    if (wakeWordDetected && currentState == Listening) {
        Serial.print("Wake word detected: ");
        currentState = Streaming;
        playBeep();
        String transcript = recordAndStream();
        Serial.printf("Transcript: %s\n", transcript.c_str());
        currentState = Listening;
    }
}