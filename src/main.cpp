#include <Arduino.h>
#include<WINBOND.h>


#define CS 10

void setup()
{
    Serial.begin(115200);
    while(!Serial);
    WINBOND winbond;
    winbond.Init(CS);
    Serial.println("STM32");
    Serial.println(winbond.Read_jedec_id());
    winbond.Read(true);
}


void loop()
{

}