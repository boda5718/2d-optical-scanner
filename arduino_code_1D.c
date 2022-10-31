int pinDir = 10;
int pinStep = 11;
int datafromUser=0;


void setup() {
  Serial.begin(9600);
  pinMode(pinDir,OUTPUT);
  pinMode(pinStep,OUTPUT);
}

void loop() {
   if(Serial.available() > 0)
  {
    datafromUser=Serial.read();
  }
  if(datafromUser == '1')
  {
     Serial.print('0'); 

    digitalWrite(pinDir,HIGH);
    
    //scan each 100/4 steps (6.1mm) 
    //note: we have used a microstepping 1/4
    
    for(int j=0; j<100; j++){  
    digitalWrite(pinStep, HIGH);
    delay(20);
    digitalWrite(pinStep, LOW);
    delay(20);
    Serial.print('0');
    }
    datafromUser=0;
    Serial.print('1'); 
    
  }
 }
 
