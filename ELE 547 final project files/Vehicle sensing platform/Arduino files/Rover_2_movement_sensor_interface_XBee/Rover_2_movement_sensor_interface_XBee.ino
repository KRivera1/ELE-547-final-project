///////////////////////////////////////////////////////////////
// Script:   Rover_2_movement_sensor_interface_XBee.ino       
// Description: This file allows the collection of humidity data
//        from a DHT11, temperature data from an NTC thermistor,
//        resistance data from a MiCS-5914 and resistance data
//        from a photocell. The data is transmitted wirelessly.
//        The file also is also used to control a Rover V2 tank.
//        Overall sensor data is output and directional inputs
//        are recieved and used to control the vehicle.
//                                                            
// Authors:  Kevin Rivera                                     
// Creation Date:  11.23.20 v1.0                              
///////////////////////////////////////////////////////////////

//Circuit diagrams:
//
//  Thermistor = 
//
//                         A0
//      5V-----thermistor-----resistor-----ground
//    
//      notes: makes sure resistor has a low temperature
//             coefficient to ensure that resistance measurements
//             are accurate for the thermistor.
//
//
//  Photocell = 
//
//                        A1
//      5V-----photocell-----resistor-----ground
//
//
//  MiCS-5914 (Mounted on PCB I designed) = 
//
//                       A2
//      D-----photocell-----resistor-----ground
//		GND---ground
//		VCCG--5V
//		VCCS--5V
//
//
//  DHT11 = 
//
//      S-----digital pin 9
//		GND---ground
//		VCC--5V
//
//
//  HC-SR04 ultrasonic sensor = 
//
//      Trig-----digital pin 10
//		Echo---digital pin 11
//		VCC--5V
//		GND---ground

//////////////////////////////////////Libraries//////////////////////////////////////////

#include <dht.h>
#include <Math.h>
#include <SoftwareSerial.h>
#include <Ticker.h>


//////////////////////////////////////Variables//////////////////////////////////////////


// Vehicle movement specific variables
const int trigPin = 10;						// Ultrasonic sensor trigger pin
const int echoPin = 11;						// Ultrasonic sensor echo pin
const int E1 = 6; 							// Motor 1 Speed Control
const int E2 = 5; 							// Motor 2 Speed Control
const int M1 = 8; 							// Motor 1 Direction Control
const int M2 = 7; 							// Motor 2 Direction Control
int leftspeed = 75;							// Maximum speed that the left motor is allowed to move. 0-255 is the range.
int rightspeed = 75;						// Maximum speed that the right motor is allowed to move. = 0-255 is the range.


// Sensor specific variables
long duration;								// Variable to contain the signal dureation of the ultrasonic sensor
float distance;								// Variable to contain the measured distance by the ultrasonic sensor
const int DHT11_PIN = 9;					// Digital pin connected to the DHT11 module.
float photoRes;								// Variable that will contain the photocell resistance value.
float gasRes;								// Variable that will contain the MiCS-5914 resistance value.
float thermRes;                            	// Variable that will contain the thermistor resistance value.
const float R2 = 980;                      	// R2 resistance in series with the NTC thermistor.
const float R3 = 9900;             			// R3 resistance in series with the photocell.
const float R4 = 93.1;             			// R4 resistance in series with the MiCS-5914.
float T;                                   	// Temperature measured by the thermistor.
char TM[10];                               	// Thermistor data will be stored here.
char PC[10];                 				// Photocell data will be stored here.
char GS[10];                 				// MiCS-5914 data will be stored here.
char HM[10];								// Humidity data will be stored here.
char DATA[100];								// All of the data collected will be stored in this array.

// Miscellaneous variables
char a = ' ';


// Function headers
float thermT(float a);
void sendData();
void stop();
void forward(char a,char b);
void reverse (char a,char b);
void left(char a,char b);
void right(char a,char b);
void movement();



// Objects
dht DHT;
SoftwareSerial XBee(2, 3);
Ticker dataSend(sendData, 5000, 0, MILLIS);


//////////////////////////////////////Functions//////////////////////////////////////////

void setup(){

  //Pin initializations
  pinMode(E1, OUTPUT);
  pinMode(E2, OUTPUT);
  pinMode(M1, OUTPUT);
  pinMode(M2, OUTPUT);
  
  
  XBee.begin(9600);							// Starting the communication with the Xbee.
  Serial.begin(9600);
  dataSend.start();							// Starting the ticker.
}

void loop()
{
  distanceFunc();
  if (distance < 5.0){
    stop();
    reverse(leftspeed,rightspeed);
    while (distance < 5.0){
      distanceFunc();
    }
    stop();
  }
  
  dataSend.update();
  movement();

}

// Function that can convert the thermistor resistance to temperature directly.
float thermT(float a){
	
  T = 1.0 / (0.001129148 + (0.000234125 * log(a)) + (0.0000000876741 * log(a) * log(a) * log(a)));
  T = T - 273.15;                          			// Conversion from Kelvin to Celsius.
  return T;
}

// Function that collects sensor data, converts it to a character array and then
// transmits it wirelessly. (Should be broken up into chunks for possible debugging).
void sendData(){
  
  thermRes=R2*((1023.0 / analogRead(A0)) - 1.0);    // Thermistor resistance measured.
  photoRes=R3*((1023.0 / analogRead(A1)) - 1.0);    // Photocell resistance measured.
  gasRes=R4*((1023.0 / analogRead(A2)) - 1.0);    	// MiCS-5914 resistance measured.
  dtostrf(photoRes, 6, 2, PC);						// Converting photocell resistance value into a char array.
  dtostrf(gasRes, 6, 2, GS);						// Converting the MiCS-5914 resistance value into a char array.
  dtostrf(thermT(thermRes), 6, 2, TM);				// Converting the thermistor temperature value into a char array.
  
  int chk = DHT.read11(DHT11_PIN);					// Collecting the DHT11 sensor readings.
  dtostrf((float)DHT.humidity, 6, 0, HM);			// Converting the DHT11 humidity reading into a char array.
  
  // Concatinating the sensor readings into the DATA char array.
  strcat(DATA, HM);
  strcat(DATA, ",");
  strcat(DATA, TM);
  strcat(DATA, ",");
  strcat(DATA, GS);
  strcat(DATA, ",");
  strcat(DATA, PC);
  
  // Transmitting the contents of the DATA char array wirelessly.
  XBee.write(DATA);
  Serial.println(DATA);
  
  // Clearing the contents of all the arrays before the next loop begins.
  memset(TM, 0, sizeof(TM));
  memset(TM, 0, sizeof(PC));
  memset(TM, 0, sizeof(GS));
  memset(TM, 0, sizeof(HM));
  memset(DATA, 0, sizeof(DATA));
}

// Function to stop the vehicle movement.
void stop(){
	
 digitalWrite(E1,LOW);
 digitalWrite(E2,LOW);
}

// Function to move the vehicle forward.
void forward(char a,char b){
	
 analogWrite (E1,a);
 digitalWrite(M1,LOW);
 analogWrite (E2,b);
 digitalWrite(M2,LOW);
}

// Function to move the vehicle in reverse.
void reverse(char a,char b){
	
 analogWrite (E1,a);
 digitalWrite(M1,HIGH);
 analogWrite (E2,b);
 digitalWrite(M2,HIGH);
}

// Function to turn the vehicle left.
void left(char a,char b){
	
 analogWrite (E1,a);
 digitalWrite(M1,HIGH);
 analogWrite (E2,b);
 digitalWrite(M2,LOW);
}

// Function to turn the vehicle right.
void right(char a,char b){
	
 analogWrite (E1,a);
 digitalWrite(M1,LOW);
 analogWrite (E2,b);
 digitalWrite(M2,HIGH);
}

// Function to determine which direction the vehicle will move.
void movement(){
	
  if (XBee.available()){
	  
    a = XBee.read();
  
    // Forward
    if (a == 'w'){
      forward(leftspeed,rightspeed);
    }
    // Reverse
    else if (a == 's'){
      reverse(leftspeed,rightspeed);
    }
    // Left
    else if (a == 'a'){
      left(leftspeed,rightspeed);
    }
    // Right
    else if (a == 'd'){
      right(leftspeed,rightspeed);
    }
    // Stop
    else{
      stop();
    }
  }
}

// Calculates the distance measured by the ultrasonic sensor.
void distanceFunc(){
  
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  duration = pulseIn(echoPin, HIGH);
  distance = duration * 0.034/2.0;
  
}
