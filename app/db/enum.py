from enum import Enum
from sqlmodel import Session, select, func
from app.db.session import engine
from app.db.models.transaction import Transaction

def fetch_distinct_values_from_db(column) -> list[str]:
    """Fetch distinct values from a specific column in the Transaction table."""
    with Session(engine) as session:
        statement = select(column).distinct()
        results = session.exec(statement).all()
        return results

def create_enum(enum_name: str, column) -> Enum:
    """Dynamically create an Enum class based on distinct values from a database column."""
    values = fetch_distinct_values_from_db(column)
    return Enum(enum_name, {value.upper(): value for value in values})

# Dynamically create enums for each column
DeviceIdsEnum = create_enum("DeviceIdsEnum", Transaction.device_id)
PaymentStatusesEnum = create_enum("PaymentStatusesEnum", Transaction.payment_status)
TransactionStatusesEnum = create_enum("TransactionStatusesEnum", Transaction.transaction_status)
PaymentMethodEnum = create_enum("PaymentMethodEnum", Transaction.payment_method)