import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_superstore_dataset(num_records=3000, output_path="data/raw_sales_data.csv"):
    print("Initializing synthetic e-commerce dataset generation...")
    np.random.seed(42)  # For reproducibility

    # Ensure target folder exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # 1. Generate Customer Pool
    first_names = ["James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Charles",
                   "Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", "Jessica", "Sarah", "Karen",
                   "Christopher", "Nancy", "Lisa", "Betty", "Margaret", "Sandra", "Ashley", "Kimberly", "Emily", "Donna"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
                  "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
                  "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson"]
    
    # Create 150 unique customers to guarantee repeat customers
    customers = [f"{np.random.choice(first_names)} {np.random.choice(last_names)}" for _ in range(150)]
    customer_purchase_weights = np.random.zipf(1.6, size=150) # Zipf distribution for realistic high-value/frequent customers
    customer_purchase_weights = customer_purchase_weights / customer_purchase_weights.sum()

    # 2. Product and Category Structure with standard pricing ranges
    product_catalog = {
        "Electronics": {
            "Phones": (200, 1000, 0.15),       # (MinPrice, MaxPrice, TargetProfitMargin)
            "Laptops": (500, 2000, 0.12),
            "Accessories": (15, 120, 0.35),
            "Smartwatches": (100, 400, 0.20)
        },
        "Furniture": {
            "Chairs": (80, 450, 0.08),
            "Tables": (150, 800, -0.05),        # Selling tables at a loss is common in promotions
            "Bookcases": (100, 600, 0.05),
            "Furnishings": (10, 150, 0.25)
        },
        "Office Supplies": {
            "Paper": (5, 40, 0.45),
            "Binders": (2, 25, 0.50),
            "Storage": (30, 250, 0.20),
            "Art": (5, 80, 0.40)
        }
    }

    categories = list(product_catalog.keys())
    category_weights = [0.35, 0.25, 0.40] # Office Supplies has highest volume

    regions = ["Central", "East", "South", "West"]
    region_weights = [0.22, 0.28, 0.18, 0.32] # West is the highest performing region

    # 3. Generate Timestamps (Jan 1, 2024 to May 25, 2026)
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2026, 5, 25)
    delta_days = (end_date - start_date).days

    records = []
    customer_history = set()  # Track seen customers to mark repeat purchase dynamics

    for i in range(num_records):
        # Determine Date with seasonality
        random_day = np.random.randint(0, delta_days + 1)
        order_date = start_date + timedelta(days=random_day)
        
        # Calculate date features
        month = order_date.month
        day_of_week = order_date.weekday() # 5 = Saturday, 6 = Sunday

        # Basic customer assignment
        customer_name = np.random.choice(customers, p=customer_purchase_weights)
        is_repeat = "Yes" if customer_name in customer_history else "No"
        customer_history.add(customer_name)

        # Select Category, Sub-Category, and Product details
        category = np.random.choice(categories, p=category_weights)
        sub_categories = list(product_catalog[category].keys())
        sub_category = np.random.choice(sub_categories)
        min_p, max_p, margin = product_catalog[category][sub_category]
        
        # Generate base cost, quantity, and base sales
        base_unit_price = np.random.uniform(min_p, max_p)
        quantity = int(np.random.choice([1, 2, 3, 4, 5], p=[0.4, 0.3, 0.15, 0.1, 0.05]))
        sales = base_unit_price * quantity
        
        # Regional modifiers
        region = np.random.choice(regions, p=region_weights)
        if region == "West":
            sales *= 1.10 # West region sales are slightly higher
        elif region == "South":
            sales *= 0.95

        # Seasonality adjustments (Holiday season boost in Nov/Dec, Summer dip in July)
        seasonality_factor = 1.0
        if month in [11, 12]:
            seasonality_factor = 1.35  # Holiday sales lift
        elif month == 7:
            seasonality_factor = 0.85  # Summer dip

        # Weekend boost adjustment (Saturday / Sunday sales show a 35% growth boost)
        weekend_factor = 1.0
        if day_of_week in [5, 6]:
            weekend_factor = 1.35

        # Finalize Sales with factors
        sales = round(sales * seasonality_factor * weekend_factor, 2)

        # Calculate Profit based on base cost margin + random fluctuation (-5% to +5% variation)
        noise = np.random.uniform(-0.05, 0.05)
        effective_margin = margin + noise
        profit = round(sales * effective_margin, 2)

        # Generate Order ID
        year_str = order_date.strftime("%Y")
        order_id = f"CA-{year_str}-{100000 + i}"

        records.append({
            "Order ID": order_id,
            "Order Date": order_date.strftime("%Y-%m-%d"),
            "Customer Name": customer_name,
            "Category": category,
            "Sub-Category": sub_category,
            "Sales": sales,
            "Profit": profit,
            "Quantity": quantity,
            "Region": region,
            "Is Repeat Customer": is_repeat
        })

    # Sort by date for chronological consistency
    df = pd.DataFrame(records)
    df = df.sort_values(by="Order Date").reset_index(drop=True)
    
    # Double check repeat customer column based on chronological sorting
    seen_customers = set()
    for idx, row in df.iterrows():
        cust = row["Customer Name"]
        if cust in seen_customers:
            df.at[idx, "Is Repeat Customer"] = "Yes"
        else:
            df.at[idx, "Is Repeat Customer"] = "No"
            seen_customers.add(cust)

    # Save to file
    df.to_csv(output_path, index=False)
    print(f"Dataset generated successfully! Created {len(df)} records at: {output_path}")
    return df

if __name__ == "__main__":
    generate_superstore_dataset()
