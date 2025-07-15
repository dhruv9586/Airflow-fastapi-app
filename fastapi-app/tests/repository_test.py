import pytest
from unittest.mock import AsyncMock, patch
from bson import ObjectId
from fastapi import HTTPException

from app.repositories.user_repository import UserRepository
from app.models.user import User

# Sample test data
VALID_USER_ID = "6406be13c5eb3f4e4d86b3b1"
INVALID_USER_ID = "invalid-id"
SAMPLE_USER_DICT = {
    "_id": ObjectId(VALID_USER_ID),
    "name": "Test User",
    "email": "test@example.com",
    "age": 30,
}
SAMPLE_USER_CREATE = User(name="Test User", email="test@example.com", age=30)


@pytest.mark.asyncio
class TestUserRepository:

    @pytest.fixture
    def mock_collection(self):
        collection = AsyncMock()
        return collection

    @pytest.fixture
    def user_repo(self, mock_collection) -> UserRepository:
        with patch(
            "app.repositories.user_repository.get_collection",
            return_value=mock_collection,
        ):
            repo = UserRepository()
            repo.collection = mock_collection
            return repo

    async def test_create_user_success(
        self, user_repo: UserRepository, mock_collection
    ):
        # Setup the mock
        mock_collection.insert_one.return_value = AsyncMock(
            inserted_id=ObjectId(VALID_USER_ID),
        )
        mock_collection.find_one.return_value = SAMPLE_USER_DICT

        # Call the function
        result = await user_repo.create_user(SAMPLE_USER_CREATE)

        # Assertions
        assert result == SAMPLE_USER_DICT
        mock_collection.insert_one.assert_called_once()
        mock_collection.find_one.assert_called_once()

    async def test_get_user_by_id_success(
        self, user_repo: UserRepository, mock_collection
    ):

        mock_collection.find_one.return_value = SAMPLE_USER_DICT
        response = await user_repo.get_user_by_id(VALID_USER_ID)

        assert response == SAMPLE_USER_DICT
        mock_collection.find_one.assert_called_once_with(
            {"_id": ObjectId(VALID_USER_ID)}
        )

    async def test_get_user_by_id_not_found(
        self, user_repo: UserRepository, mock_collection
    ):
        # Setup the mock
        mock_collection.find_one.return_value = None

        # Call the function
        result = await user_repo.get_user_by_id(VALID_USER_ID)

        # Assertions
        assert result is None
        mock_collection.find_one.assert_called_once_with(
            {"_id": ObjectId(VALID_USER_ID)}
        )

    async def test_get_user_by_id_invalid_id(self, user_repo):
        # Test with invalid ID
        with pytest.raises(HTTPException) as excinfo:
            await user_repo.get_user_by_id(INVALID_USER_ID)

        # Assertions
        assert excinfo.value.status_code == 400
        assert "Invalid user id" in str(excinfo.value.detail)

    async def test_delete_user_success(
        self, user_repo: UserRepository, mock_collection
    ):
        # Setup the mock
        mock_collection.delete_one.return_value = AsyncMock(deleted_count=1)

        # Call the function
        result = await user_repo.delete_user(VALID_USER_ID)

        # Assertions
        assert result is True
        mock_collection.delete_one.assert_called_once_with(
            {"_id": ObjectId(VALID_USER_ID)}
        )

    async def test_delete_user_not_found(
        self, user_repo: UserRepository, mock_collection
    ):
        # Setup the mock
        mock_collection.delete_one.return_value = AsyncMock(deleted_count=0)

        # Call the function
        result = await user_repo.delete_user(VALID_USER_ID)

        # Assertions
        assert result is False
        mock_collection.delete_one.assert_called_once_with(
            {"_id": ObjectId(VALID_USER_ID)}
        )

    async def test_delete_user_invalid_id(self, user_repo: UserRepository):
        # Test with invalid ID
        with pytest.raises(HTTPException) as excinfo:
            await user_repo.delete_user(INVALID_USER_ID)

        # Assertions
        assert excinfo.value.status_code == 400
        assert "Invalid user id" in str(excinfo.value.detail)
