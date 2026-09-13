from fastapi import Depends
from backend.models.classrooms import Classroom
from backend.repository.database import get_session
from sqlmodel import Session
from sqlalchemy import text

class ClassroomRepo:
    def __init__(self, session: Session=Depends(get_session)):
        self.session = session
    
    async def list(self, *, limit: int, offset: int):
        result = self.session.execute(
            text("""
                SELECT id, name, capacity, location
                FROM classroom
                ORDER BY id ASC
                LIMIT :limit
                OFFSET :offset
            """),
            {
                "limit": limit,
                "offset": offset,
            },
        )
        rows = result.mappings().all()
        total = self.session.execute(
            text("SELECT COUNT(*) FROM classroom")
        ).scalar_one()
        return rows, total

    async def create(
        self,
        create: dict,
    ):
        classroom = Classroom(**create)
        self.session.add(classroom)
        self.session.commit()
        self.session.refresh(classroom)
        return classroom or None
