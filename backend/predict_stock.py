from datetime import UTC, datetime

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sqlalchemy import delete, select

from db import SessionLocal, ensure_schema_ready
from models import Inventory, StockPrediction


def utc_now_naive() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


def derive_reference_date(last_sold_dates: pd.Series) -> pd.Timestamp:
    latest_sale = pd.to_datetime(last_sold_dates).max()
    if pd.isna(latest_sale):
        return pd.Timestamp(utc_now_naive())

    reference_date = latest_sale + pd.Timedelta(days=1)
    return min(reference_date, pd.Timestamp(utc_now_naive()))


def suggest_discount(probability: float) -> int:
    if probability > 0.8:
        return 30
    if probability >= 0.5:
        return 15
    return 0


def run_dead_stock_model() -> None:
    ensure_schema_ready()

    with SessionLocal() as session:
        inventory_rows = session.execute(select(Inventory)).scalars().all()
        if not inventory_rows:
            raise RuntimeError("Inventory table is empty. Run seed_data.py first.")

        df = pd.DataFrame(
            [
                {
                    "stock_code": row.stock_code,
                    "unit_price": float(row.unit_price),
                    "current_stock_level": row.current_stock_level,
                    "last_sold_date": row.last_sold_date,
                }
                for row in inventory_rows
            ]
        )

        df["last_sold_date"] = pd.to_datetime(df["last_sold_date"])
        reference_date = derive_reference_date(df["last_sold_date"])
        df["days_since_last_sale"] = (
            reference_date - df["last_sold_date"]
        ).dt.days.clip(lower=0)
        df["is_dead_stock"] = (df["days_since_last_sale"] > 90).astype(int)

        feature_columns = ["unit_price", "current_stock_level", "days_since_last_sale"]
        X = df[feature_columns]
        y = df["is_dead_stock"]

        if y.nunique() < 2:
            df["dead_stock_probability"] = y.astype(float)
        else:
            model = RandomForestClassifier(
                n_estimators=300,
                random_state=42,
                class_weight="balanced_subsample",
            )
            model.fit(X, y)
            df["dead_stock_probability"] = model.predict_proba(X)[:, 1]

        df["suggested_discount"] = df["dead_stock_probability"].apply(suggest_discount)
        df["is_dead_stock"] = df["days_since_last_sale"] > 90

        session.execute(delete(StockPrediction))
        session.bulk_save_objects(
            [
                StockPrediction(
                    stock_code=row.stock_code,
                    dead_stock_probability=float(row.dead_stock_probability),
                    is_dead_stock=bool(row.is_dead_stock),
                    suggested_discount=int(row.suggested_discount),
                    last_updated=utc_now_naive(),
                )
                for row in df.itertuples(index=False)
            ]
        )
        session.commit()

    print(f"Generated predictions for {len(df)} inventory items.")


if __name__ == "__main__":
    run_dead_stock_model()
