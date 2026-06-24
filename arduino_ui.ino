#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <Keypad.h>

// ==========================================
// CONFIGURATION
// ==========================================

// I2C LCD Configuration (address usually 0x27 or 0x3F)
LiquidCrystal_I2C lcd(0x27, 16, 2);

// Keypad Configuration
const byte ROWS = 4;
const byte COLS = 4;
char keys[ROWS][COLS] = {
  {'1','2','3','A'},
  {'4','5','6','B'},
  {'7','8','9','C'},
  {'*','0','#','D'}
};
// Connect keypad ROW1, ROW2, ROW3 and ROW4 to these Arduino pins.
byte rowPins[ROWS] = {9, 8, 7, 6};
// Connect keypad COL1, COL2, COL3 and COL4 to these Arduino pins.
byte colPins[COLS] = {5, 4, 3, 2};

Keypad keypad = Keypad(makeKeymap(keys), rowPins, colPins, ROWS, COLS);

// Soil Moisture Pins
#define SOIL_PIN_1 A0
#define SOIL_PIN_2 A1
#define SOIL_PIN_3 A2

// Variables
const String PASSWORD = "123";
String inputPassword = "";
int selectedField = 0; // 1, 2, or 3
int selectedCropIndex = 0;

// The 8 valid crops from the dataset mapping
String crops[8] = {"Wheat", "Maize", "Rice", "Potato", "Tomato", "Ginger", "Mustard", "Chili"};

enum State {
  ENTER_PASSWORD,
  SELECT_FIELD,
  SELECT_CROP,
  READING_SENSORS,
  SENDING_DATA
};

State currentState = ENTER_PASSWORD;

void setup() {
  Serial.begin(115200); // Communicate with NodeMCU
  
  lcd.init();
  lcd.backlight();
  
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Enter Password:");
  lcd.setCursor(0, 1);
}

void loop() {
  char key = keypad.getKey();

  switch (currentState) {
    case ENTER_PASSWORD:
      if (key) {
        if (key == 'C') { // Clear password
          inputPassword = "";
          lcd.setCursor(0, 1);
          lcd.print("                "); // clear line
          lcd.setCursor(0, 1);
        } else if (key >= '0' && key <= '9') {
          inputPassword += key;
          lcd.print("*");
          
          if (inputPassword.length() == PASSWORD.length()) {
            delay(500);
            if (inputPassword == PASSWORD) {
              currentState = SELECT_FIELD;
              lcd.clear();
              lcd.setCursor(0, 0);
              lcd.print("Password OK!");
              delay(1000);
              
              lcd.clear();
              lcd.setCursor(0, 0);
              lcd.print("Select Field:");
              lcd.setCursor(0, 1);
              lcd.print("1, 2, or 3?");
            } else {
              lcd.clear();
              lcd.setCursor(0, 0);
              lcd.print("Wrong Password!");
              delay(2000);
              inputPassword = "";
              lcd.clear();
              lcd.setCursor(0, 0);
              lcd.print("Enter Password:");
              lcd.setCursor(0, 1);
            }
          }
        }
      }
      break;

    case SELECT_FIELD:
      if (key) {
        if (key == '1' || key == '2' || key == '3') {
          selectedField = key - '0';
          currentState = SELECT_CROP;
          
          lcd.clear();
          lcd.setCursor(0, 0);
          lcd.print("Select Crop:");
          lcd.setCursor(0, 1);
          lcd.print("A:Next C:Confirm");
          delay(1500);
          
          lcd.clear();
          lcd.setCursor(0, 0);
          lcd.print("Crop:");
          lcd.setCursor(0, 1);
          lcd.print(crops[selectedCropIndex]);
        }
      }
      break;

    case SELECT_CROP:
      if (key) {
        if (key == 'A') {
          // Cycle through crops
          selectedCropIndex++;
          if (selectedCropIndex > 7) {
            selectedCropIndex = 0;
          }
          lcd.clear();
          lcd.setCursor(0, 0);
          lcd.print("Crop:");
          lcd.setCursor(0, 1);
          lcd.print(crops[selectedCropIndex]);
        } else if (key == 'C') {
          // Confirm crop
          currentState = READING_SENSORS;
          lcd.clear();
          lcd.setCursor(0, 0);
          lcd.print("Reading Soil");
          lcd.setCursor(0, 1);
          lcd.print("Moisture...");
        }
      }
      break;

    case READING_SENSORS:
      delay(1000); // Simulate reading time
      
      int soilAnalogValue = 0;
      if (selectedField == 1) {
        soilAnalogValue = analogRead(SOIL_PIN_1);
      } else if (selectedField == 2) {
        soilAnalogValue = analogRead(SOIL_PIN_2);
      } else if (selectedField == 3) {
        soilAnalogValue = analogRead(SOIL_PIN_3);
      }

      // The raw analog reading (e.g. 100 = Wet, 1000 = Dry)
      int rawSoilValue = soilAnalogValue;
      
      currentState = SENDING_DATA;
      
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Soil Raw:");
      lcd.print(rawSoilValue);
      lcd.setCursor(0, 1);
      lcd.print("Sending to MCU..");
      
      // SEND DATA TO NODEMCU VIA SERIAL
      // Format: <FieldID>,<CropIndex>,<SoilMoisture>
      Serial.print(selectedField);
      Serial.print(",");
      Serial.print(selectedCropIndex);
      Serial.print(",");
      Serial.println(rawSoilValue);
      
      delay(3000);
      
      // Reset back to field selection for continuous operation
      currentState = SELECT_FIELD;
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Select Field:");
      lcd.setCursor(0, 1);
      lcd.print("1, 2, or 3?");
      break;
  }
}
