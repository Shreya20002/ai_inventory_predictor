from datetime import UTC, datetime, timedelta

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from config import get_settings
from db import SessionLocal, ensure_schema_ready
from models import Inventory, StockPrediction
from schemas import InventoryHealthItem, InventoryHealthResponse


settings = get_settings()
app = FastAPI(title=settings.api_title)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def utc_now_naive() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


def derive_reference_now(max_last_sold_date: datetime | None) -> datetime:
    if max_last_sold_date is None:
        return utc_now_naive()

    reference_now = max_last_sold_date + timedelta(days=1)
    return min(reference_now, utc_now_naive())


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def startup() -> None:
    ensure_schema_ready()


@app.get("/healthz")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/inventory/health", response_model=InventoryHealthResponse)
def get_inventory_health(db: Session = Depends(get_db)) -> InventoryHealthResponse:
    total_items = db.scalar(select(func.count()).select_from(Inventory)) or 0
    dead_stock_count = (
        db.scalar(
            select(func.count())
            .select_from(StockPrediction)
            .where(StockPrediction.is_dead_stock.is_(True))
        )
        or 0
    )

    at_risk_revenue = (
        db.scalar(
            select(
                func.coalesce(
                    func.sum(Inventory.unit_price * Inventory.current_stock_level), 0
                )
            )
            .join(StockPrediction, StockPrediction.stock_code == Inventory.stock_code)
            .where(StockPrediction.is_dead_stock.is_(True))
        )
        or 0
    )

    latest_prediction_time = db.scalar(select(func.max(StockPrediction.last_updated)))
    max_last_sold_date = db.scalar(select(func.max(Inventory.last_sold_date)))

    reference_now = derive_reference_now(max_last_sold_date)
    rows = db.execute(
        select(Inventory, StockPrediction)
        .join(StockPrediction, StockPrediction.stock_code == Inventory.stock_code)
        .order_by(StockPrediction.dead_stock_probability.desc(), Inventory.stock_code.asc())
        .limit(15)
    ).all()

    items = []
    for inventory, prediction in rows:
        days_since_last_sale = None
        if inventory.last_sold_date is not None:
            days_since_last_sale = max((reference_now - inventory.last_sold_date).days, 0)

        items.append(
            InventoryHealthItem(
                stock_code=inventory.stock_code,
                description=inventory.description,
                category=inventory.category,
                unit_price=float(inventory.unit_price),
                current_stock_level=inventory.current_stock_level,
                last_sold_date=inventory.last_sold_date,
                days_since_last_sale=days_since_last_sale,
                dead_stock_probability=prediction.dead_stock_probability,
                is_dead_stock=prediction.is_dead_stock,
                suggested_discount=prediction.suggested_discount,
                inventory_value=float(inventory.unit_price) * inventory.current_stock_level,
            )
        )

    return InventoryHealthResponse(
        total_items=total_items,
        dead_stock_count=dead_stock_count,
        at_risk_revenue=float(at_risk_revenue),
        generated_at=latest_prediction_time or reference_now,
        items=items,
    )
