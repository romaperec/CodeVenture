import pytest
from fastapi import HTTPException, status
from unittest.mock import AsyncMock, MagicMock
from app.modules.users.schemas import UserCreate, UserResponse
from app.modules.users.models import User
from app.modules.users.service import UserService


@pytest.fixture
def mock_db_session():
    session = AsyncMock()
    session.commit = AsyncMock()
    session.delete = AsyncMock()
    session.add = MagicMock()
    session.execute = AsyncMock()
    return session


@pytest.fixture
def user_service(mock_db_session):
    return UserService(db=mock_db_session)


@pytest.mark.asyncio
async def test_get_by_id_found(user_service, mock_db_session):
    user_id = 1
    expected_user = User(id=user_id, email="test@test.com")

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = expected_user
    mock_db_session.execute.return_value = mock_result

    result = await user_service.get_by_id(user_id)

    mock_db_session.execute.assert_awaited_once()
    assert result == expected_user
    assert result.id == 1


@pytest.mark.asyncio
async def test_get_by_id_not_found(user_service, mock_db_session):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db_session.execute.return_value = mock_result

    result = await user_service.get_by_id(999)

    assert result is None


@pytest.mark.asyncio
async def test_get_by_email_found(user_service, mock_db_session):
    email = "test@test.com"
    expected_user = User(id=1, email=email)

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = expected_user
    mock_db_session.execute.return_value = mock_result

    result = await user_service.get_by_email(email)

    assert result == expected_user
    assert result.email == email


@pytest.mark.asyncio
async def test_create_user(user_service, mock_db_session):
    schema = UserCreate(
        username="newuser", email="new@example.com", password="secret_password"
    )

    def set_user_id(user):
        user.id = 1

    mock_db_session.add.side_effect = set_user_id

    result = await user_service.create_user(schema)

    mock_db_session.add.assert_called_once()

    added_user = mock_db_session.add.call_args[0][0]

    assert isinstance(added_user, User)
    assert added_user.username == "newuser"
    assert added_user.email == "new@example.com"
    assert added_user.id == 1

    mock_db_session.commit.assert_awaited_once()

    assert isinstance(result, UserResponse)
    assert result.username == "newuser"
    assert result.id == 1


@pytest.mark.asyncio
async def test_delete_user_success(user_service, mock_db_session):
    user_id = 1
    existing_user = User(id=user_id, email="del@test.com")

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_user
    mock_db_session.execute.return_value = mock_result

    result = await user_service.delete_user(user_id)

    mock_db_session.delete.assert_awaited_once_with(existing_user)
    mock_db_session.commit.assert_awaited_once()
    assert result == {"status": "success", "deleted_id": user_id}


@pytest.mark.asyncio
async def test_delete_user_not_found(user_service, mock_db_session):
    user_id = 999

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db_session.execute.return_value = mock_result

    with pytest.raises(HTTPException) as exc_info:
        await user_service.delete_user(user_id)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "User not found by id"

    mock_db_session.delete.assert_not_awaited()
    mock_db_session.commit.assert_not_awaited()
