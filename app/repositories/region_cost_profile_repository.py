from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.region_cost_profile import RegionCostProfile


class RegionCostProfileRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_profiles(self) -> list[RegionCostProfile]:
        stmt = select(RegionCostProfile).order_by(
            RegionCostProfile.updated_at.desc(), RegionCostProfile.id.desc()
        )
        return list(self.db.scalars(stmt).all())

    def get_by_id(self, profile_id: int) -> Optional[RegionCostProfile]:
        return self.db.get(RegionCostProfile, profile_id)

    def create(self, profile: RegionCostProfile) -> RegionCostProfile:
        self.db.add(profile)
        self.db.flush()
        self.db.refresh(profile)
        return profile

    def delete(self, profile: RegionCostProfile) -> None:
        self.db.delete(profile)
        self.db.flush()

