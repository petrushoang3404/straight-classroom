from fastapi import Depends
from sqlalchemy import func
from sqlmodel import Session, select

from backend.models.attendance import AttendanceRecord, AttendanceSession
from backend.models.classrooms import Classroom
from backend.models.students import Student
from backend.repository.database import get_session
from backend.repository.errors import NotFoundError


class AttendanceRepo:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def list(self, classroom_id: int, *, limit: int, offset: int):
        if self.session.get(Classroom, classroom_id) is None:
            raise NotFoundError("Classroom not found")

        rows = self.session.exec(
            select(AttendanceSession)
            .where(AttendanceSession.classroom_id == classroom_id)
            .order_by(
                AttendanceSession.session_date.desc(), AttendanceSession.id.desc()
            )
            .limit(limit)
            .offset(offset)
        ).all()
        total = self.session.exec(
            select(func.count())
            .select_from(AttendanceSession)
            .where(AttendanceSession.classroom_id == classroom_id)
        ).one()
        return rows, total

    def get_by_id(self, classroom_id: int, session_id: int):
        attendance = self.session.get(AttendanceSession, session_id)
        if attendance is None or attendance.classroom_id != classroom_id:
            return None
        return attendance

    def create(self, create: dict, records: list[dict]):
        student_ids = {record["student_id"] for record in records}
        in_classroom = set(
            self.session.exec(
                select(Student.id).where(
                    Student.classroom_id == create["classroom_id"],
                    Student.id.in_(student_ids),
                )
            )
        )
        if in_classroom != student_ids:
            raise NotFoundError("Student not found in this classroom")

        attendance = AttendanceSession(
            **create, records=[AttendanceRecord(**record) for record in records]
        )
        self.session.add(attendance)
        self.session.commit()
        self.session.refresh(attendance)
        return attendance

    def delete(self, attendance: AttendanceSession):
        self.session.delete(attendance)
        self.session.commit()
