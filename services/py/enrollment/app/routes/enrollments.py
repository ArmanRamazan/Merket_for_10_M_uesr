from typing import Annotated
from uuid import UUID

import jwt
from fastapi import APIRouter, Depends, Header, Query

from common.errors import AppError
from app.domain.enrollment import (
    EnrollmentCreate,
    EnrollmentResponse,
    EnrollmentListResponse,
)
from app.services.enrollment_service import EnrollmentService

router = APIRouter(prefix="/enrollments", tags=["enrollments"])


def _get_enrollment_service() -> EnrollmentService:
    from app.main import get_enrollment_service
    return get_enrollment_service()


def _get_current_user_claims(authorization: Annotated[str, Header()]) -> dict:
    from app.main import app_settings

    if not authorization.startswith("Bearer "):
        raise AppError("Invalid authorization header", status_code=401)
    token = authorization[7:]
    try:
        payload = jwt.decode(
            token, app_settings.jwt_secret, algorithms=[app_settings.jwt_algorithm]
        )
        return {
            "user_id": UUID(payload["sub"]),
            "role": payload.get("role", "student"),
            "is_verified": payload.get("is_verified", False),
        }
    except (jwt.PyJWTError, ValueError, KeyError) as exc:
        raise AppError("Invalid token", status_code=401) from exc


def _to_response(e: "Enrollment") -> EnrollmentResponse:
    from app.domain.enrollment import Enrollment
    return EnrollmentResponse(
        id=e.id,
        student_id=e.student_id,
        course_id=e.course_id,
        payment_id=e.payment_id,
        status=e.status,
        enrolled_at=e.enrolled_at,
    )


@router.post("", response_model=EnrollmentResponse, status_code=201)
async def create_enrollment(
    body: EnrollmentCreate,
    claims: Annotated[dict, Depends(_get_current_user_claims)],
    service: Annotated[EnrollmentService, Depends(_get_enrollment_service)],
) -> EnrollmentResponse:
    enrollment = await service.enroll(
        student_id=claims["user_id"],
        role=claims["role"],
        course_id=body.course_id,
        payment_id=body.payment_id,
    )
    return _to_response(enrollment)


@router.get("/me", response_model=EnrollmentListResponse)
async def list_my_enrollments(
    claims: Annotated[dict, Depends(_get_current_user_claims)],
    service: Annotated[EnrollmentService, Depends(_get_enrollment_service)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> EnrollmentListResponse:
    items, total = await service.list_my(claims["user_id"], limit, offset)
    return EnrollmentListResponse(
        items=[_to_response(e) for e in items],
        total=total,
    )


@router.get("/course/{course_id}/count")
async def get_course_enrollment_count(
    course_id: UUID,
    service: Annotated[EnrollmentService, Depends(_get_enrollment_service)],
) -> dict:
    count = await service.count_by_course(course_id)
    return {"course_id": course_id, "count": count}
