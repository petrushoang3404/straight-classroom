from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


class AuthSessionResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    token: str
    username: str
    display_name: str = Field(alias="displayName")
    provider: Literal["password", "google"]
