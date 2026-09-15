from sqlmodel import Field, SQLModel


class Teacher(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str = Field(max_length=255)
    subject: str = Field(max_length=255)
