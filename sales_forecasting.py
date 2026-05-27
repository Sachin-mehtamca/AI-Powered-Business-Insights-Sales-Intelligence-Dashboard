import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def run_sales_forecasting(input_path="data/cleaned_sales_data.csv", 
                          results_path="machine_learning/forecast_results.json",
                          plot_path="reports/images/sales_forecast.png"):
    print("Initializing Machine Learning Sales Forecasting Module...")

    # Ensure directories exist
    os.makedirs(os.path.dirname(results_path), exist_ok=True)
    os.makedirs(os.path.dirname(plot_path), exist_ok=True)

    # 1. Load Cleaned Dataset
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Cleaned dataset not found at: {input_path}. Please run python_analysis/data_cleaning.py first.")
    
    df = pd.read_csv(input_path)
    df["Order Date"] = pd.to_datetime(df["Order Date"])

    # 2. Time-Series Aggregation
    print("Aggregating transactional data to monthly sales metrics...")
    df["YearMonth"] = df["Order Date"].dt.to_period("M")
    monthly_series = df.groupby("YearMonth").agg({"Sales": "sum", "Profit": "sum"}).reset_index()
    monthly_series = monthly_series.sort_values(by="YearMonth").reset_index(drop=True)
    
    # Total months available
    n_months = len(monthly_series)
    print(f"Historical timeframe spans {n_months} months: {monthly_series['YearMonth'].iloc[0]} to {monthly_series['YearMonth'].iloc[-1]}")

    # Convert YearMonth to timestamp for plotting/formatting
    monthly_series["Timestamp"] = monthly_series["YearMonth"].dt.to_timestamp()

    # 3. Feature Engineering for Time-Series Regression
    # Create lag features, rolling windows, and time-based index
    monthly_series["MonthIndex"] = np.arange(n_months)  # Linear trend feature
    monthly_series["MonthOfYear"] = monthly_series["Timestamp"].dt.month
    
    # Sine/Cosine encoding for seasonality (annual cyclical patterns)
    monthly_series["Month_Sin"] = np.sin(2 * np.pi * monthly_series["MonthOfYear"] / 12)
    monthly_series["Month_Cos"] = np.cos(2 * np.pi * monthly_series["MonthOfYear"] / 12)
    
    # Lag features (Sales from previous months)
    monthly_series["Sales_Lag1"] = monthly_series["Sales"].shift(1)
    monthly_series["Sales_Lag2"] = monthly_series["Sales"].shift(2)
    
    # Fill NaN values created by lag shifts
    monthly_series = monthly_series.dropna().reset_index(drop=True)
    
    # 4. Train-Test Split (Chronological splitting for Time-Series validation)
    # Use last 5 months as test set
    test_size = 5
    train_df = monthly_series.iloc[:-test_size]
    test_df = monthly_series.iloc[-test_size:]
    
    features = ["MonthIndex", "Month_Sin", "Month_Cos", "Sales_Lag1", "Sales_Lag2"]
    target = "Sales"
    
    X_train, y_train = train_df[features], train_df[target]
    X_test, y_test = test_df[features], test_df[target]

    print(f"Dataset split: Train = {len(train_df)} months, Test = {len(test_df)} months")

    # 5. Model 1: Linear Regression (Baseline)
    print("Training Linear Regression Baseline...")
    lr_model = LinearRegression()
    lr_model.fit(X_train, y_train)
    lr_pred = lr_model.predict(X_test)

    # 6. Model 2: Random Forest Regressor
    print("Training Random Forest Regressor...")
    rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
    rf_model.fit(X_train, y_train)
    rf_pred = rf_model.predict(X_test)

    # 7. Model Evaluation
    metrics = {}
    for name, pred in [("Linear Regression", lr_pred), ("Random Forest", rf_pred)]:
        mae = mean_absolute_error(y_test, pred)
        rmse = np.sqrt(mean_squared_error(y_test, pred))
        r2 = r2_score(y_test, pred)
        metrics[name] = {
            "MAE": round(mae, 2),
            "RMSE": round(rmse, 2),
            "R2": round(r2, 4)
        }
        print(f"Model: {name} | MAE: ${mae:,.2f} | RMSE: ${rmse:,.2f} | R2: {r2:.4f}")

    # 8. Train on FULL Dataset & Forecast next 12 Months
    print("Re-fitting models on full historical timeframe...")
    X_full = monthly_series[features]
    y_full = monthly_series[target]
    
    lr_final = LinearRegression()
    lr_final.fit(X_full, y_full)
    
    rf_final = RandomForestRegressor(n_estimators=100, random_state=42)
    rf_final.fit(X_full, y_full)

    # Autoregressive 12-month Forecasting (June 2026 - May 2027)
    last_row = monthly_series.iloc[-1]
    forecast_records = []
    
    current_lag1 = last_row["Sales"]
    current_lag2 = last_row["Sales_Lag1"]
    current_month_index = last_row["MonthIndex"] + 1
    
    last_timestamp = last_row["Timestamp"]
    
    for i in range(12):
        # Determine future date details
        future_date = last_timestamp + pd.DateOffset(months=i+1)
        future_month = future_date.month
        
        # Formulate features
        f_sin = np.sin(2 * np.pi * future_month / 12)
        f_cos = np.cos(2 * np.pi * future_month / 12)
        
        X_future = pd.DataFrame([{
            "MonthIndex": current_month_index,
            "Month_Sin": f_sin,
            "Month_Cos": f_cos,
            "Sales_Lag1": current_lag1,
            "Sales_Lag2": current_lag2
        }])
        
        # Predict
        lr_f_pred = lr_final.predict(X_future)[0]
        rf_f_pred = rf_final.predict(X_future)[0]
        
        forecast_records.append({
            "Month": future_date.strftime("%Y-%m"),
            "Linear_Regression_Forecast": round(float(lr_f_pred), 2),
            "Random_Forest_Forecast": round(float(rf_f_pred), 2)
        })
        
        # Roll forward lag values using Random Forest predictions as default feedback loop
        current_lag2 = current_lag1
        current_lag1 = rf_f_pred
        current_month_index += 1

    # 9. Format outputs for client-side consumption
    historical_data = []
    for idx, row in monthly_series.iterrows():
        historical_data.append({
            "Month": row["YearMonth"].strftime("%Y-%m"),
            "Sales": round(row["Sales"], 2),
            "Profit": round(row["Profit"], 2)
        })

    output_payload = {
        "evaluation_metrics": metrics,
        "historical_sales": historical_data,
        "forecast_12_months": forecast_records
    }

    # Save to JSON
    with open(results_path, "w") as f:
        json.dump(output_payload, f, indent=4)
    print(f"Forecast results and performance metrics saved to: {results_path}")

    # 10. Generate Forecast Visualization
    print("Generating AI Sales Forecast comparison chart...")
    plt.figure(figsize=(12, 6), dpi=150)
    
    # Historical Actuals
    hist_months = [h["Month"] for h in historical_data]
    hist_sales = [h["Sales"] for h in historical_data]
    plt.plot(hist_months, hist_sales, label="Historical Actuals", color="#1e293b", marker="o", linewidth=2.5)

    # Forecast Months & values
    f_months = [f["Month"] for f in forecast_records]
    f_lr = [f["Linear_Regression_Forecast"] for f in forecast_records]
    f_rf = [f["Random_Forest_Forecast"] for f in forecast_records]

    # Combine months for continuous x-axis plotting
    all_months = hist_months + f_months
    
    # Connect last historical month to first forecast month visually
    plt.plot([hist_months[-1], f_months[0]], [hist_sales[-1], f_lr[0]], color="#6366f1", linestyle="--", alpha=0.5)
    plt.plot([hist_months[-1], f_months[0]], [hist_sales[-1], f_rf[0]], color="#ec4899", linestyle="--", alpha=0.5)

    plt.plot(f_months, f_lr, label="AI Forecast (Linear Regression)", color="#6366f1", linestyle="--", marker="^", linewidth=2)
    plt.plot(f_months, f_rf, label="AI Forecast (Random Forest)", color="#ec4899", linestyle="--", marker="s", linewidth=2)

    plt.xticks(all_months, rotation=90, fontsize=8)
    plt.title("AI-Powered 12-Month Future Revenue Forecasting", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Month-Year", fontweight="semibold")
    plt.ylabel("Revenue ($)", fontweight="semibold")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend(loc="upper left")
    plt.tight_layout()

    plt.savefig(plot_path, dpi=300)
    plt.close()
    print(f"Forecasting chart successfully saved to: {plot_path}\n")

if __name__ == "__main__":
    run_sales_forecasting()
