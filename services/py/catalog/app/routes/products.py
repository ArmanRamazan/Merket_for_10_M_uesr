from typing import Annotated
from uuid import UUID

import jwt
from fastapi import APIRouter, Depends, Header, Query

from common.errors import AppError
from app.domain.product import ProductCreate, ProductResponse, ProductListResponse
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["products"])


def _get_product_service() -> ProductService:
    from app.main import get_product_service
    return get_product_service()


def _get_current_user_id(authorization: Annotated[str, Header()]) -> UUID:
    from app.main import app_settings

    if not authorization.startswith("Bearer "):
        raise AppError("Invalid authorization header", status_code=401)
    token = authorization[7:]
    try:
        payload = jwt.decode(
            token, app_settings.jwt_secret, algorithms=[app_settings.jwt_algorithm]
        )
        return UUID(payload["sub"])
    except (jwt.PyJWTError, ValueError, KeyError) as exc:
        raise AppError("Invalid token", status_code=401) from exc


@router.get("", response_model=ProductListResponse)
async def list_products(
    service: Annotated[ProductService, Depends(_get_product_service)],
    q: Annotated[str | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> ProductListResponse:
    if q:
        items, total = await service.search(q, limit, offset)
    else:
        items, total = await service.list(limit, offset)
    return ProductListResponse(
        items=[
            ProductResponse(
                id=p.id,
                seller_id=p.seller_id,
                title=p.title,
                description=p.description,
                price=p.price,
                stock=p.stock,
                created_at=p.created_at,
            )
            for p in items
        ],
        total=total,
    )


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: UUID,
    service: Annotated[ProductService, Depends(_get_product_service)],
) -> ProductResponse:
    p = await service.get(product_id)
    return ProductResponse(
        id=p.id,
        seller_id=p.seller_id,
        title=p.title,
        description=p.description,
        price=p.price,
        stock=p.stock,
        created_at=p.created_at,
    )


@router.post("", response_model=ProductResponse, status_code=201)
async def create_product(
    body: ProductCreate,
    user_id: Annotated[UUID, Depends(_get_current_user_id)],
    service: Annotated[ProductService, Depends(_get_product_service)],
) -> ProductResponse:
    p = await service.create(user_id, body.title, body.description, float(body.price), body.stock)
    return ProductResponse(
        id=p.id,
        seller_id=p.seller_id,
        title=p.title,
        description=p.description,
        price=p.price,
        stock=p.stock,
        created_at=p.created_at,
    )
