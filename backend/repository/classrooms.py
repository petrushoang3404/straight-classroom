from fastapi import Depends
from backend.models.classrooms import Classroom
from backend.repository.database import get_session
from sqlmodel import Session
from sqlalchemy import text

class ClassroomRepo:
    def __init__(self, session: Session=Depends(get_session)):
        self.session = session
    
    def list(self, *, limit: int, offset: int):
        result = self.session.exec(
            text("""
                SELECT id, name, capacity, location
                FROM classroom
                ORDER BY id ASC
                LIMIT :limit
                OFFSET :offset
            """),
            params={
                "limit": limit,
                "offset": offset,
            },
        )
        rows = result.mappings().all()
        total = self.session.exec(
            text("SELECT COUNT(*) FROM classroom")
        ).scalar_one()
        return rows, total

    def get_by_id(self, classroom_id: int):
        result = self.session.exec(
            text("""
                SELECT id, name, capacity, location
                FROM classroom
                WHERE id = :classroom_id
            """),
            params={
                "classroom_id": classroom_id,
            },
        )
        return result.mappings().one_or_none()

    def create(
        self,
        create: dict,
    ):
        result = self.session.exec(
            text("""
                INSERT INTO classroom (name, capacity, location)
                VALUES (:name, :capacity, :location)
                RETURNING id, name, capacity, location
            """),
            params={
                "name": create["name"],
                "capacity": create["capacity"],
                "location": create["location"],
            },
        )
        classroom = result.mappings().one_or_none()
        self.session.commit()
        return classroom or None

    def update(
        self,
        classroom_id: int,
        updates: dict,
    ):
        result = self.session.exec(
            text("""
                UPDATE classroom
                SET name = COALESCE(:name, name),
                    capacity = COALESCE(:capacity, capacity),
                    location = COALESCE(:location, location)
                WHERE id = :classroom_id
                RETURNING id, name, capacity, location
            """),
            params={
                "classroom_id": classroom_id,
                "name": updates.get("name"),
                "capacity": updates.get("capacity"),
                "location": updates.get("location"),
            },
        )
        row = result.mappings().one_or_none()
        self.session.commit()
        return row or None

    def delete(self, classroom_id: int):
        result = self.session.exec(
            text("""
                DELETE FROM classroom
                WHERE id = :classroom_id
                RETURNING id, name, capacity, location
            """),
            params={
                "classroom_id": classroom_id,
            },
        )
        row = result.mappings().one_or_none()
        self.session.commit()
        return row or None
