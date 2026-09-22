from fastapi import Depends
from sqlalchemy import func
from sqlmodel import Session, select

from backend.models.teachers import Teacher
from backend.repository.database import get_session
from backend.repository.errors import NotFoundError


class TeacherRepo:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def get_by_id(self, teacher_id: int):
        return self.session.get(Teacher, teacher_id)

    def get_by_name(self, name: str, limit: int, offset: int):
        return self.session.exec(
            select(Teacher)
            .where(Teacher.name == name)
            .order_by(Teacher.id)
            .limit(limit)
            .offset(offset)
        ).all()

    def list(self, *, limit: int, offset: int):
        rows = self.session.exec(
            select(Teacher).order_by(Teacher.id).limit(limit).offset(offset)
        ).all()
        total = self.session.exec(select(func.count()).select_from(Teacher)).one()
        return rows, total

    def create(self, create: dict):
        teacher = Teacher(**create)
        self.session.add(teacher)
        self.session.commit()
        self.session.refresh(teacher)
        return teacher

    def update(self, teacher_id: int, updates: dict):
        teacher = self.session.get(Teacher, teacher_id)
        if teacher is None:
            return None
        for field, value in updates.items():
            setattr(teacher, field, value)
        self.session.add(teacher)
        self.session.commit()
        self.session.refresh(teacher)
        return teacher

    def delete(self, teacher_id: int):
        teacher = self.session.get(Teacher, teacher_id)
        if teacher is None:
            return None
        self.session.delete(teacher)
        self.session.commit()
        return teacher

    def list_classrooms(self, teacher_id: int):
        teacher = self.session.get(Teacher, teacher_id)
        if teacher is None:
            raise NotFoundError("Teacher not found")
        return teacher.classrooms
