from pathlib import Path
from decimal import Decimal
from urllib.error import URLError

import pandas as pd
from sqlalchemy import delete

from config import get_settings
from db import SessionLocal, ensure_schema_ready
from models import Inventory, StockPrediction


settings = get_settings()
ROOT_DIR = Path(__file__).resolve().parent


def derive_category(description: str | None) -> str:
    if not description:
        return "Uncategorized"

    tokens = [token for token in description.split() if token.isalpha()]
    if not tokens:
        return "Uncategorized"

    return tokens[0].title()


def read_dataset(source: str) -> pd.DataFrame:
    source_path = Path(source)
    if not source_path.is_absolute():
        source_path = ROOT_DIR / source_path

    if source_path.exists():
        if source_path.suffix.lower() == ".csv":
            return pd.read_csv(source_path)
        return pd.read_excel(source_path)

    if source.lower().endswith(".csv"):
        return pd.read_csv(source)
    return pd.read_excel(source)


def load_dataset() -> pd.DataFrame:
    sources = [settings.inventory_dataset_url, settings.inventory_dataset_path]
    failures: list[str] = []

    for source in sources:
        if not source:
            continue

        try:
            return read_dataset(source)
        except (FileNotFoundError, PermissionError, URLError, OSError, ValueError) as exc:
            failures.append(f"{source}: {exc}")

    failure_details = "\n".join(failures)
    raise RuntimeError(
        "Unable to load the inventory dataset. Set INVENTORY_DATASET_URL to a reachable Excel/CSV "
        "source or INVENTORY_DATASET_PATH to a local file.\n"
        f"{failure_details}"
    )


def build_inventory_frame(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.dropna(subset=["Description", "StockCode", "InvoiceDate"]).copy()
    cleaned = cleaned[~cleaned["InvoiceNo"].astype(str).str.startswith("C")]
    cleaned = cleaned[(cleaned["Quantity"] > 0) & (cleaned["UnitPrice"] > 0)]
    cleaned["Description"] = cleaned["Description"].astype(str).str.strip()

    inventory_df = (
        cleaned.groupby("StockCode", as_index=False)
        .agg(
            description=("Description", "first"),
            unit_price=("UnitPrice", "mean"),
            current_stock_level=("Quantity", "sum"),
            last_sold_date=("InvoiceDate", "max"),
        )
        .rename(columns={"StockCode": "stock_code"})
    )

    inventory_df["unit_price"] = inventory_df["unit_price"].round(2)
    inventory_df["current_stock_level"] = inventory_df["current_stock_level"].astype(int)
    inventory_df["last_sold_date"] = pd.to_datetime(inventory_df["last_sold_date"])
    inventory_df["category"] = inventory_df["description"].apply(derive_category)
    return inventory_df


def seed_database() -> None:
    print("Loading UCI Online Retail dataset...")
    raw_df = load_dataset()
    inventory_df = build_inventory_frame(raw_df)
    ensure_schema_ready()

    records = inventory_df.to_dict(orient="records")
    with SessionLocal() as session:
        session.execute(delete(StockPrediction))
        session.execute(delete(Inventory))
        session.bulk_save_objects(
            [
                Inventory(
                    stock_code=str(record["stock_code"]).strip(),
                    description=record["description"],
                    unit_price=Decimal(str(record["unit_price"])),
                    current_stock_level=int(record["current_stock_level"]),
                    last_sold_date=record["last_sold_date"].to_pydatetime(),
                    category=record["category"],
                )
                for record in records
            ]
        )
        session.commit()

    print(f"Seeded {len(records)} inventory rows.")


if __name__ == "__main__":
    seed_database()
