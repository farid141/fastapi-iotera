from fastapi import FastAPI
from app.routers import users, items, transactions
from app.auth import routes as auth_routes
import uvicorn

app = FastAPI()

app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(items.router, prefix="/items", tags=["Items"])
app.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])
app.include_router(auth_routes.router, prefix="/auth", tags=["Auth"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)