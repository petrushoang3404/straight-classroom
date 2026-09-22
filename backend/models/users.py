from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(max_length=255, unique=True, index=True)
    hashed_password: str
    display_name: str = Field(max_length=255)
