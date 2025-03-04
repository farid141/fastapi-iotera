import json

from app.db.repositories.transaction import TransactionRepository
from app.db.models.transaction import Transaction
from app.db.session import redis_client
from app.db.utils import invalidate_pattern_cache


class TransactionService:
    def __init__(self, transaction_repository: TransactionRepository):
        self.transaction_repository = transaction_repository

    def get_transactions(self, limit: int, offset: int) -> list[Transaction]:
        cache_key = f"transactions:offset:{offset}:limit:{limit}"
        cached_transactions = redis_client.get(cache_key)

        if cached_transactions:
            return json.loads(cached_transactions)

        # Fetch from DB if cache not found
        transactions = self.transaction_repository.get_transactions(offset=offset, limit=limit)
        transactions_data = [transaction.dict() for transaction in transactions]

        # Cache results for 5 minutes
        redis_client.setex(cache_key, 300, json.dumps(transactions_data, default=str))

        return self.transaction_repository.get_transactions(limit=limit, offset=offset)
    
    def create_transaction(self, schema, transaction_data: Transaction) -> Transaction:            
        transaction = self.transaction_repository.create_transaction(schema, transaction_data)

        if transaction:
            cache_key = f"transaction:{transaction.uuid}"
            redis_client.setex(cache_key, 300, json.dumps(transaction.model_dump(), default=str))
            invalidate_pattern_cache("transactions.*")
        return transaction