from datetime import UTC, datetime, timedelta
from typing import Annotated

import bcrypt
import jwt
from fastapi import Depends, Header, HTTPException, status

from backend.config import settings
from backend.models.users import User
from backend.repository.users import UserRepo

JWT_ALGORITHM = "HS256"

UNAUTHORIZED = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Not authenticated",
    headers={"WWW-Authenticate": "Bearer"},
)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(user: User) -> str:
    expires_at = datetime.now(UTC) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": str(user.id), "exp": expires_at}
    return jwt.encode(payload, settings.jwt_secret, algorithm=JWT_ALGORITHM)


def _user_id_from_token(token: str) -> int:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[JWT_ALGORITHM])
        return int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError) as exc:
        raise UNAUTHORIZED from exc


def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
    repo: UserRepo = Depends(UserRepo),
) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise UNAUTHORIZED

    token = authorization.split(" ", 1)[1]
    user = repo.get_by_id(_user_id_from_token(token))
    if user is None:
        raise UNAUTHORIZED
    return user
