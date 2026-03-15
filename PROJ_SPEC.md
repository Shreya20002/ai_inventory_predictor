# 📄 PROJECT_SPEC.md: AI-Driven Inventory & Demand Dashboard

## 1. Project Overview
Build a full-stack dashboard that identifies "Dead Stock" (items unsold for >90 days) using the UCI Online Retail dataset. The tool provides a probability score for stock health and suggests dynamic discount percentages to recover capital.

## 2. Tech Stack
- **Frontend:** Next.js , Tailwind CSS, Tremor (Dashboard UI).
- **Backend:** FastAPI (Python 3.11+), SQLAlchemy, Pandas, Scikit-learn.
- **Database:** PostgreSQL (Supabase).
- **Icons:** Lucide-react.

---

## 3. Database Schema (PostgreSQL)
```sql
CREATE TABLE inventory (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(50) UNIQUE,
    description TEXT,
    unit_price NUMERIC(10, 2),
    current_stock_level INTEGER DEFAULT 100,
    last_sold_date TIMESTAMP,
    category VARCHAR(100)
);

CREATE TABLE stock_predictions (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(50) REFERENCES inventory(stock_code),
    dead_stock_probability FLOAT,
    is_dead_stock BOOLEAN,
    suggested_discount INTEGER,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

4. Key Functionalities
A. Data Ingestion (seed_data.py)
Source: UCI Online Retail Dataset (.xlsx).

Logic: Clean negative quantities, aggregate transactions by StockCode, find the max(InvoiceDate) as last_sold_date.

Output: Populate the inventory table.

B. AI Engine (predict_stock.py)
Model: Random Forest Classifier (Scikit-learn).

Features: unit_price, current_stock_level, days_since_last_sale.

Labeling: Binary (1 if days_since_last_sale > 90, else 0).

Prescriptive Logic:

Prob > 0.8: 30% discount suggestion.

Prob 0.5-0.8: 15% discount suggestion.

Output: Populate/Update stock_predictions table.

C. Backend API (main.py)
Endpoint: GET /inventory/health.

Logic: Perform a SQL JOIN between inventory and stock_predictions. Return total count, dead stock count, and top 15 highest-risk items.

D. Frontend Dashboard (app/page.tsx)
UI Library: Tremor.

Features:

KPI Cards: Total Items, Dead Stock Count, At-Risk Revenue.

AI Metrics: Display dead_stock_probability using a Tremor ProgressBar.

Actions: Display suggested_discount as a clearance recommendation.