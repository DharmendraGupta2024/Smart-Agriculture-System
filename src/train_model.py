from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"

def main():
    print("Loading data...")
    data_path = DATA_DIR / "Crop_recommendation.csv"
    df = pd.read_csv(data_path)

    # Features: temperature, humidity, label
    # Target: rainfall (water required)
    X = df[['temperature', 'humidity', 'label']]
    y = df['rainfall']

    print("Setting up preprocessing and model pipeline...")
    # Preprocessing: One-hot encode the categorical 'label' feature
    categorical_features = ['label']
    categorical_transformer = OneHotEncoder(handle_unknown='ignore')

    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', categorical_transformer, categorical_features)
        ],
        remainder='passthrough'
    )

    # Define the Random Forest Regressor Model
    model = RandomForestRegressor(n_estimators=100, random_state=42)

    # Bundle preprocessing and modeling code in a pipeline
    clf = Pipeline(steps=[('preprocessor', preprocessor),
                          ('model', model)])

    # Split data into train and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print("Training the model...")
    clf.fit(X_train, y_train)

    print("Evaluating the model...")
    y_pred = clf.predict(X_test)

    mse = mean_squared_error(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print("\n--- Model Evaluation Metrics ---")
    print(f"Mean Squared Error (MSE): {mse:.2f}")
    print(f"Mean Absolute Error (MAE): {mae:.2f} mm")
    print(f"R-squared (R2): {r2:.2f}")

    # Create an output matrix of Actual vs Predicted
    results_df = pd.DataFrame({
        'Crop': X_test['label'],
        'Actual Rainfall (mm)': y_test.round(2),
        'Predicted Rainfall (mm)': np.round(y_pred, 2),
        'Difference (mm)': np.round(y_test - y_pred, 2)
    })
    
    print("\n--- Output Matrix: Actual vs Predicted (First 15 samples) ---")
    print(results_df.head(15).to_string())
    
    # Save the evaluation to a CSV file for the user
    eval_matrix_path = DATA_DIR / "evaluation_matrix.csv"
    results_df.to_csv(eval_matrix_path, index=False)
    print(f"\nFull output matrix saved to '{eval_matrix_path}'.")

    # Save the trained model pipeline (includes encoder and model)
    model_path = MODELS_DIR / "crop_water_model.pkl"
    joblib.dump(clf, model_path)
    print(f"\nModel successfully saved to '{model_path}'")

if __name__ == "__main__":
    main()

