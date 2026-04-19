from fastapi import APIRouter

from app.api.bom import router as bom_router
from app.api.bom_item import router as bom_item_router
from app.api.cost_item import router as cost_item_router
from app.api.currency import router as currency_router
from app.api.currency_exchange_rate import router as exchange_rate_router
from app.api.equipment import router as equipment_router
from app.api.equipment_category import router as equipment_category_router
from app.api.equipment_cost_profile import router as equipment_cost_profile_router
from app.api.equipment_rate import router as equipment_rate_router
from app.api.equipment_specification import router as equipment_specification_router
from app.api.material import router as material_router
from app.api.material_category import router as material_category_router
from app.api.material_price import router as material_price_router
from app.api.material_type import router as material_type_router
from app.api.part import router as part_router
from app.api.part_attachment import router as part_attachment_router
from app.api.region import router as region_router
from app.api.region_cost_profile import router as region_cost_profile_router
from app.api.unit import router as unit_router


api_router = APIRouter(prefix="/api/v1")
api_router.include_router(unit_router)
api_router.include_router(currency_router)
api_router.include_router(exchange_rate_router)
api_router.include_router(region_router)
api_router.include_router(region_cost_profile_router)
api_router.include_router(equipment_category_router)
api_router.include_router(equipment_router)
api_router.include_router(equipment_specification_router)
api_router.include_router(equipment_rate_router)
api_router.include_router(equipment_cost_profile_router)
api_router.include_router(material_category_router)
api_router.include_router(material_router)
api_router.include_router(material_price_router)
api_router.include_router(material_type_router)
api_router.include_router(part_router)
api_router.include_router(part_attachment_router)
api_router.include_router(bom_router)
api_router.include_router(bom_item_router)
api_router.include_router(cost_item_router)
