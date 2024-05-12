float angle = 0; // keeps track of motor angle relative to initial shaft direction
float microstep = 1.0;
float num_steps = 200;
int delay = 500; // time before next step / 2

void setup() {
  pinMode(2, OUTPUT);
  pinMode(3, OUTPUT);
  pinMode(4, OUTPUT);
  pinMode(5, OUTPUT);
  pinMode(6, OUTPUT); // STBY

  digitalWrite(6, LOW);

  digitalWrite(2, LOW);
  digitalWrite(3, LOW);
  digitalWrite(4, LOW);
  digitalWrite(5, LOW);

  digitalWrite(6, HIGH);

  Serial.begin(9600);
}

void loop() {
  for (int count = 0; count < num_steps/microstep; count++){
    //taking a step
    digitalWrite(4, HIGH);
    delay(500);
    digitalWrite(4, LOW);
    delay(500);
    //updating angle
    if(digitalRead(5)){
      angle -= 360/num_steps;
    }
    else{
      angle += 1.8/num_steps;
    }
  }
  digitalWrite(5, !digitalRead(5)); // change direction of shaft (so that SMA cable doesn't get tangled)
}
