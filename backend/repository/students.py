from fastapi import Depends
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from backend.models.students import Student
from backend.repository.database import get_session
from backend.repository.errors import NotFoundError


class StudentRepo:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def get_by_id(self, student_id: int):
        return self.session.get(Student, student_id)

    def get_by_name(
        self,
        name: str,
        limit: int,
        offset: int,
        *,
        classroom_ids: list[int] | None = None,
    ):
        statement = select(Student).where(
            (Student.first_name == name) | (Student.last_name == name)
        )
        if classroom_ids is not None:
            statement = statement.where(Student.classroom_id.in_(classroom_ids))
        return self.session.exec(
            statement.order_by(Student.id).limit(limit).offset(offset)
        ).all()

    def list(self, *, limit: int, offset: int, classroom_ids: list[int] | None = None):
        statement = select(Student)
        count_statement = select(func.count()).select_from(Student)
        if classroom_ids is not None:
            statement = statement.where(Student.classroom_id.in_(classroom_ids))
            count_statement = count_statement.where(
                Student.classroom_id.in_(classroom_ids)
            )

        rows = self.session.exec(
            statement.order_by(Student.id).limit(limit).offset(offset)
        ).all()
        total = self.session.exec(count_statement).one()
        return rows, total

    def create(self, create: dict):
        student = Student(**create)
        self.session.add(student)
        try:
            self.session.commit()
        except IntegrityError as exc:
            self.session.rollback()
            raise NotFoundError("Classroom not found") from exc
        self.session.refresh(student)
        return student

    def update(self, student_id: int, update: dict):
        student = self.session.get(Student, student_id)
        if student is None:
            return None
        for field, value in update.items():
            setattr(student, field, value)
        self.session.add(student)
        try:
            self.session.commit()
        except IntegrityError as exc:
            self.session.rollback()
            raise NotFoundError("Classroom not found") from exc
        self.session.refresh(student)
        return student

    def delete(self, student_id: int):
        student = self.session.get(Student, student_id)
        if student is None:
            return None
        self.session.delete(student)
        self.session.commit()
        return student
