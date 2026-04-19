from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.material_category import (
    MaterialCategoryCreate,
    MaterialCategoryRead,
    MaterialCategoryTreeNode,
    MaterialCategoryUpdate,
)
from app.services.material_category_service import MaterialCategoryService


router = APIRouter(prefix="/material-categories", tags=["物质分类配置"])


@router.get("", response_model=list[MaterialCategoryRead], summary="物质分类列表")
def list_material_categories(db: Session = Depends(get_db)) -> list[MaterialCategoryRead]:
    return MaterialCategoryService(db).list_categories()


@router.get("/{category_id}", response_model=MaterialCategoryRead, summary="物质分类详情")
def get_material_category(category_id: int, db: Session = Depends(get_db)) -> MaterialCategoryRead:
    return MaterialCategoryService(db).get_category_detail(category_id)


@router.post(
    "",
    response_model=MaterialCategoryRead,
    status_code=status.HTTP_201_CREATED,
    summary="新建物质分类",
)
def create_material_category(
    payload: MaterialCategoryCreate, db: Session = Depends(get_db)
) -> MaterialCategoryRead:
    return MaterialCategoryService(db).create_category(payload)


@router.put("/{category_id}", response_model=MaterialCategoryRead, summary="更新物质分类")
def update_material_category(
    category_id: int, payload: MaterialCategoryUpdate, db: Session = Depends(get_db)
) -> MaterialCategoryRead:
    return MaterialCategoryService(db).update_category(category_id, payload)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT, summary="删除物质分类")
def delete_material_category(category_id: int, db: Session = Depends(get_db)) -> Response:
    MaterialCategoryService(db).delete_category(category_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/tree/all", response_model=list[MaterialCategoryTreeNode], summary="物质分类树")
def get_material_category_tree(db: Session = Depends(get_db)) -> list[MaterialCategoryTreeNode]:
    return MaterialCategoryService(db).get_category_tree()

