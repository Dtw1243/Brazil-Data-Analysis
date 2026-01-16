import pandas as pd
import sqlite3
import os

print(os.getcwd())

orders = pd.read_csv('data/orders.csv')
order_items = pd.read_csv('data/order_items.csv')
products = pd.read_csv('data/products.csv')
customers = pd.read_csv('data/customers.csv')

# Show first 3 rows of each
print(orders.head(3))
print(order_items.head(3))
print(products.head(3))
print(customers.head(3))

# Check row counts
print(orders.shape)
print(order_items.shape)
print(products.shape)
print(customers.shape)

# Check column names
print(orders.columns)
print(order_items.columns)
print(products.columns)
print(customers.columns)

orders.info()
order_items.info()
products.info()
customers.info()

orders['order_purchase_timestamp'] = pd.to_datetime(orders['order_purchase_timestamp'], errors='coerce')
orders['order_delivered_customer_date'] = pd.to_datetime(orders['order_delivered_customer_date'], errors='coerce')

print(orders.isnull().sum().sort_values(ascending=False))
print(order_items.isnull().sum())
print(products.isnull().sum())
print(customers.isnull().sum())


# Orders table: order_id should be unique
print(orders['order_id'].nunique() == len(orders))

# Order items table: order_id + order_item_id should be unique
print(order_items[['order_id','order_item_id']].duplicated().sum())

# Join test: all orders exist in order_items
print(orders['order_id'].isin(order_items['order_id']).mean())


# Create a SQLite database in your project folder
conn = sqlite3.connect('olist.db')

# Load tables
orders.to_sql('orders', conn, if_exists='replace', index=False)
order_items.to_sql('order_items', conn, if_exists='replace', index=False)
products.to_sql('products', conn, if_exists='replace', index=False)
customers.to_sql('customers', conn, if_exists='replace', index=False)

# Verify tables exist
print(pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", conn))

# Count total orders
print(pd.read_sql("SELECT COUNT(*) AS total_orders FROM orders;", conn))

# Count total revenue
print(pd.read_sql("SELECT SUM(price) AS total_revenue FROM order_items;", conn))

query = """
SELECT
    strftime('%Y-%m', o.order_purchase_timestamp) AS month,
    SUM(oi.price) AS revenue
FROM orders o
JOIN order_items oi
    ON o.order_id = oi.order_id
GROUP BY month
ORDER BY month;
"""

revenue_df = pd.read_sql(query, conn)
revenue_df.head()



#inspect the data
print(revenue_df.head())
print(revenue_df.info())
print(revenue_df.describe())

#a little data cleaning
revenue_df['month'] = pd.to_datetime(revenue_df['month'])

#then visualize
import matplotlib.pyplot as plt

plt.figure(figsize=(12,6))
plt.plot(revenue_df['month'], revenue_df['revenue'], marker='o')
plt.title('Monthly Revenue Trend')
plt.xlabel('Month')
plt.ylabel('Revenue (BRL)')
plt.xticks(rotation=45)
plt.grid(True)
plt.show()



#saving to a different file name 
revenue_df.to_csv('monthly_revenue.csv', index=False)
