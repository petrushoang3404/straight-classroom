from sqlmodel import Field, SQLModel


class Classroom(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    capacity: int
    location: str
