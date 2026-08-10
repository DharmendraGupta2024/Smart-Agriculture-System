from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import numpy as np
import os

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
REPORTS_DIR = BASE_DIR / "reports"

def generate_research_matrices():
    print("Loading data and model...")
    data_path = DATA_DIR / "Crop_recommendation.csv"
    model_path = MODELS_DIR / "crop_water_model.pkl"
    
    df = pd.read_csv(data_path)
    model = joblib.load(model_path)

    # Recreate the test split
    X = df[['temperature', 'humidity', 'label']]
    y = df['rainfall']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Predictions
    y_pred = model.predict(X_test)

    # Ensure reports directory exists
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Correlation Matrix Heatmap (Excluding the categorical 'label')
    print("Generating Correlation Matrix...")
    plt.figure(figsize=(10, 8))
    numeric_df = df.drop(columns=['label'])
    corr_matrix = numeric_df.corr()
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5)
    plt.title('Feature Correlation Matrix')
    plt.tight_layout()
    corr_plot_path = REPORTS_DIR / "correlation_matrix.png"
    plt.savefig(corr_plot_path, dpi=300)
    plt.close()

    # 2. Actual vs Predicted Scatter Matrix
    print("Generating Actual vs Predicted Matrix Plot...")
    plt.figure(figsize=(8, 8))
    plt.scatter(y_test, y_pred, alpha=0.6, color='blue', edgecolors='k')
    
    # Plot perfect prediction line
    min_val = min(y_test.min(), y_pred.min())
    max_val = max(y_test.max(), y_pred.max())
    plt.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2, label='Perfect Prediction')
    
    plt.xlabel('Actual Water Requirement (Rainfall mm)')
    plt.ylabel('Predicted Water Requirement (Rainfall mm)')
    plt.title('Prediction Accuracy: Actual vs. Predicted')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    scatter_plot_path = REPORTS_DIR / "actual_vs_predicted_matrix.png"
    plt.savefig(scatter_plot_path, dpi=300)
    plt.close()

    # 3. Residual Error Matrix Plot
    print("Generating Residual Error Matrix...")
    residuals = y_test - y_pred
    plt.figure(figsize=(10, 6))
    sns.histplot(residuals, kde=True, bins=40, color='purple')
    plt.title('Residual Error Distribution')
    plt.xlabel('Prediction Error (mm)')
    plt.ylabel('Frequency')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    residual_plot_path = REPORTS_DIR / "residual_error_matrix.png"
    plt.savefig(residual_plot_path, dpi=300)
    plt.close()

    print("Saved as:")
    print(f" 1. {corr_plot_path} (Shows relationship between soil/temp and water)")
    print(f" 2. {scatter_plot_path} (Shows prediction accuracy)")
    print(f" 3. {residual_plot_path} (Shows error distribution)")

if __name__ == "__main__":
    generate_research_matrices()

