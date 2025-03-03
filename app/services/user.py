import json

from app.db.repositories.user import UserRepository
from app.db.models.user import User
from app.db.session import redis_client
from app.db.utils import invalidate_pattern_cache


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def get_users(self, limit: int, offset: int) -> list[User]:
        cache_key = f"users:offset:{offset}:limit:{limit}"
        cached_users = redis_client.get(cache_key)

        if cached_users:
            return json.loads(cached_users)

        # Fetch from DB if cache not found
        users = self.user_repository.get_users(offset=offset, limit=limit)
        users_data = [user.dict() for user in users]

        # Cache results for 5 minutes
        redis_client.setex(cache_key, 300, json.dumps(users_data))

        return self.user_repository.get_users(limit=limit, offset=offset)

    def get_user_by_id(self, user_id: int) -> User:
        cache_key = f"user:{user_id}"
        cached_user = redis_client.get(cache_key)

        if cached_user:
            return json.loads(cached_user)

        user = self.user_repository.get_user_by_id(user_id)
        if user:
            redis_client.setex(cache_key, 300, json.dumps(user.model_dump()))
        return user

    def create_user(self, user_data: User) -> User:
        user = self.user_repository.create_user(user_data)

        if user:
            cache_key = f"user:{user.id}"
            redis_client.setex(cache_key, 300, json.dumps(user.model_dump()))
            invalidate_pattern_cache("users.*")
        return user

    def update_user(self, user_id: int, update_data: dict) -> User:
        user = self.user_repository.update_user(user_id, update_data)

        if user:
            cache_key = f"user:{user_id}"
            redis_client.delete(cache_key)  
            redis_client.setex(cache_key, 300, json.dumps(user.dict()))  
            invalidate_pattern_cache("users.*")
        return user

    def delete_user(self, user_id: int) -> bool:
        success = self.user_repo.delete(user_id)
        if success:
            cache_key = f"user:{user_id}"
            redis_client.delete(cache_key)  
            invalidate_pattern_cache("users.*")
        return success
