import jwt
from datetime import datetime, timedelta, timezone
from argon2 import PasswordHasher
from fastapi import Depends, HTTPException
from argon2.exceptions import VerifyMismatchError
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from main_app.exeptions_alert import NoEnter

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
SEKRET_KEY = "234wtfTzzfcfsdfsdff/sdawadwaelpwlla3123123"  #keep this in .env file
ALGORITHM = "HS256"  #

ph = PasswordHasher(
    time_cost=3,
    memory_cost=65536,# 64 MB
    parallelism=2
)
def hash_password(password: str) -> str:
    return ph.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    try:
        ph.verify(hashed, password)
        return True

    except VerifyMismatchError:
        return False

def code_jwt(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(data, SEKRET_KEY, algorithm=ALGORITHM)

def de_code(token):
    try:
        payload = jwt.decode(token, SEKRET_KEY, algorithms=[ALGORITHM])  # Декодируем токен с помощью секретного ключа
        return payload

    except jwt.ExpiredSignatureError:
        return JSONResponse(
            status_code=401,
            content={"message": "Token is Expired"}

        )

    except jwt.InvalidTokenError:
        return JSONResponse(
            status_code=401,
            content={"message": "Invalid token"}

        )


def get_token_from_header(token: str = Depends(oauth2_scheme)):
    return de_code(token)


def role_required(allowed_roles: list[str]):

    def role_checker(current_user = Depends(get_token_from_header)):

        if current_user["sub"] not in allowed_roles:
            raise NoEnter(
                status_code=403,
                detail="Not enough permissions",
                message=f"You can't use this API, with role '{current_user["sub"]}'",
                users_role=current_user["sub"],
                required_role=allowed_roles,
                er_code="Not enter to endpoint -> auth token"
            )

        return current_user

    return role_checker


def role_control(user_role, request_role):  #control func for create endpoint so 'user' cant crete new data with moder or admin role
    if user_role not in ["moder", "admin", "user", "guest"]:
        return JSONResponse(
            status_code=400,
            content={"message": f"Role '{user_role}' doesn't exist"}
        )

    if user_role == "user" and request_role in ["moder", "admin"]:
        raise NoEnter(
            status_code=403,
            detail="Not enough permissions",
            message="You can't create role 'admin' or 'moder', if you are 'user'",
            users_role=user_role,
            required_role=["moder", "admin"],
            er_code="Role creating -> create"
        )

    pass




