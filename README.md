# AI-Driven Inventory & Demand Dashboard

Full-stack dashboard for detecting dead stock from the UCI Online Retail dataset, scoring inventory health, and suggesting discount actions for recovery.

## Stack

- Frontend: Next.js, Tailwind CSS, Tremor, Lucide
- Backend: FastAPI, SQLAlchemy, Pandas, Scikit-learn
- Database: PostgreSQL

## What It Does

- Seeds an `inventory` table from the UCI Online Retail Excel dataset
- Falls back to a bundled sample dataset when the UCI download is unavailable
- Trains a Random Forest classifier on:
  - `unit_price`
  - `current_stock_level`
  - `days_since_last_sale`
- Flags dead stock as items unsold for more than 90 days
- Stores model output in `stock_predictions`
- Exposes `GET /inventory/health` with:
  - `total_items`
  - `dead_stock_count`
  - `at_risk_revenue`
  - top 15 highest-risk items

## Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
alembic upgrade head
python seed_data.py
python predict_stock.py
uvicorn main:app --reload
```

For Supabase, set `DATABASE_URL` to your Supabase Postgres connection string before running `alembic upgrade head`.

## Frontend Setup

```bash
cd frontend
copy .env.example .env.local
npm install
npm run dev
```

## Required Environment Variables

Backend:

- `DATABASE_URL`
- `INVENTORY_DATASET_URL` (optional; defaults to the UCI source)
- `INVENTORY_DATASET_PATH` (optional; defaults to `backend/data/online_retail_sample.csv`)

Frontend:

- `NEXT_PUBLIC_API_BASE_URL`

## API

`GET /inventory/health`

Returns aggregated KPI metrics and the top 15 SKUs ranked by dead-stock probability.
