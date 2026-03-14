import pandas as pd
from sqlalchemy import create_engine, text
from sklearn.ensemble import RandomForestClassifier
from datetime import datetime

# DB Setup
DB_URL = "postgresql://user:password@host:5432/postgres"
engine = create_engine(DB_URL)

def run_dead_stock_model():
    print(" Fetching inventory data for AI analysis...")
    
    # 1. Load Data
    query = "SELECT * FROM inventory"
    df = pd.read_sql(query, engine)
    
    # 2. Feature Engineering
    # Convert dates and calculate age of stock
    df['last_sold_date'] = pd.to_datetime(df['last_sold_date'])
    reference_date = df['last_sold_date'].max() # Use latest date in dataset as "today"
    
    df['days_idle'] = (reference_date - df['last_sold_date']).dt.days
    
    # Target Label: 1 if idle > 90 days, else 0
    df['is_dead'] = (df['days_idle'] > 90).astype(int)
    
    # Features for the model: Price and Current Stock Level
    # (In a real scenario, we'd add historical volatility)
    X = df[['unit_price', 'current_stock_level', 'days_idle']]
    y = df['is_dead']
    
    # 3. Train Model
    print(" Training Random Forest Classifier...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    # 4. Generate Predictions & Suggestions
    df['dead_stock_probability'] = model.predict_proba(X)[:, 1]
    
    # Logic for Discount Suggestion: 
    # High prob (>0.8) -> 30% off | Med prob (0.5-0.8) -> 15% off | Else 0
    def suggest_discount(prob):
        if prob > 0.8: return 30
        if prob > 0.5: return 15
        return 0

    df['suggested_discount'] = df['dead_stock_probability'].apply(suggest_discount)
    
    # 5. Push Results to stock_predictions table
    print(" Updating predictions in database...")
    
    # Clean up results for the DB
    results = df[['stock_code', 'dead_stock_probability', 'is_dead', 'suggested_discount']]
    results.columns = ['stock_code', 'dead_stock_probability', 'is_dead_stock', 'suggested_discount']
    
    # Clear old predictions and insert new ones
    with engine.connect() as conn:
        conn.execute(text("TRUNCATE TABLE stock_predictions"))
        conn.commit()
        
    results.to_sql('stock_predictions', engine, if_exists='append', index=False)
    print(" Prediction engine complete!")

if __name__ == "__main__":
    run_dead_stock_model()