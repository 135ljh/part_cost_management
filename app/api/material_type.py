from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.material_type import (
    MaterialTypeCreate,
    MaterialTypeRead,
    MaterialTypeUpdate,
)
from app.services.material_type_service import MaterialTypeService


router = APIRouter(prefix="/material-types", tags=["物料类型配置"])


@router.get("", response_model=list[MaterialTypeRead], summary="物料类型列表")
def list_material_types(db: Session = Depends(get_db)) -> list[MaterialTypeRead]:
    return MaterialTypeService(db).list_material_types()


@router.get("/{material_type_id}", response_model=MaterialTypeRead, summary="物料类型详情")
def get_material_type(
    material_type_id: int, db: Session = Depends(get_db)
) -> MaterialTypeRead:
    return MaterialTypeService(db).get_material_type_detail(material_type_id)


@router.post(
    "", response_model=MaterialTypeRead, status_code=status.HTTP_201_CREATED, summary="新建物料类型"
)
def create_material_type(
    payload: MaterialTypeCreate, db: Session = Depends(get_db)
) -> MaterialTypeRead:
    return MaterialTypeService(db).create_material_type(payload)


@router.put("/{material_type_id}", response_model=MaterialTypeRead, summary="更新物料类型")
def update_material_type(
    material_type_id: int, payload: MaterialTypeUpdate, db: Session = Depends(get_db)
) -> MaterialTypeRead:
    return MaterialTypeService(db).update_material_type(material_type_id, payload)


@router.delete("/{material_type_id}", status_code=status.HTTP_204_NO_CONTENT, summary="删除物料类型")
def delete_material_type(material_type_id: int, db: Session = Depends(get_db)) -> Response:
    MaterialTypeService(db).delete_material_type(material_type_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
