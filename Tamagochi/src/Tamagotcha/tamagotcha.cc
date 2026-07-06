#include "tamagotcha.h"

Tamagotcha::Tamagotcha():daysAlive(0),happiness(50),hungriness(50),evolutionStage(0){
    startLifeTime();
}

void Tamagotcha::startLifeTime(){
    loadState();
    checkBehaviourState();
}

void Tamagotcha::update(unsigned long time){
    // Add to timeSinceDay
    // Check if daysAlive needs to increase
    timeSinceDay += time;
    if (timeSinceDay >= 86400000){ // If longer than a day
        daysAlive += 1;
        timeSinceDay -= 86400000;
    }
    // Add time to decay time. This time we can reset at any time
    timeSinceDecay += time;
    decay();

    checkBehaviourState();
    saveState();
}

void Tamagotcha::feed(){
    // Call function when feed button is pressed
    if(hungriness <= 81){hungriness += 20;} 
    else{hungriness = 100;}
    saveState();

}

void Tamagotcha::play(){
    // Call this function when play button is pressed
    if(happiness <= 50){happiness += 50;}
    else{happiness = 100;}
    saveState();
}

void Tamagotcha::evolve(){
    // Add code to switch to new pokemon stage
    evolutionStage += 1;
    saveState();
}

Behaviour Tamagotcha::getBehaviour(){
    return currentBehaviour;
}

void Tamagotcha::loadState(){
    // Load data already saved or use normal data
    savedData.begin("Tamagotcha", false);
    timeSinceDay = savedData.getInt("timeSinceDay", 0);
    timeSinceDecay = savedData.getInt("timeSinceDecay", 0);
    daysAlive = savedData.getInt("daysAlive", 0);
    hungriness = savedData.getInt("hungriness", 50);
    happiness = savedData.getInt("happiness", 50);
    evolutionStage = savedData.getInt("evoStage", 0);
    savedData.end();
}

void Tamagotcha::saveState(){
    // Save data to preserved storage
    savedData.begin("Tamagotcha", false);
    savedData.putInt("timeSinceDay", timeSinceDay);
    savedData.putInt("timeSinceDecay", timeSinceDecay);
    savedData.putInt("daysAlive", daysAlive);
    savedData.putInt("hungriness", hungriness);
    savedData.putInt("happiness", happiness);
    savedData.putInt("evoStage", evolutionStage);
    savedData.end();
}

void Tamagotcha::checkBehaviourState(){
    if(daysAlive >= firstEvolutionLevel && evolutionStage == 0){
        currentBehaviour = Evolve;
        return;
    }
    else if(daysAlive >= secondEvolutionLevel && evolutionStage == 1){
        currentBehaviour = Evolve;
        return;
    }
    if(hungriness < 20){
        currentBehaviour = Hungry;
        return;
    }
    if(happiness > 70){
        currentBehaviour = Excited;
        return;
    }
    currentBehaviour = Neutral;
}

void Tamagotcha::decay(){
    // Check if enough time has passed since last decay to decay again
    while (timeSinceDecay >= happinessTimeDecay){
        // Reset timedecay to represent that a decay has happened
        timeSinceDecay -= happinessTimeDecay;
        // If happiness can be lowered decay by set value
        if (happiness >= happinessDecay){
            happiness -= happinessDecay;
        } else {happiness = 0;}
    }
    // Check if enough time has passed since last decay to decay again
    while (timeSinceDecay >= hungrinessTimeDecay){
        // Reset timedecay to represent that a decay has happened
        timeSinceDecay -= hungrinessTimeDecay;
        // If happiness can be lowered decay by set value
        if (hungriness >= hungrinessDecay){
            hungriness -= hungrinessDecay;
        } else {hungriness = 0;}
    }
}