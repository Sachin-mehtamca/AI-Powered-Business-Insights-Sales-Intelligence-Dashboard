import os
import pandas as pd
import numpy as np

def clean_and_prepare_data(input_path="data/raw_sales_data.csv", output_path="data/cleaned_sales_data.csv"):
    print("Starting Python Data Cleaning & Preprocessing pipeline...")
    
    # 1. Load Raw Dataset
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Raw data file not found at: {input_path}. Please run data/generate_dataset.py first.")
    
    df = pd.read_csv(input_path)
    print(f"Successfully loaded raw dataset. Shape: {df.shape}")

    # 2. Inspect Missing Values
    null_counts = df.isnull().sum()
    print("Null values check:")
    for col, null_val in null_counts.items():
        print(f" - {col}: {null_val} missing values")

    # If any null values existed, we would fill or drop them:
    # df = df.fillna({'Sales': 0, 'Profit': 0})
    
    # 3. Standardize String Columns (trimming whitespace, correct capitalization)
    string_cols = ["Order ID", "Customer Name", "Category", "Sub-Category", "Region", "Is Repeat Customer"]
    for col in string_cols:
        df[col] = df[col].astype(str).str.strip()

    # 4. Standardize Dates
    print("Standardizing 'Order Date' to datetime...")
    df["Order Date"] = pd.to_datetime(df["Order Date"])
    
    # 5. Type Conversions & Precision
    print("Enforcing datatype integrity...")
    df["Sales"] = pd.to_numeric(df["Sales"]).round(2)
    df["Profit"] = pd.to_numeric(df["Profit"]).round(2)
    df["Quantity"] = pd.to_numeric(df["Quantity"]).astype(int)

    # 6. Feature Engineering (Adding month-year, week, weekday helper fields for EDA & modeling)
    df["Order Year"] = df["Order Date"].dt.year
    df["Order Month"] = df["Order Date"].dt.month
    df["Order Month Name"] = df["Order Date"].dt.strftime("%b")
    df["Order Day of Week"] = df["Order Date"].dt.day_name()
    df["Order Month-Year"] = df["Order Date"].dt.to_period("M").astype(str)
    
    # Add an Order Day Type (Weekend vs Weekday)
    df["Day Type"] = np.where(df["Order Date"].dt.dayofweek.isin([5, 6]), "Weekend", "Weekday")

    # 7. Outlier Detection & Logging
    # Define an outlier as sales greater than 3 standard deviations from the category mean
    print("Scanning for sales outliers...")
    outliers = []
    for cat in df["Category"].unique():
        cat_df = df[df["Category"] == cat]
        mean = cat_df["Sales"].mean()
        std = cat_df["Sales"].std()
        cat_outliers = cat_df[cat_df["Sales"] > (mean + 3 * std)]
        outliers.append(cat_outliers)
    
    all_outliers = pd.concat(outliers)
    print(f" - Detected {len(all_outliers)} sales transactions exceeding 3 standard deviations.")

    # In a real business application, we might keep them or isolate them depending on the goal.
    # Here, we keep them as they represent valid high-value orders.

    # 8. Save Cleaned Dataset
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Data Cleaning pipeline completed. Cleaned dataset stored at: {output_path}")
    print(f"Final Cleaned Dataset Shape: {df.shape}\n")
    return df

if __name__ == "__main__":
    clean_and_prepare_data()
