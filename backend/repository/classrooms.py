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

    async def get_by_id(self, classroom_id: int):
        result = self.session.execute(
            text("""
                SELECT id, name, capacity, location
                FROM classroom
                WHERE id = :classroom_id
            """),
            {
                "classroom_id": classroom_id,
            },
        )
        return result.mappings().one_or_none()

    async def create(
        self,
        create: dict,
    ):
        classroom = Classroom(**create)
        self.session.add(classroom)
        self.session.commit()
        self.session.refresh(classroom)
        return classroom or None
    
    async def update(
        self,
        classroom_id: int,
        updates: dict,
    ):
        if not updates:
            return await self.get_by_id(classroom_id)
        set_clauses = []
        params = {
            "classroom_id": classroom_id,
        }
        for field, value in updates.items():
            set_clauses.append(f"{field} = :{field}")
            params[field] = value
        query = f"""
            UPDATE classroom
            SET {", ".join(set_clauses)}
            WHERE id = :classroom_id
            RETURNING id, name, capacity, location
        """
        result = self.session.execute(
            text(query),
            params,
        )
        row = result.mappings().one_or_none()
        self.session.commit()
        return row
