import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import numpy as np
import os

def generate_research_matrices():
    print("Loading data and model...")
    df = pd.read_csv('Crop_recommendation.csv')
    model = joblib.load('crop_water_model.pkl')

    # Recreate the test split
    X = df[['temperature', 'humidity', 'label']]
    y = df['rainfall']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Predictions
    y_pred = model.predict(X_test)

    # 1. Correlation Matrix Heatmap (Excluding the categorical 'label')
    print("Generating Correlation Matrix...")
    plt.figure(figsize=(10, 8))
    numeric_df = df.drop(columns=['label'])
    corr_matrix = numeric_df.corr()
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5)
    plt.title('Feature Correlation Matrix ')
    plt.tight_layout()
    plt.savefig('correlation_matrix.png', dpi=300)
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
    plt.savefig('actual_vs_predicted_matrix.png', dpi=300)
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
    plt.savefig('residual_error_matrix.png', dpi=300)
    plt.close()

    print("Saved as:")
    print(" 1. correlation_matrix.png (Shows relationship between soil/temp and water)")
    print(" 2. actual_vs_predicted_matrix.png (Shows prediction accuracy)")
    print(" 3. residual_error_matrix.png (Shows error distribution)")

if __name__ == "__main__":
    generate_research_matrices()
