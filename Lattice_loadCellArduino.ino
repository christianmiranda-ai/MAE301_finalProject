# the following is code meant to later interface (if needed) an Amazon-sourced load cell with an HX711 load cell amplifier
#include "HX711.h"
#define DOUT 2  // Data pin to Mega 2560
#define CLK  3  // Clock pin to Mega 2560
HX711 scale;
float calibration_factor = -7050; // Adjust after testing with a known weight

void setup() {
  Serial.begin(9600);
  scale.begin(DOUT, CLK);
  scale.set_scale(calibration_factor);
  scale.tare(); // Zero out initial reading
  Serial.println("Time (ms),Force (kg)"); // CSV header
}

void loop() {
  float force = scale.get_units(); // Reads in kg
  unsigned long time = millis();   // Time in milliseconds
  Serial.print(time);
  Serial.print(",");
  Serial.println(force);
  delay(500); // Update every 0.5s
}
