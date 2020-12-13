///////////////////////////////////////////////////////////////
// Script:   Rover_2_joystick_controller.ino       
// Description: This file allows directional input to be sent to the
//        IoT vehicle sensing platform. This file also allows sensor
//        data from the IoT vehicle sensing platform to be received
//        and printed in a serial window.
//        
//        
//        
//                                                            
// Authors:  Kevin Rivera                                     
// Creation Date:  11.23.20 v1.0                              
///////////////////////////////////////////////////////////////

//////////////////////////////////////Libraries//////////////////////////////////////////

#include <SoftwareSerial.h>


//////////////////////////////////////Variables//////////////////////////////////////////

SoftwareSerial XBee(2, 3); // RX, TX
String a = "";
char input = ' ';
float xval = 0;
float yval = 0;
const int joystickPin = 2;


//////////////////////////////////////Functions//////////////////////////////////////////

void setup()
{

  XBee.begin(9600);
  Serial.begin(9600);
  pinMode(joystickPin, INPUT);
}

void loop()
{
  xval = analogRead(A0);
  yval = analogRead(A1);
  if (xval == 0){
    XBee.write('a');
  }
  else if (xval == 1023){
    XBee.write('d');
  }
  else if (yval == 0){
    XBee.write('w');
  }
  else if (yval == 1023){
    XBee.write('s');
  }
  else if (digitalRead(joystickPin) == LOW){
    XBee.write('q');
  }
  else{}
  if (XBee.available())
  {
    a = XBee.readString();
    Serial.println(a);
  }
  
}
