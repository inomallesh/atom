#include <ESP32Servo.h>

Servo l_pitch_servo;
Servo l_roll_servo;
Servo l_elbow_servo;

Servo r_pitch_servo;
Servo r_roll_servo;
Servo r_elbow_servo;

String data = "";

void setup() {
  Serial.begin(115200);

  l_pitch_servo.attach(13);
  l_roll_servo.attach(12);
  l_elbow_servo.attach(14);

  r_pitch_servo.attach(27);
  r_roll_servo.attach(26);
  r_elbow_servo.attach(25);
}

void loop() {
  if (Serial.available()) {
    data = Serial.readStringUntil('\n');

    int values[6];
    int index = 0;

    char *token = strtok((char*)data.c_str(), ",");

    while (token != NULL && index < 6) {
      values[index++] = atoi(token);
      token = strtok(NULL, ",");
    }

    if (index == 6) {
      l_pitch_servo.write(values[0]);
      l_roll_servo.write(values[1]);
      l_elbow_servo.write(values[2]);

      r_pitch_servo.write(values[3]);
      r_roll_servo.write(values[4]);
      r_elbow_servo.write(values[5]);
    }
  }
}