import os
import json
import pandas as pd

def compile_dashboard_data(cleaned_csv="data/cleaned_sales_data.csv",
                           forecast_json="machine_learning/forecast_results.json",
                           output_js="dashboard/data_store.js"):
    print("Compiling dataset for web dashboard...")

    # Check dependencies
    if not os.path.exists(cleaned_csv):
        raise FileNotFoundError(f"Cleaned CSV not found: {cleaned_csv}")
    if not os.path.exists(forecast_json):
        raise FileNotFoundError(f"Forecast JSON not found: {forecast_json}")

    # Load cleaned data
    df = pd.read_csv(cleaned_csv)
    
    # Load forecast data
    with open(forecast_json, "r") as f:
        forecast_data = json.load(f)

    # 1. Compile Transactional Records
    # Limit transactions to keep JS file size manageable but representative (~1000 orders)
    # We will sort by date, select a representative sample of 800, and format
    sample_df = df.sort_values(by="Order Date")
    records = []
    for idx, row in sample_df.iterrows():
        records.append({
            "order_id": row["Order ID"],
            "date": row["Order Date"],
            "customer": row["Customer Name"],
            "category": row["Category"],
            "subcat": row["Sub-Category"],
            "sales": float(row["Sales"]),
            "profit": float(row["Profit"]),
            "qty": int(row["Quantity"]),
            "region": row["Region"],
            "repeat": row["Is Repeat Customer"]
        })

    # 2. Extract Categories and Sub-categories mapping for recommendations
    cat_structure = {}
    for cat in df["Category"].unique():
        cat_structure[cat] = list(df[df["Category"] == cat]["Sub-Category"].unique())

    # 3. Assemble JSON Payload
    payload = {
        "raw_transactions": records,
        "category_structure": cat_structure,
        "evaluation_metrics": forecast_data["evaluation_metrics"],
        "historical_sales_monthly": forecast_data["historical_sales"],
        "forecast_12_months": forecast_data["forecast_12_months"]
    }

    # 4. Write as Javascript variable definition
    os.makedirs(os.path.dirname(output_js), exist_ok=True)
    with open(output_js, "w") as f:
        f.write("// STANDALONE COMPILATION OF PORTFOLIO SALES DATA STORE\n")
        f.write("// Derived from python_analysis/data_cleaning.py & machine_learning/sales_forecasting.py\n\n")
        f.write("const SalesDashboardData = ")
        json.dump(payload, f, indent=4)
        f.write(";\n")
        
    print(f"Stand-alone JS Data Store written to: {output_js}")
    print(f"Data includes {len(records)} transactions, full ML forecasts, and metrics.")

if __name__ == "__main__":
    compile_dashboard_data()
