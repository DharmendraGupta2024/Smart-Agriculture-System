import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import numpy as np

def train_and_evaluate(X, y, feature_set_name):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    categorical_features = ['label']
    categorical_transformer = OneHotEncoder(handle_unknown='ignore')

    preprocessor = ColumnTransformer(
        transformers=[('cat', categorical_transformer, categorical_features)],
        remainder='passthrough'
    )

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    clf = Pipeline(steps=[('preprocessor', preprocessor), ('model', model)])
    
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)

    mse = mean_squared_error(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    return {'Model': feature_set_name, 'MSE': mse, 'MAE': mae, 'R2': r2}

def main():
    print("Loading dataset for comparison...")
    df = pd.read_csv('Crop_recommendation.csv')
    y = df['rainfall']

    # Full Features Model
    X_full = df[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'label']]
    res_full = train_and_evaluate(X_full, y, "Full Sensors (with N,P,K,pH)")

    # Reduced Features Model
    X_reduced = df[['temperature', 'humidity', 'label']]
    res_reduced = train_and_evaluate(X_reduced, y, "Limited Sensors (Temp, Hum)")

    results_df = pd.DataFrame([res_full, res_reduced])
    
    print("\n--- Model Comparison Results ---")
    print(results_df.to_string(index=False))
    
    # Generate Comparison Charts
    sns.set_theme(style="whitegrid")
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.suptitle('Trade-off Analysis: Sensor Availability vs. Model Accuracy', fontsize=16)

    # R2 Plot
    sns.barplot(ax=axes[0], x='Model', y='R2', data=results_df, palette=['#4C72B0', '#DD8452'])
    axes[0].set_title('R-squared Score (Higher is Better)')
    axes[0].set_ylim(0, 1.1)
    for p in axes[0].patches:
        axes[0].annotate(format(p.get_height(), '.2f'), 
                         (p.get_x() + p.get_width() / 2., p.get_height()), 
                         ha = 'center', va = 'center', xytext = (0, 9), textcoords = 'offset points')

    # MAE Plot
    sns.barplot(ax=axes[1], x='Model', y='MAE', data=results_df, palette=['#4C72B0', '#DD8452'])
    axes[1].set_title('Mean Absolute Error (Lower is Better)')
    for p in axes[1].patches:
        axes[1].annotate(format(p.get_height(), '.2f'), 
                         (p.get_x() + p.get_width() / 2., p.get_height()), 
                         ha = 'center', va = 'center', xytext = (0, 9), textcoords = 'offset points')

    # MSE Plot
    sns.barplot(ax=axes[2], x='Model', y='MSE', data=results_df, palette=['#4C72B0', '#DD8452'])
    axes[2].set_title('Mean Squared Error (Lower is Better)')
    for p in axes[2].patches:
        axes[2].annotate(format(p.get_height(), '.2f'), 
                         (p.get_x() + p.get_width() / 2., p.get_height()), 
                         ha = 'center', va = 'center', xytext = (0, 9), textcoords = 'offset points')

    plt.tight_layout()
    plt.savefig('model_comparison.png', dpi=300)
    print("\nComparison chart saved as 'model_comparison.png'")

if __name__ == "__main__":
    main()
