-- ==========================================
-- Schema Definition: AI-Powered Sales Dashboard
-- Compatible with MySQL, PostgreSQL, and SQL Server
-- ==========================================

-- Create Database if not exists (MySQL syntax example)
CREATE DATABASE IF NOT EXISTS sales_intelligence_db;
USE sales_intelligence_db;

-- Drop table if exists to allow fresh installations
DROP TABLE IF EXISTS orders;

-- Create Orders Table
CREATE TABLE orders (
    order_id VARCHAR(50) NOT NULL PRIMARY KEY,
    order_date DATE NOT NULL,
    customer_name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    sub_category VARCHAR(50) NOT NULL,
    sales DECIMAL(10, 2) NOT NULL,
    profit DECIMAL(10, 2) NOT NULL,
    quantity INT NOT NULL,
    region VARCHAR(50) NOT NULL,
    is_repeat_customer VARCHAR(5) NOT NULL,
    
    -- Performance Indexes
    INDEX idx_order_date (order_date),
    INDEX idx_category (category),
    INDEX idx_region (region),
    INDEX idx_customer (customer_name)
);

-- Comments / Metadata
-- This table structure matches the E-Commerce / Superstore Dataset columns exactly.
-- Run python data_cleaning.py to process raw csv data before importing into this database.
