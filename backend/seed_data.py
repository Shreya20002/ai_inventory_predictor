import pandas as pd
from sqlalchemy import create_engine
import datetime

# 1. Database Configuration
# REPLACE with your actual connection string
DB_URL = "postgresql://user:password@host:5432/dbname"
engine = create_engine(DB_URL)

def seed_database():
    print(" Starting data seeding process...")
    
    # 2. Download UCI Retail Dataset
    # Using a direct raw link to ensure it works without manual downloads
    url = "https://archive.ics.uci.edu/ml/machine-learning-databases/00352/Online%20Retail.xlsx"
    
    print(" Downloading dataset (this may take a minute, ~23MB)...")
    try:
        # Note: requires 'openpyxl' (pip install openpyxl)
        df = pd.read_excel(url)
    except Exception as e:
        print(f" Download failed: {e}")
        return

    print(f"✅ Downloaded {len(df)} rows. Cleaning data...")

    # 3. Data Cleaning
    # Remove rows with no Description or CustomerID
    df = df.dropna(subset=['Description', 'CustomerID'])
    
    # Remove cancellations (InvoiceNo starting with 'C') and non-positive values
    df = df[~df['InvoiceNo'].astype(str).str.startswith('C')]
    df = df[(df['Quantity'] > 0) & (df['UnitPrice'] > 0)]
    
    # Clean strings
    df['Description'] = df['Description'].str.strip()
    
    # 4. Transform for our 'inventory' table schema
    # We aggregate the transactional data into a unique 'per product' inventory view
    inventory_df = df.groupby('StockCode').agg({
        'Description': 'first',
        'UnitPrice': 'mean',
        'Quantity': 'sum',
        'InvoiceDate': 'max'
    }).reset_index()

    # Rename columns to match our SQL schema
    inventory_df.columns = [
        'stock_code', 'description', 'unit_price', 
        'current_stock_level', 'last_sold_date'
    ]

    # 5. Push to PostgreSQL
    print(f" Pushing {len(inventory_df)} unique items to PostgreSQL...")
    try:
        inventory_df.to_sql('inventory', engine, if_exists='append', index=False)
        print(" Database successfully seeded!")
    except Exception as e:
        print(f" Database push failed: {e}")

if __name__ == "__main__":
    seed_database()