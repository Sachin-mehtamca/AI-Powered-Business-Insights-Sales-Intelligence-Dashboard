-- ==============================================================
-- Business Intelligence Reports: Customer and Sales Dynamics
-- Contains advanced analytics and analytical reports
-- ==============================================================

-- 1. High-Value Customer Identification (CLV Proxy)
-- Identifies top 15 customers contributing most to total sales and profit
SELECT 
    customer_name,
    COUNT(DISTINCT order_id) AS order_count,
    SUM(quantity) AS items_purchased,
    ROUND(SUM(sales), 2) AS total_spent,
    ROUND(SUM(profit), 2) AS total_profit_contributed,
    ROUND((SUM(profit) / SUM(sales)) * 100, 2) AS customer_margin_pct
FROM orders
GROUP BY customer_name
ORDER BY total_spent DESC
LIMIT 15;


-- 2. Customer Retention & Repeat Purchase Analysis
-- Compares sales share, profit, and metrics between new and repeat customers
SELECT 
    is_repeat_customer,
    COUNT(DISTINCT customer_name) AS unique_customers_count,
    COUNT(DISTINCT order_id) AS total_orders_placed,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND((SUM(sales) / (SELECT SUM(sales) FROM orders)) * 100, 2) AS sales_revenue_share_pct
FROM orders
GROUP BY is_repeat_customer;


-- 3. Weekend vs. Weekday Sales Analysis
-- Tracks the 35% weekend sales growth trend
SELECT 
    CASE 
        WHEN DAYOFWEEK(order_date) IN (1, 7) THEN 'Weekend (Sat/Sun)'
        ELSE 'Weekday (Mon-Fri)'
    END AS day_type,
    COUNT(DISTINCT order_id) AS orders_count,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(AVG(sales), 2) AS average_order_value,
    ROUND(SUM(profit), 2) AS total_profit
FROM orders
GROUP BY 
    CASE 
        WHEN DAYOFWEEK(order_date) IN (1, 7) THEN 'Weekend (Sat/Sun)'
        ELSE 'Weekday (Mon-Fri)'
    END;


-- 4. Deep Dive: Product Sub-Category Performance Analysis
-- Evaluates margins, total revenue, and profit ratios per sub-category
SELECT 
    category,
    sub_category,
    ROUND(SUM(sales), 2) AS subcat_sales,
    ROUND(SUM(profit), 2) AS subcat_profit,
    ROUND((SUM(profit) / SUM(sales)) * 100, 2) AS profit_margin_pct,
    SUM(quantity) AS units_sold,
    DENSE_RANK() OVER (PARTITION BY category ORDER BY SUM(sales) DESC) AS rank_in_category
FROM orders
GROUP BY category, sub_category
ORDER BY category, subcat_sales DESC;


-- 5. Regional Growth Trajectory (Year-over-Year Performance)
-- Evaluates region-wise expansion across multiple years
SELECT 
    region,
    EXTRACT(YEAR FROM order_date) AS order_year,
    ROUND(SUM(sales), 2) AS annual_sales,
    ROUND(SUM(profit), 2) AS annual_profit,
    ROUND((SUM(profit) / SUM(sales)) * 100, 2) AS annual_margin_pct
FROM orders
GROUP BY region, EXTRACT(YEAR FROM order_date)
ORDER BY region, order_year;
