from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import declarative_base, sessionmaker

from config import get_settings


settings = get_settings()
REQUIRED_TABLES = ("inventory", "stock_predictions")

engine = create_engine(settings.database_url, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()


def get_missing_tables() -> list[str]:
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    return [table_name for table_name in REQUIRED_TABLES if table_name not in existing_tables]


def ensure_schema_ready() -> None:
    missing_tables = get_missing_tables()
    if missing_tables:
        missing_list = ", ".join(missing_tables)
        raise RuntimeError(
            f"Database schema is not initialized. Missing tables: {missing_list}. "
            "Run `alembic upgrade head` before starting the API or data scripts."
        )
