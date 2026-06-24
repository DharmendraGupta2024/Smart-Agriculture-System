#define BLYNK_TEMPLATE_ID "TMPLxxxxxx"
#define BLYNK_TEMPLATE_NAME "SmartAgriculture"
#define BLYNK_AUTH_TOKEN "YourAuthToken" // REPLACE THIS!

#include <ESP8266WiFi.h>
#include <BlynkSimpleEsp8266.h>
#include <DHT.h>
#include "crop_model.h"

// Instantiate the Machine Learning Model
Eloquent::ML::Port::RandomForestRegressor edgeModel;

// Wi-Fi Credentials
char ssid[] = "YOUR_WIFI_SSID";
char pass[] = "YOUR_WIFI_PASSWORD";

// --- PUMP RELAYS (3 Fields) ---
#define PUMP_RELAY_1 D1
#define PUMP_RELAY_2 D2
#define PUMP_RELAY_3 D3

// --- MISTIFIER RELAYS (3 Separate Pins as requested) ---
#define MIST_RELAY_1 D5
#define MIST_RELAY_2 D6
#define MIST_RELAY_3 D7

// --- DHT11 SENSOR ---
#define DHTPIN D4
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// Blynk Timer
BlynkTimer timer;

// Global variables
float currentTemp = 0.0;
float currentHum = 0.0;

void checkMistifiers();

void setup() {
  Serial.begin(115200);

  // Initialize Pump Relays (Active LOW)
  pinMode(PUMP_RELAY_1, OUTPUT);
  pinMode(PUMP_RELAY_2, OUTPUT);
  pinMode(PUMP_RELAY_3, OUTPUT);
  digitalWrite(PUMP_RELAY_1, HIGH); // OFF
  digitalWrite(PUMP_RELAY_2, HIGH); // OFF
  digitalWrite(PUMP_RELAY_3, HIGH); // OFF

  // Initialize Mistifier Relays (Active LOW)
  pinMode(MIST_RELAY_1, OUTPUT);
  pinMode(MIST_RELAY_2, OUTPUT);
  pinMode(MIST_RELAY_3, OUTPUT);
  digitalWrite(MIST_RELAY_1, HIGH); // OFF
  digitalWrite(MIST_RELAY_2, HIGH); // OFF
  digitalWrite(MIST_RELAY_3, HIGH); // OFF

  dht.begin();
  Blynk.begin(BLYNK_AUTH_TOKEN, ssid, pass);

  // Set up timer for checking Mistifiers and conditions every 1 second
  timer.setInterval(1000L, checkMistifiers);
  
  Serial.println("NodeMCU Ready. Waiting for Arduino data...");
}

void loop() {
  Blynk.run();
  timer.run();
  
  // Check for incoming Serial data from Arduino
  if (Serial.available() > 0) {
    String incoming = Serial.readStringUntil('\n');
    incoming.trim();
    
    // Parse format: FieldID,CropIndex,SoilMoisture
    // Example: "1,4,45"
    int firstComma = incoming.indexOf(',');
    int secondComma = incoming.lastIndexOf(',');
    
    if (firstComma > 0 && secondComma > firstComma) {
      int fieldId = incoming.substring(0, firstComma).toInt();
      int cropIndex = incoming.substring(firstComma + 1, secondComma).toInt();
      int soilMoisture = incoming.substring(secondComma + 1).toInt();
      
      processFieldData(fieldId, cropIndex, soilMoisture);
    }
  }
}

void checkMistifiers() {
  currentTemp = dht.readTemperature();
  currentHum = dht.readHumidity();
  
  if (isnan(currentTemp) || isnan(currentHum)) {
    return; // Failed to read DHT
  }
  
  // Send Live Temp and Hum to Blynk (Virtual Pins 0 and 1)
  Blynk.virtualWrite(V0, currentTemp);
  Blynk.virtualWrite(V1, currentHum);
  
  // Logic: If Temp > 30, turn on all 3 mistifiers independently.
  if (currentTemp > 30.0) {
    digitalWrite(MIST_RELAY_1, LOW); // ON
    digitalWrite(MIST_RELAY_2, LOW); // ON
    digitalWrite(MIST_RELAY_3, LOW); // ON
    Blynk.virtualWrite(V4, "Mistifiers ON");
  } else {
    digitalWrite(MIST_RELAY_1, HIGH); // OFF
    digitalWrite(MIST_RELAY_2, HIGH); // OFF
    digitalWrite(MIST_RELAY_3, HIGH); // OFF
    Blynk.virtualWrite(V4, "Mistifiers OFF");
  }
}

void processFieldData(int fieldId, int cropIndex, int soilMoisture) {
  // Update Blynk with Soil Moisture
  Blynk.virtualWrite(V2, soilMoisture);
  
  // Create features array for the ML model: [temperature, humidity, crop_id]
  float features[3] = {currentTemp, currentHum, (float)cropIndex};
  
  // Predict Rainfall locally using C++ Edge Model!
  float predictedRainfall = edgeModel.predict(features);
  
  // Prototype Scaling Logic (15cm x 30cm wooden box)
  float area = 0.045; // m2
  float volumeLiters = area * predictedRainfall;
  float volumeMl = volumeLiters * 1000.0;
  
  // PROTOTYPE SCALE FACTOR: Keep pump duration under ~30 seconds for tabletop demo
  float PROTOTYPE_SCALE_FACTOR = 0.33;
  float scaledVolumeMl = volumeMl * PROTOTYPE_SCALE_FACTOR;
  
  // Flow rate = 50 ml/sec
  float flowRate = 50.0;
  float pumpDurationSec = scaledVolumeMl / flowRate;
  
  // Skip if soil is already wet enough (raw analog value <= 400 means Wet)
  if (soilMoisture <= 400) {
    pumpDurationSec = 0;
  }
  
  // Send required duration to Blynk
  Blynk.virtualWrite(V3, pumpDurationSec); 
  
  // Trigger appropriate pump relay
  if (pumpDurationSec > 0) {
    int targetRelay = PUMP_RELAY_1;
    if (fieldId == 2) targetRelay = PUMP_RELAY_2;
    if (fieldId == 3) targetRelay = PUMP_RELAY_3;
    
    digitalWrite(targetRelay, LOW); // ON
    
    // Blocking delay is acceptable for this simple prototype flow
    delay(pumpDurationSec * 1000);  
    
    digitalWrite(targetRelay, HIGH); // OFF
  }
}
