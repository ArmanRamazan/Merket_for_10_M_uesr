import pytest
from app.domain.user import User
from common.errors import ConflictError, ForbiddenError, NotFoundError


class TestListPendingTeachers:
    async def test_admin_can_list(self, auth_service, mock_repo, unverified_teacher):
        mock_repo.list_unverified_teachers.return_value = ([unverified_teacher], 1)
        teachers, total = await auth_service.list_pending_teachers("admin")
        assert total == 1
        assert teachers[0].email == "unverified@example.com"

    async def test_student_forbidden(self, auth_service):
        with pytest.raises(ForbiddenError):
            await auth_service.list_pending_teachers("student")

    async def test_teacher_forbidden(self, auth_service):
        with pytest.raises(ForbiddenError):
            await auth_service.list_pending_teachers("teacher")


class TestVerifyTeacher:
    async def test_verify_success(self, auth_service, mock_repo, unverified_teacher):
        mock_repo.get_by_id.return_value = unverified_teacher
        verified = User(
            id=unverified_teacher.id,
            email=unverified_teacher.email,
            password_hash=unverified_teacher.password_hash,
            name=unverified_teacher.name,
            role=unverified_teacher.role,
            is_verified=True,
            created_at=unverified_teacher.created_at,
        )
        mock_repo.set_verified.return_value = verified

        result = await auth_service.verify_teacher("admin", unverified_teacher.id)
        assert result.is_verified is True
        mock_repo.set_verified.assert_awaited_once_with(unverified_teacher.id, True)

    async def test_forbidden_for_student(self, auth_service, unverified_teacher):
        with pytest.raises(ForbiddenError):
            await auth_service.verify_teacher("student", unverified_teacher.id)

    async def test_not_found(self, auth_service, mock_repo):
        mock_repo.get_by_id.return_value = None
        with pytest.raises(NotFoundError):
            await auth_service.verify_teacher("admin", "00000000-0000-0000-0000-000000000000")

    async def test_already_verified(self, auth_service, mock_repo, teacher_user):
        mock_repo.get_by_id.return_value = teacher_user  # is_verified=True
        with pytest.raises(ConflictError, match="already verified"):
            await auth_service.verify_teacher("admin", teacher_user.id)
