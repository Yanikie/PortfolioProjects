#include <Arduino.h>
#include "ePaper/ePaperDisplay.h"
#include "Tamagotcha/tamagotcha.h"

// System settings
const int baudRateSerialPort = 115200;

// Used object
ePaper display(baudRateSerialPort);
Tamagotcha pokemon;
// Arduino Template
void setup(){
    Serial.begin(baudRateSerialPort);
    delay(1000);     // Wait till Serial port has been configured
    display.showPokemon();
}

void loop(){
    unsigned long time = millis();
    Behaviour pokemonBehaviour = pokemon.getBehaviour();
    if (pokemonBehaviour == Neutral){
        Serial.println("Pokemon is Neutral");
        // display.showNeutral();
    } else if (pokemonBehaviour == Hungry){
        Serial.println("Pokemon is Hungry");
        // display.showHungry();
    } else if (pokemonBehaviour == Excited){
        Serial.println("Pokemon is Excited");
        // display.showExcited();
    } else if (pokemonBehaviour == Evolve){
        Serial.println("Pokemon is Evolving");
        // display.showEvolve();
    }
    delay(3000);
 
    unsigned long timedifference = millis() - time;
    pokemon.update(timedifference);
}