from fastapi import Depends
from sqlalchemy import func
from sqlmodel import Session, select

from backend.models.classrooms import Classroom
from backend.models.materials import Material
from backend.repository.database import get_session
from backend.repository.errors import NotFoundError


class MaterialRepo:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def list(self, classroom_id: int, *, limit: int, offset: int):
        if self.session.get(Classroom, classroom_id) is None:
            raise NotFoundError("Classroom not found")

        rows = self.session.exec(
            select(Material)
            .where(Material.classroom_id == classroom_id)
            .order_by(Material.created_at.desc())
            .limit(limit)
            .offset(offset)
        ).all()
        total = self.session.exec(
            select(func.count())
            .select_from(Material)
            .where(Material.classroom_id == classroom_id)
        ).one()
        return rows, total

    def get_by_id(self, classroom_id: int, material_id: int):
        material = self.session.get(Material, material_id)
        if material is None or material.classroom_id != classroom_id:
            return None
        return material

    def create(self, create: dict):
        material = Material(**create)
        self.session.add(material)
        self.session.commit()
        self.session.refresh(material)
        return material

    def delete(self, material: Material):
        self.session.delete(material)
        self.session.commit()
