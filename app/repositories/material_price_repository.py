from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.material_price import MaterialPrice


class MaterialPriceRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_prices(self) -> list[MaterialPrice]:
        stmt = select(MaterialPrice).order_by(MaterialPrice.updated_at.desc(), MaterialPrice.id.desc())
        return list(self.db.scalars(stmt).all())

    def get_by_id(self, price_id: int) -> Optional[MaterialPrice]:
        return self.db.get(MaterialPrice, price_id)

    def create(self, price: MaterialPrice) -> MaterialPrice:
        self.db.add(price)
        self.db.flush()
        self.db.refresh(price)
        return price

    def delete(self, price: MaterialPrice) -> None:
        self.db.delete(price)
        self.db.flush()

