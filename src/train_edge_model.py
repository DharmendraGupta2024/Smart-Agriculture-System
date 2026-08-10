from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from micromlgen import port
import joblib

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
FIRMWARE_DIR = BASE_DIR / "firmware" / "node_mcu_client"

# The 8 crops the user wants
TARGET_CROPS = ['wheat', 'maize', 'rice', 'potato', 'tomato', 'ginger', 'mustard', 'chili']

def main():
    print("Loading data...")
    data_path = DATA_DIR / "Crop_recommendation.csv"
    df = pd.read_csv(data_path)

    # Add synthetic data for missing crops to ensure the model can train
    missing_crops = [crop for crop in TARGET_CROPS if crop not in df['label'].unique()]
    synthetic_rows = []
    
    # Generate some plausible synthetic data for the missing crops
    for crop in missing_crops:
        for _ in range(100):
            temp = np.random.uniform(20.0, 35.0)
            hum = np.random.uniform(40.0, 80.0)
            rainfall = np.random.uniform(80.0, 200.0)
            synthetic_rows.append({'temperature': temp, 'humidity': hum, 'label': crop, 'rainfall': rainfall})
            
    if synthetic_rows:
        synth_df = pd.DataFrame(synthetic_rows)
        df = pd.concat([df, synth_df], ignore_index=True)

    # Filter dataset to ONLY the 8 target crops
    df = df[df['label'].isin(TARGET_CROPS)].copy()

    # Create an integer mapping for the crops because C++ handles integers much better
    crop_to_id = {crop: idx for idx, crop in enumerate(TARGET_CROPS)}
    df['crop_id'] = df['label'].map(crop_to_id)

    # Save mapping for predict.py to use later
    crop_mapping_path = MODELS_DIR / "crop_mapping.pkl"
    joblib.dump(crop_to_id, crop_mapping_path)
    print("Crop Mapping:", crop_to_id)

    X = df[['temperature', 'humidity', 'crop_id']]
    y = df['rainfall']

    print(f"Training Random Forest on {len(df)} samples...")
    # Keep n_estimators small so the C++ header file isn't massive (ESP8266 has limited memory)
    model = RandomForestRegressor(n_estimators=15, max_depth=8, random_state=42)
    model.fit(X, y)

    # Export to C++ using micromlgen
    print("Exporting model to pure C++ (crop_model.h)...")
    try:
        c_code = port(model)
        
        # Save header to models/ directory
        header_model_path = MODELS_DIR / "crop_model.h"
        with open(header_model_path, 'w') as f:
            f.write(c_code)
            
        # Also save directly inside NodeMCU firmware directory for Arduino IDE compilation
        header_firmware_path = FIRMWARE_DIR / "crop_model.h"
        with open(header_firmware_path, 'w') as f:
            f.write(c_code)
            
        print(f"Successfully exported crop_model.h to:\n - {header_model_path}\n - {header_firmware_path}")
    except Exception as e:
        print(f"Error exporting model via micromlgen: {e}")
        
    # Also save the python model for the CLI tool
    edge_model_path = MODELS_DIR / "edge_rf_model.pkl"
    joblib.dump(model, edge_model_path)
    print(f"Saved {edge_model_path} for Python CLI.")

if __name__ == "__main__":
    main()

