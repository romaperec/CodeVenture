import pytest
from fastapi import HTTPException, status
from unittest.mock import AsyncMock, MagicMock
from app.modules.auth.schemas import UserRegister, UserLogin, UserResponse
from app.modules.auth.service import AuthService


@pytest.fixture
def mock_user_service():
    return AsyncMock()


@pytest.fixture
def auth_service(mock_user_service):
    return AuthService(user_service=mock_user_service)


@pytest.mark.asyncio
async def test_register_user_success(auth_service, mock_user_service, mocker):
    register_schema = UserRegister(
        username="testuser",
        email="new@example.com",
        password="plain_password",
        description="Test description",
    )

    mock_user_service.get_by_email.return_value = None

    created_user_mock = MagicMock()
    created_user_mock.username = "testuser"
    created_user_mock.email = "new@example.com"
    mock_user_service.create_user.return_value = created_user_mock

    mocker.patch("app.modules.auth.service.hash_password", return_value="hashed_secret")

    result = await auth_service.register_user(register_schema)

    mock_user_service.get_by_email.assert_awaited_once_with("new@example.com")
    assert register_schema.password == "hashed_secret"
    mock_user_service.create_user.assert_awaited_once_with(register_schema)
    assert result == created_user_mock


@pytest.mark.asyncio
async def test_register_user_already_exists(auth_service, mock_user_service):
    register_schema = UserRegister(
        username="testuser", email="exists@example.com", password="password"
    )

    mock_user_service.get_by_email.return_value = MagicMock()

    with pytest.raises(HTTPException) as exc_info:
        await auth_service.register_user(register_schema)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == "Email already registered"

    mock_user_service.create_user.assert_not_awaited()


@pytest.mark.asyncio
async def test_login_user_success(auth_service, mock_user_service, mocker):
    login_schema = UserLogin(email="user@example.com", password="correct_password")

    existing_user = MagicMock()
    existing_user.username = "User"
    existing_user.email = "user@example.com"
    existing_user.password = "hashed_real_password"
    existing_user.description = "Desc"

    mock_user_service.get_by_email.return_value = existing_user

    mocker.patch("app.modules.auth.service.verify_password", return_value=True)

    result = await auth_service.login_user(login_schema)

    assert isinstance(result, UserResponse)
    assert result.email == "user@example.com"


@pytest.mark.asyncio
async def test_login_user_not_found(auth_service, mock_user_service):
    login_schema = UserLogin(email="unknown@example.com", password="any")

    mock_user_service.get_by_email.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await auth_service.login_user(login_schema)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Invalid email or password"


@pytest.mark.asyncio
async def test_login_user_wrong_password(auth_service, mock_user_service, mocker):
    login_schema = UserLogin(email="user@example.com", password="wrong_password")

    existing_user = MagicMock()
    existing_user.password = "hashed_real_password"
    mock_user_service.get_by_email.return_value = existing_user

    mocker.patch("app.modules.auth.service.verify_password", return_value=False)

    with pytest.raises(HTTPException) as exc_info:
        await auth_service.login_user(login_schema)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Invalid email or password"
