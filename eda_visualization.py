import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def generate_eda_visualizations(input_path="data/cleaned_sales_data.csv", output_dir="reports/images/"):
    print("Initiating Exploratory Data Analysis (EDA) & Visualization script...")

    # Ensure output folder exists
    os.makedirs(output_dir, exist_ok=True)

    # 1. Load Preprocessed Data
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Cleaned dataset not found at: {input_path}. Please run python_analysis/data_cleaning.py first.")
    df = pd.read_csv(input_path)
    df["Order Date"] = pd.to_datetime(df["Order Date"])

    # Define color scheme for cohesive aesthetics (modern theme)
    colors = {
        'primary': '#6366f1',    # Indigo
        'secondary': '#a855f7',  # Violet
        'accent': '#ec4899',     # Pink
        'success': '#10b981',    # Emerald
        'dark': '#1e293b',       # Slate
        'light': '#f8fafc',      # Slate-50
        'grid': '#e2e8f0'        # Slate-200
    }

    # Set Matplotlib style defaults for sleek appearance
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['text.color'] = colors['dark']
    plt.rcParams['axes.labelcolor'] = colors['dark']
    plt.rcParams['xtick.color'] = colors['dark']
    plt.rcParams['ytick.color'] = colors['dark']
    plt.rcParams['axes.edgecolor'] = '#cbd5e1'
    plt.rcParams['axes.linewidth'] = 0.8

    # -------------------------------------------------------------
    # Visualization 1: Monthly Sales & Profit Trend (Time-Series)
    # -------------------------------------------------------------
    print("Generating Chart 1: Monthly Sales & Profit Trend...")
    monthly_data = df.groupby("Order Month-Year").agg({"Sales": "sum", "Profit": "sum"}).reset_index()
    monthly_data = monthly_data.sort_values(by="Order Month-Year")

    fig, ax1 = plt.subplots(figsize=(12, 6), dpi=150)

    # Sales Bar Chart
    bars = ax1.bar(monthly_data["Order Month-Year"], monthly_data["Sales"], color=colors['primary'], alpha=0.15, label="Monthly Sales")
    ax1.set_xlabel("Month", fontweight="semibold", labelpad=10)
    ax1.set_ylabel("Sales ($)", color=colors['primary'], fontweight="semibold")
    ax1.tick_params(axis='y', labelcolor=colors['primary'])
    ax1.set_xticks(monthly_data["Order Month-Year"])
    ax1.set_xticklabels(monthly_data["Order Month-Year"], rotation=45, ha='right', fontsize=8)

    # Profit Line Chart on secondary y-axis
    ax2 = ax1.twinx()
    line = ax2.plot(monthly_data["Order Month-Year"], monthly_data["Profit"], color=colors['secondary'], marker='o', linewidth=2.5, label="Monthly Profit")
    ax2.set_ylabel("Profit ($)", color=colors['secondary'], fontweight="semibold")
    ax2.tick_params(axis='y', labelcolor=colors['secondary'])

    # Aesthetics
    plt.title("Monthly Sales & Profit Growth Trend (2024 - 2026)", fontsize=14, fontweight="bold", pad=15)
    ax1.grid(True, linestyle='--', alpha=0.5, color=colors['grid'])
    fig.tight_layout()

    # Save
    chart1_path = os.path.join(output_dir, "monthly_trends.png")
    plt.savefig(chart1_path, dpi=300)
    plt.close()
    print(f" - Saved monthly trend chart to: {chart1_path}")

    # -------------------------------------------------------------
    # Visualization 2: Category and Sub-category Sales & Margins
    # -------------------------------------------------------------
    print("Generating Chart 2: Category Sales & Profit Performance...")
    cat_data = df.groupby("Category").agg({"Sales": "sum", "Profit": "sum"}).reset_index()
    cat_data["Margin %"] = (cat_data["Profit"] / cat_data["Sales"]) * 100

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=150)

    # Sales Comparison (Pie Chart)
    wedges, texts, autotexts = ax1.pie(
        cat_data["Sales"], 
        labels=cat_data["Category"], 
        autopct='%1.1f%%',
        startangle=140, 
        colors=[colors['primary'], colors['secondary'], colors['accent']],
        wedgeprops=dict(width=0.6, edgecolor='white', linewidth=2) # Donut style
    )
    plt.setp(texts, size=10, fontweight="semibold")
    plt.setp(autotexts, size=9, weight="bold", color="white")
    ax1.set_title("Sales Contribution by Category", fontsize=12, fontweight="bold", pad=10)

    # Profit & Profit Margin Comparison (Bar Chart)
    x_indices = np.arange(len(cat_data["Category"]))
    bar_width = 0.35

    rects1 = ax2.bar(x_indices - bar_width/2, cat_data["Profit"], bar_width, label="Profit ($)", color=colors['success'])
    ax2_twin = ax2.twinx()
    rects2 = ax2_twin.plot(x_indices + bar_width/2, cat_data["Margin %"], color=colors['dark'], marker='s', linewidth=2, label="Margin %")
    
    ax2.set_ylabel("Profit ($)", fontweight="semibold")
    ax2_twin.set_ylabel("Profit Margin (%)", fontweight="semibold")
    ax2.set_xticks(x_indices)
    ax2.set_xticklabels(cat_data["Category"], fontweight="semibold")
    ax2.grid(True, linestyle='--', alpha=0.3, color=colors['grid'])
    
    ax2.set_title("Category Profitability & Profit Margins", fontsize=12, fontweight="bold", pad=10)
    fig.tight_layout()

    chart2_path = os.path.join(output_dir, "category_performance.png")
    plt.savefig(chart2_path, dpi=300)
    plt.close()
    print(f" - Saved category performance chart to: {chart2_path}")

    # -------------------------------------------------------------
    # Visualization 3: Regional Sales Distribution
    # -------------------------------------------------------------
    print("Generating Chart 3: Regional Sales Distribution...")
    region_data = df.groupby("Region").agg({"Sales": "sum", "Profit": "sum"}).reset_index().sort_values(by="Sales", ascending=False)

    plt.figure(figsize=(10, 5), dpi=150)
    plt.barh(region_data["Region"], region_data["Sales"], color=colors['primary'], height=0.6, alpha=0.85, label="Sales")
    
    # Draw vertical lines for context
    plt.grid(axis='x', linestyle='--', alpha=0.5, color=colors['grid'])
    
    # Add text labels on bars
    for index, value in enumerate(region_data["Sales"]):
        plt.text(value - (value * 0.12), index, f"${value:,.2f}", va='center', color='white', fontweight='bold', fontsize=9)

    plt.title("Region-wise Sales Performance", fontsize=13, fontweight="bold", pad=15)
    plt.xlabel("Total Sales ($)", fontweight="semibold")
    plt.ylabel("Region", fontweight="semibold")
    plt.gca().invert_yaxis()  # Put highest sales at the top
    plt.tight_layout()

    chart3_path = os.path.join(output_dir, "regional_distribution.png")
    plt.savefig(chart3_path, dpi=300)
    plt.close()
    print(f" - Saved regional sales chart to: {chart3_path}")

    # -------------------------------------------------------------
    # Visualization 4: Customer Retention & Repeat Purchase Analysis
    # -------------------------------------------------------------
    print("Generating Chart 4: Customer Purchase Behavior...")
    repeat_data = df.groupby("Is Repeat Customer").agg({"Sales": "sum", "Customer Name": "count"}).reset_index()
    repeat_data.columns = ["Repeat Customer?", "Total Sales", "Order Count"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), dpi=150)

    # Order Count Distribution
    ax1.bar(repeat_data["Repeat Customer?"], repeat_data["Order Count"], color=[colors['accent'], colors['success']], width=0.5, alpha=0.85)
    ax1.set_ylabel("Number of Orders", fontweight="semibold")
    ax1.set_xlabel("Is Repeat Customer?", fontweight="semibold")
    ax1.set_title("Order Shares: First-time vs. Repeat Customers", fontsize=11, fontweight="bold", pad=10)
    ax1.grid(True, linestyle='--', alpha=0.3, color=colors['grid'])

    # Sales Revenue Distribution
    ax2.pie(
        repeat_data["Total Sales"], 
        labels=repeat_data["Repeat Customer?"], 
        autopct='%1.1f%%',
        startangle=90, 
        colors=[colors['accent'], colors['success']],
        wedgeprops=dict(edgecolor='white', linewidth=1.5)
    )
    ax2.set_title("Revenue Breakdown by Customer Loyalty", fontsize=11, fontweight="bold", pad=10)
    
    fig.suptitle("Customer Purchase Pattern & Loyalty Metrics", fontsize=14, fontweight="bold", y=1.02)
    fig.tight_layout()

    chart4_path = os.path.join(output_dir, "customer_retention.png")
    plt.savefig(chart4_path, dpi=300)
    plt.close()
    print(f" - Saved customer retention chart to: {chart4_path}")

    print("EDA Visualizations generated successfully!\n")

if __name__ == "__main__":
    generate_eda_visualizations()
