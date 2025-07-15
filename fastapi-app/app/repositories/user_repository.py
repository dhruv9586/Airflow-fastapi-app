from bson import ObjectId
from fastapi import HTTPException
from app.database.connection import get_collection
from app.models.user import User, UserResponse
from app.utils.helpers import parse_json


class UserRepository:
    def __init__(self):
        self.collection = get_collection("users")

    async def create_user(self, user: User):
        new_user = await self.collection.insert_one(user.model_dump())
        created_user = await self.collection.find_one({"_id": new_user.inserted_id})
        return created_user

    async def get_user_by_id(self, user_id: str):
        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="Invalid user id")
        user_object_id = ObjectId(user_id)
        user = await self.collection.find_one({"_id": user_object_id})
        return user

    async def get_all_users(self, page: int = 1, size: int = 5):
        skip = (page - 1) * size
        cursor = self.collection.find().skip(skip).limit(size)
        users = await cursor.to_list(size)
        return parse_json(users)

    async def delete_user(self, user_id: str):
        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="Invalid user id")
        result = await self.collection.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0
