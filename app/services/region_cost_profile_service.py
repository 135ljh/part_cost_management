import random
from datetime import datetime
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.currency import Currency
from app.models.region import Region
from app.models.region_cost_profile import RegionCostProfile
from app.repositories.region_cost_profile_repository import RegionCostProfileRepository
from app.schemas.region_cost_profile import (
    RegionCostProfileCreate,
    RegionCostProfileRead,
    RegionCostProfileUpdate,
)


class RegionCostProfileService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = RegionCostProfileRepository(db)

    def _generate_code(self) -> str:
        return f"RCP{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(100,999)}"

    def _validate_fk(self, region_id: int, currency_id: int) -> None:
        if not self.db.get(Region, region_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="区域不存在")
        if not self.db.get(Currency, currency_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="基础货币不存在")

    def _region_levels(self, region_id: int) -> dict[str, str | None]:
        levels = {
            "country": None,
            "province": None,
            "city": None,
            "district": None,
            "street": None,
        }
        current = self.db.get(Region, region_id)
        visited: set[int] = set()
        while current and current.id not in visited:
            visited.add(current.id)
            rtype = (current.region_type or "").upper()
            if rtype in ("COUNTRY", "NATION"):
                levels["country"] = current.region_name
            elif rtype in ("PROVINCE", "STATE"):
                levels["province"] = current.region_name
            elif rtype in ("CITY",):
                levels["city"] = current.region_name
            elif rtype in ("DISTRICT", "COUNTY"):
                levels["district"] = current.region_name
            elif rtype in ("STREET", "TOWN"):
                levels["street"] = current.region_name
            current = self.db.get(Region, current.parent_id) if current.parent_id else None
        return levels

    def _to_read(self, profile: RegionCostProfile) -> RegionCostProfileRead:
        base = RegionCostProfileRead.model_validate(profile)
        levels = self._region_levels(profile.region_id)
        return base.model_copy(
            update={
                "country": levels["country"],
                "province": levels["province"],
                "city": levels["city"],
                "district": levels["district"],
                "street": levels["street"],
                "factory_name": profile.supplier_name,
                "factory_code": profile.supplier_code,
            }
        )

    def list_profiles(self) -> list[RegionCostProfileRead]:
        return [self._to_read(x) for x in self.repo.list_profiles()]

    def get_profile_detail(self, profile_id: int) -> RegionCostProfileRead:
        profile = self.repo.get_by_id(profile_id)
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="区域成本配置不存在")
        return self._to_read(profile)

    def create_profile(self, payload: RegionCostProfileCreate) -> RegionCostProfileRead:
        self._validate_fk(payload.region_id, payload.currency_id)
        profile = RegionCostProfile(
            profile_code=payload.profile_code or self._generate_code(),
            profile_name=payload.profile_name,
            region_id=payload.region_id,
            supplier_name=payload.supplier_name,
            supplier_code=payload.supplier_code,
            currency_id=payload.currency_id,
            operating_worker_rate=payload.operating_worker_rate,
            skilled_worker_rate=payload.skilled_worker_rate,
            transfer_technician_rate=payload.transfer_technician_rate,
            production_leader_rate=payload.production_leader_rate,
            inspector_rate=payload.inspector_rate,
            engineer_rate=payload.engineer_rate,
            mold_fitter_rate=payload.mold_fitter_rate,
            cost_interest_rate=payload.cost_interest_rate,
            benefits_one_shift=payload.benefits_one_shift,
            benefits_two_shift=payload.benefits_two_shift,
            benefits_three_shift=payload.benefits_three_shift,
            factory_rent=payload.factory_rent,
            office_fee=payload.office_fee,
            electricity_fee=payload.electricity_fee,
            water_fee=payload.water_fee,
            gas_fee=payload.gas_fee,
            effective_from=payload.effective_from,
            effective_to=payload.effective_to,
            is_active=1 if payload.is_active else 0,
            remark=payload.remark,
        )
        try:
            created = self.repo.create(profile)
            self.db.commit()
            return self._to_read(created)
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="创建失败：编码重复或数据约束冲突"
            )

    def update_profile(
        self, profile_id: int, payload: RegionCostProfileUpdate
    ) -> RegionCostProfileRead:
        profile = self.repo.get_by_id(profile_id)
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="区域成本配置不存在")
        update_data: dict[str, Any] = payload.model_dump(exclude_unset=True)

        region_id = update_data.get("region_id", profile.region_id)
        currency_id = update_data.get("currency_id", profile.currency_id)
        self._validate_fk(region_id, currency_id)

        if "is_active" in update_data:
            update_data["is_active"] = 1 if update_data["is_active"] else 0

        for k, v in update_data.items():
            setattr(profile, k, v)

        try:
            self.db.flush()
            self.db.commit()
            self.db.refresh(profile)
            return self._to_read(profile)
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="更新失败：数据约束冲突"
            )

    def delete_profile(self, profile_id: int) -> None:
        profile = self.repo.get_by_id(profile_id)
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="区域成本配置不存在")
        self.repo.delete(profile)
        self.db.commit()

