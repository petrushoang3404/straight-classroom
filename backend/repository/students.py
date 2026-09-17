from fastapi import Depends
from sqlmodel import Session, text

from backend.repository.database import get_session


class StudentRepo:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def get_by_id(self, student_id: int):
        result = self.session.exec(
            text("""
                SELECT id, saint_name, first_name, last_name, division, classroom_id
                FROM student
                WHERE id = :student_id"""),
            params={
                "student_id": student_id,
            },
        )
        return result.mappings().one_or_none()

    def get_by_name(self, name: str, limit: int, offset: int):
        result = self.session.exec(
            text("""
                SELECT id, saint_name, first_name, last_name, division, classroom_id
                FROM student
                WHERE first_name = :name OR last_name = :name
                ORDER BY id ASC
                LIMIT :limit
                OFFSET :offset"""),
            params={
                "name": name,
                "limit": limit,
                "offset": offset,
            },
        )
        return result.mappings().all()

    def list(self, *, limit: int, offset: int):
        result = self.session.exec(
            text("""
                SELECT id, saint_name, first_name, last_name, division, classroom_id
                FROM student
                ORDER BY id ASC
                LIMIT :limit
                OFFSET :offset"""),
            params={
                "limit": limit,
                "offset": offset,
            },
        )
        rows = result.mappings().all()
        total = self.session.exec(text("SELECT COUNT(*) FROM student")).scalar_one()
        return rows, total

    def create(self, create: dict):
        result = self.session.exec(
            text("""
                INSERT INTO student (saint_name, first_name, last_name, division, classroom_id)
                VALUES (:saint_name, :first_name, :last_name, :division, :classroom_id)
                RETURNING id, saint_name, first_name, last_name, division, classroom_id"""),
            params={
                "saint_name": create["saint_name"],
                "first_name": create["first_name"],
                "last_name": create["last_name"],
                "division": create["division"],
                "classroom_id": create["classroom_id"],
            },
        )
        student = result.mappings().one_or_none()
        self.session.commit()
        return student or None

    def update(self, student_id: int, update: dict):
        result = self.session.exec(
            text("""
                UPDATE student
                SET saint_name = COALESCE(:saint_name, saint_name),
                    first_name = COALESCE(:first_name, first_name),
                    last_name = COALESCE(:last_name, last_name),
                    division = COALESCE(:division, division),
                    classroom_id = COALESCE(:classroom_id, classroom_id)
                WHERE id = :student_id
                RETURNING id, saint_name, first_name, last_name, division, classroom_id"""),
            params={
                "student_id": student_id,
                "saint_name": update.get("saint_name"),
                "first_name": update.get("first_name"),
                "last_name": update.get("last_name"),
                "division": update.get("division"),
                "classroom_id": update.get("classroom_id"),
            },
        )
        student = result.mappings().one_or_none()
        self.session.commit()
        return student or None

    def delete(self, student_id: int):
        result = self.session.exec(
            text("""
                DELETE FROM student
                WHERE id = :student_id
                RETURNING id, saint_name, first_name, last_name, division, classroom_id"""),
            params={
                "student_id": student_id,
            },
        )
        student = result.mappings().one_or_none()
        self.session.commit()
        return student or None