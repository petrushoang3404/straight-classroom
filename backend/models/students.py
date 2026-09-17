from sqlmodel import Field, SQLModel


class Student(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    saint_name: str = Field(max_length=255)
    first_name: str = Field(max_length=255)
    last_name: str = Field(max_length=255)
    division: str = Field(max_length=255)
    classroom_id: int = Field(foreign_key="classroom.id")