from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import Base


def utc_now_naive() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class Inventory(Base):
    __tablename__ = "inventory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    stock_code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    unit_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    current_stock_level: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    last_sold_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=False))
    category: Mapped[str | None] = mapped_column(String(100))

    prediction: Mapped["StockPrediction | None"] = relationship(
        back_populates="inventory",
        uselist=False,
        cascade="all, delete-orphan",
    )


class StockPrediction(Base):
    __tablename__ = "stock_predictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    stock_code: Mapped[str] = mapped_column(
        String(50), ForeignKey("inventory.stock_code"), unique=True, nullable=False
    )
    dead_stock_probability: Mapped[float] = mapped_column(Float, nullable=False)
    is_dead_stock: Mapped[bool] = mapped_column(Boolean, nullable=False)
    suggested_discount: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=utc_now_naive, nullable=False)

    inventory: Mapped[Inventory] = relationship(back_populates="prediction")
