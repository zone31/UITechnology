#include<LiquidCrystal.h>
LiquidCrystal lcd(12, 11, 5, 4, 3, 2);
//-------------------Sampling configuration variables--------------
// Amounts of samples taken for smooting
int samplesize = 15;
// Screen and data refreshrate
int refreshPerSecond = 40;
//-------------------Sensor configuration variables--------------
// Amount of sensors connected
int sensorCount = 5;
// Sensor names comma seperated in one string
String sensorNames = "Breathing,Top,Bottom,Left,Right,A5";
String sensorRanges = "0,1023|0,1023|0,1023|0,1023|0,1023|0,1023";
// Sample pointer, for current scope
int samplePointer = 0;
// The sample array
int* samples;
// The total value in array
int* res;
//-------------------Data polling variables-----------------------
// Data polling amount
int dataPollingInterval = 1;
// set up if we want the polling rate to increase dynamically
bool dynamicPolling = true;
// Dynamic range max and min
int dynamicRangeMin = 5;
int dynamicRangeMax = 10;
// Global latency for a iteraiton
int latency = 5;
//-------------------Display variables----------------------------
// Size of raw sensor data when written
int strSize = 5;
bool enableScreen = false;

void setup()
{
    delay(100);
    setupBuffers();
    Serial.begin(115200);
    while(Serial.available() == 0){}
    Serial.println ("INIT");
    sendInitialData();
    // Set the analog refference to external usage
    analogReference(AR_EXTERNAL);
    // Set the relevant pins to pullup mode, and print them
    for( int s = 0; s < sensorCount; s++) {
        //pinMode(A0+s, INPUT_PULLUP);
        //pinMode(A0+s, INPUT);
    }
    // set up the LCD's number of columns and rows:
    lcd.begin(16, 2);
}

void sendInitialData(){
     Serial.print("args:");
     Serial.println(5);
     Serial.print("fps:");
     Serial.println(refreshPerSecond);
     Serial.print("sensors:");
     Serial.println(sensorCount);
     Serial.print("sensorNames:");
     Serial.println(sensorNames);
     Serial.print("samplesize:");
     Serial.println(samplesize);
     Serial.print("sensorRanges:");
     Serial.println(sensorRanges);
}


// Allocate the needed space for the result buffer and the save buffer
void setupBuffers(){
    res = (int*) calloc(sensorCount,  sizeof *res);
    samples =  (int*) calloc( sensorCount * samplesize,  sizeof *samples);
}


void printLCD(){
    for( int s = 0; s < sensorCount && enableScreen; s++) {
        int line = 0;
        int row = s;
        if (s>2) {
            line = 1;
            row = s - 3;
        }
        lcd.setCursor(row*strSize, line);
        lcd.print(char(65+s));
        lcd.print("    ");
        lcd.setCursor(row*strSize+1, line);
        lcd.print(res[s]/samplesize);
    }
}


// Pull all sensors once
void getSensorData(){
    for( int s = 0; s < sensorCount; s++ ) {
        // subtract the last reading:
        res[s] = res[s] - (samples[s + samplePointer*sensorCount]);
        // read from the sensor:
        samples[s + samplePointer*sensorCount] = analogRead(A0 + s); //To get right sensor
        // add the reading to the total:

        res[s] = res[s] + (samples[s + samplePointer*sensorCount]);

        // delay in between reads for stability
        delay(2);
    }
    // advance to the next position in the array:
    samplePointer++;
    // if we're at the end of the array...
    if (samplePointer >= samplesize) {
        // ...wrap around to the beginning:
        samplePointer = 0;
    }
}

// Increases or decreases the dynamic polling based on min and max values
void calculateDynamicPolling(){
    if(latency > dynamicRangeMax && dynamicPolling){
        dataPollingInterval++;
    }else{
        if (latency < dynamicRangeMin && dataPollingInterval > 0 && dynamicPolling){
            dataPollingInterval--;
        }
    }
}

// Send the data over serial
void sendSensorData(){
    Serial.print(latency);
    Serial.print(",");
    Serial.print(dataPollingInterval);
    Serial.print(",");
    for( int s = 0; s < sensorCount; s++) {
        Serial.print(res[s]/samplesize);
        if (s+1 < sensorCount){
            Serial.print(",");
        }
     }
     Serial.println();
}

void loop(){

    // Start counter, so we dynamically can set the polling interval
    int starttime = millis();
    // sensor data counter
    int z = 0;

    // Call get sensor data as many times as defined
    do {
        getSensorData();
        z++;
    } while(z < dataPollingInterval);
    //Send screen
    printLCD();
    calculateDynamicPolling();
    sendSensorData();
    // get stop time, so we can count polling rate for next iterration
    int stoptime = millis();
    latency = 1000/refreshPerSecond - (stoptime-starttime);
    //Keep delay between latency
    if(latency>0){
        delay(latency);
    }
}


