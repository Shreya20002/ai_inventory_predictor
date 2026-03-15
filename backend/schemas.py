from datetime import datetime

from pydantic import BaseModel


class InventoryHealthItem(BaseModel):
    stock_code: str
    description: str | None
    category: str | None
    unit_price: float
    current_stock_level: int
    last_sold_date: datetime | None
    days_since_last_sale: int | None
    dead_stock_probability: float
    is_dead_stock: bool
    suggested_discount: int
    inventory_value: float


class InventoryHealthResponse(BaseModel):
    total_items: int
    dead_stock_count: int
    at_risk_revenue: float
    generated_at: datetime
    items: list[InventoryHealthItem]
