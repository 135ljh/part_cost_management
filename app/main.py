from fastapi import FastAPI
from sqlalchemy import text

from app.api.router import api_router
from app.core.config import settings
from app.core.database import engine
from app.models.base import Base
from app.models.bom import Bom
from app.models.bom_item import BomItem
from app.models.cost_item import CostItem
from app.models.material_type import MaterialType
from app.models.part import Part
from app.models.part_attachment import PartAttachment


app = FastAPI(
    title=settings.app_name,
    debug=settings.app_debug,
    version="0.1.0",
    description="IDME 零件成本计算系统后端服务",
)

app.include_router(api_router)


@app.on_event("startup")
def _ensure_part_tables() -> None:
    Base.metadata.create_all(
        bind=engine,
        tables=[
            MaterialType.__table__,
            Part.__table__,
            PartAttachment.__table__,
            Bom.__table__,
            BomItem.__table__,
            CostItem.__table__,
        ],
    )
    with engine.begin() as conn:
        has_material_type_id = conn.execute(
            text(
                """
                SELECT COUNT(1)
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = 'part'
                  AND COLUMN_NAME = 'material_type_id'
                """
            )
        ).scalar()
        if not has_material_type_id:
            conn.execute(text("ALTER TABLE part ADD COLUMN material_type_id INT NULL"))

        has_version_no = conn.execute(
            text(
                """
                SELECT COUNT(1)
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = 'part'
                  AND COLUMN_NAME = 'version_no'
                """
            )
        ).scalar()
        if not has_version_no:
            conn.execute(text("ALTER TABLE part ADD COLUMN version_no INT NOT NULL DEFAULT 1"))


@app.get("/health", tags=["系统"])
def health() -> dict[str, str]:
    return {"status": "ok"}
