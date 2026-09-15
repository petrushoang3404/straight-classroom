from backend.models.teachers import Teacher
from backend.repository.database import get_session
from fastapi import Depends
from sqlmodel import Session, text


class TeacherRepo:
    def __init__(self, session: Session=Depends(get_session)):
        self.session = session

    def get_by_id(self, teacher_id: int):
        result = self.session.exec(
            text("""
                SELECT id, name, subject
                FROM teacher
                WHERE id = :teacher_id"""
        ),
        params={
            "teacher_id": teacher_id,
        },
        )
        return result.mappings().one_or_none()

    def get_by_name(self, name: str, limit: int, offset: int):
        result = self.session.exec(
            text("""
                SELECT id, name, subject
                FROM teacher
                WHERE name = :name
                ORDER BY id ASC
                LIMIT :limit
                OFFSET :offset"""
        ),
        params={
            "name": name,
            "limit": limit,
            "offset": offset,
        })
        return result.mappings().all()

    def list(self, *, limit: int, offset: int):
        result = self.session.exec(
            text("""
                SELECT id, name, subject
                FROM teacher
                ORDER BY id ASC
                LIMIT :limit
                OFFSET :offset"""
        ),
        params={
            "limit": limit,
            "offset": offset,
        },
        )
        rows = result.mappings().all()
        total = self.session.exec(
            text("SELECT COUNT(*) FROM teacher")
        ).scalar_one()
        return rows, total

    def create(self, create: dict):
        result = self.session.exec(
            text("""
                INSERT INTO teacher (name, subject)
                VALUES (:name, :subject)
                RETURNING id, name, subject"""
        ),
        params={
            "name": create["name"],
            "subject": create["subject"],
        },
        )
        teacher = result.mappings().one_or_none()
        self.session.commit()
        return teacher or None
    
    def update(self, teacher_id: int, updates: dict):
        result = self.session.exec(
            text("""
                UPDATE teacher
                SET name = COALESCE(:name, name),
                    subject = COALESCE(:subject, subject)
                WHERE id = :teacher_id
                RETURNING id, name, subject"""
        ),
        params={
            "teacher_id": teacher_id,
            "name": updates.get("name"),
            "subject": updates.get("subject"),
        },
        )
        teacher = result.mappings().one_or_none()
        self.session.commit()
        return teacher or None

    def delete(self, teacher_id: int):
        result = self.session.exec(
            text("""
                DELETE FROM teacher
                WHERE id = :teacher_id
                RETURNING id, name, subject"""
        ),
        params={
            "teacher_id": teacher_id,
        },
        )
        teacher = result.mappings().one_or_none()
        self.session.commit()
        return teacher or None