//INPUT_PULLUP sets a high-ohm resistor between Analog Input and VCC

void setup()
{
    Serial.begin(9600);
    pinMode(A0, INPUT_PULLUP);   // current flows
    
    
}
float res = 0;
int samplerate = 10;

void loop()
{
    for( int i = 0; i < samplerate; i = i + 1 ) {
         res += analogRead(A0)/samplerate;
         //Serial.println(i);
    }
    Serial.println(res);
    //Serial.print(",");
    //Serial.println(analogRead(A0));
    res = 0;
    delay(200);
}
