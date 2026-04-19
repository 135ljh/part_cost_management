from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.material import MaterialCreate, MaterialRead, MaterialUpdate
from app.services.material_service import MaterialService


router = APIRouter(prefix="/materials", tags=["物质配置"])


@router.get("", response_model=list[MaterialRead], summary="物质列表")
def list_materials(db: Session = Depends(get_db)) -> list[MaterialRead]:
    return MaterialService(db).list_materials()


@router.get("/{material_id}", response_model=MaterialRead, summary="物质详情")
def get_material(material_id: int, db: Session = Depends(get_db)) -> MaterialRead:
    return MaterialService(db).get_material_detail(material_id)


@router.post("", response_model=MaterialRead, status_code=status.HTTP_201_CREATED, summary="新建物质")
def create_material(payload: MaterialCreate, db: Session = Depends(get_db)) -> MaterialRead:
    return MaterialService(db).create_material(payload)


@router.put("/{material_id}", response_model=MaterialRead, summary="更新物质")
def update_material(
    material_id: int, payload: MaterialUpdate, db: Session = Depends(get_db)
) -> MaterialRead:
    return MaterialService(db).update_material(material_id, payload)


@router.delete("/{material_id}", status_code=status.HTTP_204_NO_CONTENT, summary="删除物质")
def delete_material(material_id: int, db: Session = Depends(get_db)) -> Response:
    MaterialService(db).delete_material(material_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

