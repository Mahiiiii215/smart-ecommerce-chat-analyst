import pandas as pd
import duckdb
import os

# Define paths
data_path = "data"
db_path = "ecommerce.duckdb"

# Load main CSVs
orders = pd.read_csv(os.path.join(data_path, "olist_orders_dataset.csv"))
customers = pd.read_csv(os.path.join(data_path, "olist_customers_dataset.csv"))
items = pd.read_csv(os.path.join(data_path, "olist_order_items_dataset.csv"))
products = pd.read_csv(os.path.join(data_path, "olist_products_dataset.csv"))
payments = pd.read_csv(os.path.join(data_path, "olist_order_payments_dataset.csv"))
reviews = pd.read_csv(os.path.join(data_path, "olist_order_reviews_dataset.csv"))
catmap = pd.read_csv(os.path.join(data_path, "product_category_name_translation.csv"))

# Merge tables
merged = (
    orders
    .merge(customers, on="customer_id", how="left")
    .merge(items, on="order_id", how="left")
    .merge(products, on="product_id", how="left")
    .merge(payments, on="order_id", how="left")
    .merge(catmap, on="product_category_name", how="left")
)

# Save to DuckDB
con = duckdb.connect(db_path)
con.execute("DROP TABLE IF EXISTS ecommerce")
con.execute("CREATE TABLE ecommerce AS SELECT * FROM merged")
con.close()

print(f"✅ Database ready at {db_path}, rows: {len(merged)}")
