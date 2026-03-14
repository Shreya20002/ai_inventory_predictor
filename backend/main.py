from fastapi import FastAPI
from sqlalchemy import create_engine
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

# Enable CORS for Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

@app.get("/inventory/health")
def get_inventory_health():
    query = """
    SELECT i.*, p.dead_stock_probability, p.suggested_discount 
    FROM inventory i
    JOIN stock_predictions p ON i.stock_code = p.stock_code
    WHERE p.is_dead_stock = TRUE
    ORDER BY p.dead_stock_probability DESC
    LIMIT 15
    """
    df = pd.read_sql(query, engine)
    
    return {
        "total_items": 4200, 
        "dead_stock_count": len(df),
        "items": df.to_dict(orient="records")
    }