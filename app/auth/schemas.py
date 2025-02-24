from sqlmodel import SQLModel

class Token(SQLModel):
    access_token: str
    token_type: str

class TokenData(SQLModel):
    email: str | None = None

class UserLogin(SQLModel):
    email: str
    password: str
