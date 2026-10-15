from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel
from sqlalchemy.dialects.postgresql import insert

from src.db.connection import get_session
from src.db.models import Asset

# parents[2] = project root (load_universe.py -> ingest -> src -> root)
CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "universe.yaml"


class AssetConfig(BaseModel):
    """One asset entry; invalid labels are rejected before reaching the database."""

    ticker: str
    name: str
    asset_class: Literal["equity", "fixed_income", "commodity", "cash"]
    region: Literal["us", "developed_ex_us", "emerging", "global"]


def load_config(path: Path = CONFIG_PATH) -> list[AssetConfig]:
    with path.open() as f:
        raw = yaml.safe_load(f)  # safe_load never executes code hidden in YAML
    assets = [AssetConfig(**item) for item in raw["assets"]]

    tickers = [a.ticker for a in assets]
    if len(tickers) != len(set(tickers)):
        raise ValueError("Duplicate tickers in universe.yaml")
    return assets


def upsert_assets(assets: list[AssetConfig]) -> int:
    rows = [a.model_dump() for a in assets]
    stmt = insert(Asset).values(rows)
    stmt = stmt.on_conflict_do_update(
        index_elements=[Asset.ticker],  # the column that defines "same row"
        set_={
            "name": stmt.excluded.name,  # excluded = the values we tried to insert
            "asset_class": stmt.excluded.asset_class,
            "region": stmt.excluded.region,
        },
    )
    with get_session() as session:
        session.execute(stmt)
    return len(rows)


def main() -> None:
    assets = load_config()
    count = upsert_assets(assets)
    print(f"Upserted {count} assets")


if __name__ == "__main__":
    main()
