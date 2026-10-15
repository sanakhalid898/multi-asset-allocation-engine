"""Database tables, defined as SQLAlchemy models."""

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    JSON,
    BigInteger,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Asset(Base):
    """One row per ETF in the investable universe (loaded from config/universe.yaml)."""

    __tablename__ = "assets"

    ticker: Mapped[str] = mapped_column(String(10), primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    asset_class: Mapped[str] = mapped_column(String(30))
    region: Mapped[str] = mapped_column(String(30))


class PriceDaily(Base):
    """Daily adjusted close and volume. Ticker + date is unique, so reloads never duplicate."""

    __tablename__ = "prices_daily"

    ticker: Mapped[str] = mapped_column(ForeignKey("assets.ticker"), primary_key=True)
    date: Mapped[date] = mapped_column(Date, primary_key=True)
    adj_close: Mapped[Decimal] = mapped_column(Numeric(18, 6))
    volume: Mapped[int | None] = mapped_column(BigInteger)


class MacroSeries(Base):
    """Macro observations from FRED, e.g. DGS10 (10-year Treasury yield)."""

    __tablename__ = "macro_series"

    series_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    date: Mapped[date] = mapped_column(Date, primary_key=True)
    value: Mapped[Decimal] = mapped_column(Numeric(18, 6))


class IngestionRun(Base):
    """Audit log: one row per data load, whether it succeeded or failed."""

    __tablename__ = "ingestion_runs"

    run_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(String(20))  # "prices" or "macro"
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(20))  # "running", "success", "failed"
    rows_loaded: Mapped[int | None] = mapped_column(Integer)
    error: Mapped[str | None] = mapped_column(Text)


class PortfolioRun(Base):
    """One row per optimization, with everything needed to reproduce it."""

    __tablename__ = "portfolio_runs"

    run_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    as_of_date: Mapped[date] = mapped_column(Date)
    method: Mapped[str] = mapped_column(String(50))  # e.g. "min_variance", "max_sharpe"
    params: Mapped[dict[str, Any]] = mapped_column(JSON)
    weights: Mapped[dict[str, float]] = mapped_column(JSON)
    git_sha: Mapped[str | None] = mapped_column(String(40))
