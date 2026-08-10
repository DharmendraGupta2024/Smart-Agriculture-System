from pathlib import Path
import joblib
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models"

def calculate_pump_time_prototype(rainfall_mm, flow_rate_ml_per_sec=50.0):
    """
    Converts rainfall requirement (mm) into pump run time (seconds).
    Uses a prototype scaling factor to account for the small 15x30cm wooden box.
    """
    # Wooden setup dimensions
    length_cm = 30.0
    width_cm = 15.0
    
    length_m = length_cm / 100.0
    width_m = width_cm / 100.0
    area_m2 = length_m * width_m
    
    # Required Volume in Liters
    volume_liters = area_m2 * rainfall_mm
    
    # Convert Volume to milliliters
    volume_ml = volume_liters * 1000.0
    
    # PROTOTYPE SCALE FACTOR: The ML model predicts rainfall for an entire season/month for a crop.
    # For a small prototype demo, running the pump for 3-4 minutes is too much.
    # We apply a scale factor so it runs for ~10 to 30 seconds.
    PROTOTYPE_SCALE_FACTOR = 0.33 
    scaled_volume_ml = volume_ml * PROTOTYPE_SCALE_FACTOR
    
    # Time in seconds
    time_seconds = scaled_volume_ml / flow_rate_ml_per_sec
    
    return area_m2, volume_ml, time_seconds, scaled_volume_ml

def main():
    try:
        model = joblib.load(MODELS_DIR / 'edge_rf_model.pkl')
        crop_mapping = joblib.load(MODELS_DIR / 'crop_mapping.pkl')
    except FileNotFoundError:
        print("Model files not found. Please run 'python src/train_edge_model.py' first.")
        return


    print("==================================================")
    print("   SMART AGRICULTURE SYSTEM - COMMAND LINE DEMO   ")
    print("==================================================")
    
    # Prompt for Field
    field_id = input("Enter Field ID (e.g., 1, 2, 3): ")

    # Display Crop Menu
    print("\n--- Available Crops ---")
    valid_crops = list(crop_mapping.keys())
    for crop in valid_crops:
        print(f" - {crop.capitalize()}")
    
    while True:
        crop_input = input("\nType the name of the crop: ").strip().lower()
        if crop_input in valid_crops:
            crop_id = crop_mapping[crop_input]
            break
        else:
            print("Invalid crop. Please select from the list above.")

    # Sensor Readings
    try:
        temperature = float(input("Enter Temperature (°C): "))
        humidity = float(input("Enter Humidity (%): "))
        soil_moisture = float(input("Enter Soil Moisture (Raw Analog 100-1000): "))
    except ValueError:
        print("Invalid input. Please enter numbers only.")
        return

    # Create input dataframe matching the training features
    input_data = pd.DataFrame({
        'temperature': [temperature],
        'humidity': [humidity],
        'crop_id': [crop_id]
    })

    # Predict
    predicted_rainfall = model.predict(input_data)[0]

    print("\n==================================================")
    print("                 PREDICTION RESULTS               ")
    print("==================================================")
    print(f"Field             : {field_id}")
    print(f"Crop Selected     : {crop_input.capitalize()}")
    print(f"Sensor Readings   : {temperature}°C, {humidity}% Humidity")
    print(f"Predicted Rainfall: {predicted_rainfall:.2f} mm")
    
    # Pump Calculation
    flow_rate = 50.0 # Standard flow rate for 12v pump
    area, vol_ml, time_sec, scaled_vol = calculate_pump_time_prototype(predicted_rainfall, flow_rate)
    
    # Soil Moisture Logic (100 = Wet, 1000 = Dry)
    if soil_moisture <= 400:
        time_sec = 0
        soil_status = "SUFFICIENT (Wet)"
    else:
        soil_status = "LOW (Dry)"
    
    print("--------------------------------------------------")
    print("               PROTOTYPE PUMP LOGIC               ")
    print("--------------------------------------------------")
    print(f"Wooden Setup Area : 15 cm x 30 cm ({area:.4f} m²)")
    print(f"Soil Moisture     : {soil_moisture} -> {soil_status}")
    print(f"Raw Water Volume  : {vol_ml:.2f} mL")
    print(f"Scaled Volume     : {scaled_vol:.2f} mL (Prototype scaling applied)")
    print(f"Pump Flow Rate    : {flow_rate} mL/sec")
    
    if time_sec > 0:
        print("\n=> ACTION REQUIRED: TURN ON PUMP FOR: {:.2f} SECONDS".format(time_sec))
    else:
        print("\n=> ACTION REQUIRED: SKIP PUMPING (Soil is already wet enough)")
    print("==================================================\n")

if __name__ == '__main__':
    main()
