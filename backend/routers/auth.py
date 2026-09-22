from backend.repository.users import UserRepo
from backend.schemas.auth import AuthSessionResponse, LoginRequest
from backend.security import create_access_token, verify_password
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=AuthSessionResponse)
def login(
    credentials: LoginRequest,
    repo: UserRepo = Depends(UserRepo),
):
    user = repo.get_by_username(credentials.username)
    if user is None or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    return AuthSessionResponse(
        token=create_access_token(user),
        username=user.username,
        display_name=user.display_name,
        provider="password",
        role=user.role,
    )
