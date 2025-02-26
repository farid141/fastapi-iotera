from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

app = FastAPI()
security = HTTPBasic()

# Dummy credentials
VALID_USERNAME = "admin"
VALID_PASSWORD = "password"

def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, VALID_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, VALID_PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return credentials.username

@app.get("/secure-data")
def secure_route(username: str = Depends(authenticate)):
    return {"message": f"Hello, {username}!"}
@app.get("/secure-data2")
def secure_route(username: str = Depends(authenticate)):
    return {"message": f"Hello, {username}!"}
