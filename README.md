#  AI-Driven Inventory & Demand Forecasting Dashboard

A full-stack predictive analytics tool designed to identify "Dead Stock" (inventory idle for >90 days) and provide prescriptive discount recommendations to optimize retail margins.

##  The Problem
Retailers lose billions annually to "Dead Stock"—inventory that takes up warehouse space without generating revenue. This project identifies these items before they become a total loss and suggests recovery strategies.

##  Tech Stack
* **Frontend:** Next.js 15 (App Router), Tailwind CSS, Tremor (Dashboard UI)
* **Backend:** FastAPI (Python), SQLAlchemy, Pydantic
* **AI/ML:** Scikit-learn (Random Forest Classifier), Pandas, NumPy
* **Database:** PostgreSQL (Supabase/Neon)

##  System Architecture
1.  **Data Ingestion:** Processes the UCI Online Retail dataset (~500k records).
2.  **Feature Engineering:** Calculates "Days Since Last Sale," "Stock Velocity," and "Price Elasticity."
3.  **ML Inference:** A Random Forest model calculates a **Dead Stock Probability Score** (0.0 - 1.0).
4.  **Prescriptive Logic:** The system maps probability scores to dynamic discount tiers (15%, 30%, etc.) to maximize clearance efficiency.

##  Key Features
* **Probability Metric:** High-precision forecasting of which SKUs are likely to remain unsold.
* **Dynamic Discount Engine:** Automated pricing suggestions based on AI confidence levels.
* **KPI Overview:** Instant visibility into "At-Risk Revenue" and "Dead Stock Count."

##  Setup & Installation

### 1. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python seed_data.py       # Seeds the database with UCI data
python predict_stock.py   # Runs the initial AI inference
uvicorn main:app --reload

### 2. Frontend Setup
