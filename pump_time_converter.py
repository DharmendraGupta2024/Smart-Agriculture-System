import argparse

def calculate_pump_time(rainfall_mm, length_cm, width_cm, flow_rate_ml_per_sec):
    """
    Converts rainfall requirement (mm) into pump run time (seconds).
    
    1 mm of rainfall = 1 Liter of water per Square Meter
    1 Liter = 1000 mL
    """
    # 1. Convert dimensions from cm to meters
    length_m = length_cm / 100.0
    width_m = width_cm / 100.0
    
    # 2. Calculate Area in square meters
    area_m2 = length_m * width_m
    
    # 3. Calculate Required Volume in Liters
    # Formula: Volume (Liters) = Area (m^2) * Rainfall (mm)
    volume_liters = area_m2 * rainfall_mm
    
    # 4. Convert Volume to milliliters (since small pumps usually rate in mL/sec)
    volume_ml = volume_liters * 1000.0
    
    # 5. Calculate Pump Run Time in Seconds
    # Formula: Time (sec) = Volume (mL) / Flow Rate (mL/sec)
    time_seconds = volume_ml / flow_rate_ml_per_sec
    
    return area_m2, volume_ml, time_seconds

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert Predicted Rainfall to Pump Run Time.")
    
    # Input arguments with default test data
    parser.add_argument('--rainfall', type=float, default=215.39, help="Predicted rainfall required in mm (Default: 215.39)")
    parser.add_argument('--length', type=float, default=40.0, help="Length of the testing field in cm (Default: 40.0)")
    parser.add_argument('--width', type=float, default=40.0, help="Width of the testing field in cm (Default: 40.0)")
    parser.add_argument('--flow_rate', type=float, default=50.0, help="Pump flow rate in mL per second (Default: 50.0)")
    parser.add_argument('--field_id', type=str, default="Field 1", help="Identifier for the testing field (Default: Field 1)")

    args = parser.parse_args()

    area, volume_ml, run_time = calculate_pump_time(
        rainfall_mm=args.rainfall,
        length_cm=args.length,
        width_cm=args.width,
        flow_rate_ml_per_sec=args.flow_rate
    )

    print("\n" + "="*45)
    print(f"--- PUMP ACTIVATION CALCULATOR - {args.field_id} ---")
    print("="*45)
    print(f"Input Prediction : {args.rainfall:.2f} mm of rainfall")
    print(f"Field Dimensions : {args.length} cm x {args.width} cm")
    print(f"Field Area       : {area:.4f} m^2")
    print("-" * 45)
    print(f"Required Water   : {volume_ml:.2f} mL ({volume_ml/1000:.2f} Liters)")
    print(f"Pump Flow Rate   : {args.flow_rate} mL/sec")
    print("-" * 45)
    print(f"ACTION -> RUN MOTOR FOR: {run_time:.2f} seconds")
    print("="*45 + "\n")
