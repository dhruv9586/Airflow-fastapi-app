from fastapi import APIRouter, HTTPException, status, Depends
from app.models.user import User, UserResponse
from app.repositories.user_repository import UserRepository


router = APIRouter(prefix="/users", tags=["users"])
user_repository = UserRepository()


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def add_user(user: User):
    created_user = await user_repository.create_user(user)
    return created_user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    try:
        user = await user_repository.get_user_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        return UserResponse(
            id=user_id, name=user["name"], email=user["email"], age=user["age"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}",
        )


@router.get("/", response_model=list)
async def get_all_users(page: int = 1, size: int = 5):
    try:
        users = await user_repository.get_all_users(page, size)
        return users
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}",
        )


@router.delete("/{user_id}")
async def delete_user(user_id: str):
    try:
        user = await user_repository.get_user_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        success = await user_repository.delete_user(user_id)
        if success:
            return {"message": "User deleted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete user")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}",
        )
