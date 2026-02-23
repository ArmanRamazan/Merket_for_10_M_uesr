from fastapi import APIRouter

from app.domain.category import CategoryResponse

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryResponse])
async def list_categories() -> list[CategoryResponse]:
    from app.main import get_category_repo

    repo = get_category_repo()
    cats = await repo.list_all()
    return [CategoryResponse(id=c.id, name=c.name, slug=c.slug) for c in cats]
