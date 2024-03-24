from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from pymongo_connection import ServiceDB
from custom import get_password_hash, verify_password

app = FastAPI(debug=True)

# Variable needed
collection_name = "test_fastapi"
fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True,
    },
}
db_instance = ServiceDB(collection_name)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UpdateUser(User):
    email: Optional[str] = None


class ValidUser(BaseModel):
    username: str
    full_name: str
    email: str | None = None
    password: str


class UserInDB(User):
    hashed_password: str


def get_user(username: str):
    user_dict = db_instance.get_from_db({"username": username})
    if user_dict:
        return UserInDB(**user_dict)


async def get_current_user(user_name: str = Depends(oauth2_scheme)):
    user = get_user(user_name)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = db_instance.get_from_db({"username": form_data.username})
    print(f"form_data.username: {form_data.username} and user_dict: {user_dict}")
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    # hashed_password = get_password_hash(form_data.password)
    db_pass = user_dict.get("hashed_password")
    print(f"form_data.password: `{db_pass}` and hashed_password: `{form_data.password}`")
    if not verify_password(form_data.password, db_pass):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}


@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


def raise_not_exist(name):
    user_dict = db_instance.get_from_db({"username": name})
    if not user_dict:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User `{name}` not found in database")


@app.get("/get_data/")
def get_user_data(current_user: User = Depends(get_current_active_user)):
    return {"username": current_user.username, "email": current_user.email, "Full_Name": current_user.full_name}


@app.get("/get_name/{name}")
def get_full_name(name: str, current_user: User = Depends(get_current_active_user)) -> dict:
    raise_not_exist(name)
    return {"Full_Name": current_user.full_name}


@app.delete("/delete_user/{username}")
def delete_user(username: str, current_user: User = Depends(get_current_active_user)) -> dict:
    raise_not_exist(username)
    db_instance.delete_one({"username": username})
    return {"message": f"User `{username}` data deleted successfully"}


@app.put("/update")
def update_user(user: UpdateUser, current_user: User = Depends(get_current_active_user)) -> dict:
    username = user.username
    raise_not_exist(username)
    full_name = current_user.full_name
    query = {"username": username, "full_name": full_name}
    data = {"email": user.email}
    db_instance.update_db(query, data)
    return {"message": f"User `{username}` data updated successfully"}


@app.post("/add/users")
def add_user(user: ValidUser) -> dict:
    username = user.username
    user_rec = {
        "username": username,
        "full_name": user.full_name,
        "email": user.email,
        "disabled": False,
        "hashed_password": get_password_hash(user.password)
    }
    user_dict = db_instance.get_from_db({"username": user.username, "email": user.email})
    username = user.username
    if user_dict:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"User `{username}` already exist in db")
    else:
        db_instance.insert_one(user_rec)
    return {"message": f"User `{username}` data added successfully"}
