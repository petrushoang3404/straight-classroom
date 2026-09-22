from datetime import UTC, datetime, timedelta
from typing import Annotated

import bcrypt
import jwt
from fastapi import Depends, Header, HTTPException, Path, status
from sqlmodel import Session, select

from backend.config import settings
from backend.models.classroom_teachers import ClassroomTeacher
from backend.models.users import User
from backend.repository.database import get_session
from backend.repository.users import UserRepo

JWT_ALGORITHM = "HS256"

UNAUTHORIZED = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Not authenticated",
    headers={"WWW-Authenticate": "Bearer"},
)

FORBIDDEN = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Insufficient permissions",
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


def require_admin(user: Annotated[User, Depends(get_current_user)]) -> User:
    if user.role != "admin":
        raise FORBIDDEN
    return user


def is_assigned_to_classroom(session: Session, user: User, classroom_id: int) -> bool:
    """Whether `user` may manage the given classroom: admins always can,
    teachers only for classrooms they're linked to via ClassroomTeacher."""
    if user.role == "admin":
        return True
    if user.teacher_id is None:
        return False
    return session.get(ClassroomTeacher, (classroom_id, user.teacher_id)) is not None


def accessible_classroom_ids(session: Session, user: User) -> list[int] | None:
    """Classroom ids `user` may manage. None means unrestricted (admin)."""
    if user.role == "admin":
        return None
    if user.teacher_id is None:
        return []
    return list(
        session.exec(
            select(ClassroomTeacher.classroom_id).where(
                ClassroomTeacher.teacher_id == user.teacher_id
            )
        ).all()
    )


def require_classroom_access(
    classroom_id: Annotated[int, Path(gt=0)],
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
) -> User:
    if not is_assigned_to_classroom(session, user, classroom_id):
        raise FORBIDDEN
    return user
