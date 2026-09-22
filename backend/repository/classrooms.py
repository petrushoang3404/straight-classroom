from fastapi import Depends
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from backend.models.classroom_teachers import ClassroomTeacher
from backend.models.classrooms import Classroom
from backend.models.students import Student
from backend.models.teachers import Teacher
from backend.repository.database import get_session
from backend.repository.errors import ConflictError, NotFoundError


class ClassroomRepo:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def list(self, *, limit: int, offset: int):
        rows = self.session.exec(
            select(Classroom).order_by(Classroom.id).limit(limit).offset(offset)
        ).all()
        total = self.session.exec(select(func.count()).select_from(Classroom)).one()
        return rows, total

    def get_by_id(self, classroom_id: int):
        return self.session.get(Classroom, classroom_id)

    def create(self, create: dict):
        classroom = Classroom(**create)
        self.session.add(classroom)
        self.session.commit()
        self.session.refresh(classroom)
        return classroom

    def update(self, classroom_id: int, updates: dict):
        classroom = self.session.get(Classroom, classroom_id)
        if classroom is None:
            return None
        for field, value in updates.items():
            setattr(classroom, field, value)
        self.session.add(classroom)
        self.session.commit()
        self.session.refresh(classroom)
        return classroom

    def delete(self, classroom_id: int):
        classroom = self.session.get(Classroom, classroom_id)
        if classroom is None:
            return None
        self.session.delete(classroom)
        try:
            self.session.commit()
        except IntegrityError as exc:
            self.session.rollback()
            raise ConflictError("Classroom has students and cannot be deleted") from exc
        return classroom

    def list_students(self, classroom_id: int, *, limit: int, offset: int):
        if self.session.get(Classroom, classroom_id) is None:
            raise NotFoundError("Classroom not found")

        rows = self.session.exec(
            select(Student)
            .where(Student.classroom_id == classroom_id)
            .order_by(Student.id)
            .limit(limit)
            .offset(offset)
        ).all()
        total = self.session.exec(
            select(func.count())
            .select_from(Student)
            .where(Student.classroom_id == classroom_id)
        ).one()
        return rows, total

    def list_teachers(self, classroom_id: int):
        classroom = self.session.get(Classroom, classroom_id)
        if classroom is None:
            raise NotFoundError("Classroom not found")
        return classroom.teachers

    def assign_teacher(self, classroom_id: int, teacher_id: int):
        classroom = self.session.get(Classroom, classroom_id)
        if classroom is None:
            raise NotFoundError("Classroom not found")
        if self.session.get(Teacher, teacher_id) is None:
            raise NotFoundError("Teacher not found")
        if self.session.get(ClassroomTeacher, (classroom_id, teacher_id)) is not None:
            raise ConflictError("Teacher is already assigned to this classroom")

        self.session.add(
            ClassroomTeacher(classroom_id=classroom_id, teacher_id=teacher_id)
        )
        self.session.commit()
        self.session.refresh(classroom)
        return classroom

    def unassign_teacher(self, classroom_id: int, teacher_id: int):
        link = self.session.get(ClassroomTeacher, (classroom_id, teacher_id))
        if link is None:
            raise NotFoundError("Teacher is not assigned to this classroom")
        self.session.delete(link)
        self.session.commit()
