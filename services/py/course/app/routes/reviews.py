from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.domain.review import ReviewCreate, ReviewResponse, ReviewListResponse
from app.routes.courses import _get_current_user_claims
from app.services.review_service import ReviewService

router = APIRouter(prefix="/reviews", tags=["reviews"])


def _get_review_service() -> ReviewService:
    from app.main import get_review_service
    return get_review_service()


def _to_response(r: "Review") -> ReviewResponse:
    from app.domain.review import Review
    return ReviewResponse(
        id=r.id,
        student_id=r.student_id,
        course_id=r.course_id,
        rating=r.rating,
        comment=r.comment,
        created_at=r.created_at,
    )


@router.post("", response_model=ReviewResponse, status_code=201)
async def create_review(
    body: ReviewCreate,
    claims: Annotated[dict, Depends(_get_current_user_claims)],
    service: Annotated[ReviewService, Depends(_get_review_service)],
) -> ReviewResponse:
    r = await service.create(
        student_id=claims["user_id"],
        role=claims["role"],
        course_id=body.course_id,
        rating=body.rating,
        comment=body.comment,
    )
    return _to_response(r)


@router.get("/course/{course_id}", response_model=ReviewListResponse)
async def list_course_reviews(
    course_id: UUID,
    service: Annotated[ReviewService, Depends(_get_review_service)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> ReviewListResponse:
    items, total = await service.list_by_course(course_id, limit, offset)
    return ReviewListResponse(
        items=[_to_response(r) for r in items],
        total=total,
    )
