import json

from app.db.repositories.item import ItemRepository
from app.db.models.item import Item
from app.db.session import redis_client
from app.db.utils import invalidate_pattern_cache


class ItemService:
    def __init__(self, item_repository: ItemRepository):
        self.item_repository = item_repository

    def get_items(self, limit: int, offset: int) -> list[Item]:
        cache_key = f"items:offset:{offset}:limit:{limit}"
        cached_items = redis_client.get(cache_key)

        if cached_items:
            return json.loads(cached_items)

        # Fetch from DB if cache not found
        items = self.item_repository.get_items(offset=offset, limit=limit)
        items_data = [item.dict() for item in items]

        # Cache results for 5 minutes
        redis_client.setex(cache_key, 300, json.dumps(items_data))

        return self.item_repository.get_items(limit=limit, offset=offset)

    def get_item_by_id(self, item_id: int) -> Item:
        cache_key = f"item:{item_id}"
        cached_item = redis_client.get(cache_key)

        if cached_item:
            return json.loads(cached_item)

        item = self.item_repository.get_item_by_id(item_id)
        if item:
            redis_client.setex(cache_key, 300, json.dumps(item.model_dump()))
        return item

    def create_item(self, item_data: Item) -> Item:
        item = self.item_repository.create_item(item_data)

        if item:
            cache_key = f"item:{item.id}"
            redis_client.setex(cache_key, 300, json.dumps(item.model_dump()))
            invalidate_pattern_cache("items.*")
        return item

    def update_item(self, item_id: int, update_data: dict) -> Item:
        item = self.item_repository.update_item(item_id, update_data)

        if item:
            cache_key = f"item:{item_id}"
            redis_client.delete(cache_key)  
            redis_client.setex(cache_key, 300, json.dumps(item.dict()))  
            invalidate_pattern_cache("items.*")
        return item

    def delete_item(self, item_id: int) -> bool:
        success = self.item_repo.delete(item_id)
        if success:
            cache_key = f"item:{item_id}"
            redis_client.delete(cache_key)  
            invalidate_pattern_cache("items.*")
        return success
