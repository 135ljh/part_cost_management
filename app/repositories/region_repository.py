from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.region import Region


class RegionRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_regions(self) -> list[Region]:
        stmt = select(Region).order_by(Region.updated_at.desc(), Region.id.desc())
        return list(self.db.scalars(stmt).all())

    def get_by_id(self, region_id: int) -> Optional[Region]:
        return self.db.get(Region, region_id)

    def create(self, region: Region) -> Region:
        self.db.add(region)
        self.db.flush()
        self.db.refresh(region)
        return region

    def delete(self, region: Region) -> None:
        self.db.delete(region)
        self.db.flush()

