#pragma once
#include <Arduino.h>
#include <Preferences.h>

enum Behaviour{
    Neutral,Hungry,Excited,Evolve
};

class Tamagotcha{
public:
    Tamagotcha();
    void startLifeTime();
    void update(unsigned long time);
    void feed();
    void play();
    void evolve();
    Behaviour getBehaviour();
private:
    Preferences savedData;

    unsigned long timeSinceDay; // In milliseconds
    unsigned long timeSinceDecay; // In milliseconds

    int daysAlive;
    int happiness;
    int hungriness;
    int evolutionStage;

    const uint8_t firstEvolutionLevel = 16;
    const uint8_t secondEvolutionLevel = 32;

    const unsigned long happinessTimeDecay = 1800000; // 30 minutes in ms
    const unsigned long hungrinessTimeDecay = 1800000; // 30 minutes in ms
    const uint8_t happinessDecay = 15;
    const uint8_t hungrinessDecay = 10;
    Behaviour currentBehaviour;

    void loadState();
    void saveState();
    void checkBehaviourState();
    void decay();
};