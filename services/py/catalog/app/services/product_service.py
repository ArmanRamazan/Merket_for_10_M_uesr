from __future__ import annotations

from uuid import UUID

from common.errors import NotFoundError
from app.domain.product import Product
from app.repositories.product_repo import ProductRepository


class ProductService:
    def __init__(self, repo: ProductRepository) -> None:
        self._repo = repo

    async def create(
        self, seller_id: UUID, title: str, description: str, price: float, stock: int
    ) -> Product:
        return await self._repo.create(seller_id, title, description, price, stock)

    async def get(self, product_id: UUID) -> Product:
        product = await self._repo.get_by_id(product_id)
        if not product:
            raise NotFoundError("Product not found")
        return product

    async def list(self, limit: int = 20, offset: int = 0) -> tuple[list[Product], int]:
        return await self._repo.list(limit, offset)

    async def search(self, query: str, limit: int = 20, offset: int = 0) -> tuple[list[Product], int]:
        return await self._repo.search(query, limit, offset)
