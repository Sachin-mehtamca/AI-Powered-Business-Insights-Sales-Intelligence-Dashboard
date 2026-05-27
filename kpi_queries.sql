-- ==============================================================
-- KPI Queries: Sales Performance Tracking
-- Calculates core metrics for sales, profit, orders, and growth
-- ==============================================================

-- 1. Total Revenue, Total Profit, Average Profit Margin, and Total Quantity Sold
SELECT 
    ROUND(SUM(sales), 2) AS total_revenue,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND((SUM(profit) / SUM(sales)) * 100, 2) AS average_profit_margin_pct,
    SUM(quantity) AS total_units_sold,
    COUNT(DISTINCT order_id) AS total_orders
FROM orders;


-- 2. Average Order Value (AOV)
SELECT 
    ROUND(SUM(sales) / COUNT(DISTINCT order_id), 2) AS average_order_value
FROM orders;


-- 3. Region-wise Sales Performance & Profit Margins
SELECT 
    region,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND((SUM(profit) / SUM(sales)) * 100, 2) AS profit_margin_pct
FROM orders
GROUP BY region
ORDER BY total_sales DESC;


-- 4. Product Category Contribution & Performance
SELECT 
    category,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND((SUM(profit) / SUM(sales)) * 100, 2) AS profit_margin_pct,
    SUM(quantity) AS total_quantity_sold
FROM orders
GROUP BY category
ORDER BY total_sales DESC;


-- 5. Month-over-Month (MoM) Sales & Profit Growth
-- Employs CTEs and LAG() window function to calculate growth rate
WITH MonthlySales AS (
    SELECT 
        DATE_FORMAT(order_date, '%Y-%m') AS sales_month,
        SUM(sales) AS monthly_sales,
        SUM(profit) AS monthly_profit
    FROM orders
    GROUP BY DATE_FORMAT(order_date, '%Y-%m')
)
SELECT 
    sales_month,
    ROUND(monthly_sales, 2) AS current_month_sales,
    ROUND(LAG(monthly_sales, 1) OVER (ORDER BY sales_month), 2) AS prior_month_sales,
    ROUND(((monthly_sales - LAG(monthly_sales, 1) OVER (ORDER BY sales_month)) / LAG(monthly_sales, 1) OVER (ORDER BY sales_month)) * 100, 2) AS sales_growth_pct,
    ROUND(monthly_profit, 2) AS current_month_profit,
    ROUND(LAG(monthly_profit, 1) OVER (ORDER BY sales_month), 2) AS prior_month_profit,
    ROUND(((monthly_profit - LAG(monthly_profit, 1) OVER (ORDER BY sales_month)) / LAG(monthly_profit, 1) OVER (ORDER BY sales_month)) * 100, 2) AS profit_growth_pct
FROM MonthlySales
ORDER BY sales_month;
