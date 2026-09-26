"""Write `data/seed/seed.json` into the database, idempotently.

    make be-seed-load                 # apply
    make be-seed-load args=--dry-run  # show what would change, touch nothing

Matching is by natural key (classroom name, teacher name, student name + date of
birth) rather than by id, so the sheet can be corrected and this re-run without
creating duplicates. Re-running with no spreadsheet changes reports everything
as unchanged, which is the check that the import is really idempotent.
"""

import argparse
import json
from collections import Counter
from datetime import date
from pathlib import Path

from sqlmodel import Session, select

# Importing every model module registers its table on SQLModel's metadata;
# without it, resolving the relationships below fails (same reason as
# backend/scripts/seed_user.py and backend/alembic/env.py).
import backend.models.materials
import backend.models.users  # noqa: F401
from backend.models.classroom_teachers import ClassroomTeacher
from backend.models.classrooms import Classroom
from backend.models.students import Student
from backend.models.teachers import Teacher
from backend.repository.database import engine
from backend.scripts.seed.build_seed import DEFAULT_OUTPUT
from backend.scripts.seed.normalizers import compare_key

STUDENT_FIELDS = tuple(
    name for name in Student.model_fields if name not in {"id", "classroom_id"}
)
TEACHER_FIELDS = tuple(name for name in Teacher.model_fields if name != "id")
DATE_FIELDS = frozenset(
    {
        "date_of_birth",
        "date_of_baptism",
        "date_of_first_communion",
        "date_of_confirmation",
    }
)


def _coerce(field: str, value):
    if field in DATE_FIELDS and isinstance(value, str):
        return date.fromisoformat(value)
    return value


def _student_key(record) -> tuple:
    """Natural key for a student: who they are, per the parish's own sheet."""
    if isinstance(record, dict):
        last_name, first_name = record["last_name"], record["first_name"]
        birth = _coerce("date_of_birth", record.get("date_of_birth"))
    else:
        last_name, first_name = record.last_name, record.first_name
        birth = record.date_of_birth
    return compare_key(last_name), compare_key(first_name), birth


def _apply(instance, values: dict, fields) -> list[str]:
    """Set `fields` from `values`, returning the names that actually changed."""
    changed = []
    for field in fields:
        if field not in values:
            continue
        new_value = _coerce(field, values[field])
        if getattr(instance, field) != new_value:
            setattr(instance, field, new_value)
            changed.append(field)
    return changed


class Loader:
    def __init__(self, session: Session, *, update: bool, verbose: bool):
        self.session = session
        self.update = update
        self.verbose = verbose
        self.counts: Counter = Counter()
        self.notes: list[str] = []

    def _record(self, kind: str, action: str, label: str, changed: list[str]) -> None:
        self.counts[f"{kind} {action}"] += 1
        if action == "created" or changed:
            detail = f" ({', '.join(changed)})" if changed else ""
            self.notes.append(f"{action:9} {kind:9} {label}{detail}")

    def classroom(self, payload: dict) -> Classroom:
        existing = self.session.exec(
            select(Classroom).where(Classroom.name == payload["name"])
        ).first()
        values = {
            "name": payload["name"],
            "capacity": payload["capacity"],
            "location": payload["location"],
        }
        if existing is None:
            classroom = Classroom(**values)
            self.session.add(classroom)
            self.session.flush()
            self._record("classroom", "created", classroom.name, [])
            return classroom

        changed = (
            _apply(existing, values, ("capacity", "location")) if self.update else []
        )
        self._record(
            "classroom", "updated" if changed else "unchanged", existing.name, changed
        )
        return existing

    def teacher(self, payload: dict, classroom: Classroom) -> Teacher:
        existing = self.session.exec(
            select(Teacher).where(
                Teacher.name == payload["name"], Teacher.division == payload["division"]
            )
        ).first()
        if existing is None:
            teacher = Teacher(
                **{k: v for k, v in payload.items() if k in TEACHER_FIELDS}
            )
            self.session.add(teacher)
            self.session.flush()
            self._record("teacher", "created", teacher.name, [])
        else:
            changed = _apply(existing, payload, TEACHER_FIELDS) if self.update else []
            self._record(
                "teacher", "updated" if changed else "unchanged", existing.name, changed
            )
            teacher = existing

        link = self.session.get(ClassroomTeacher, (classroom.id, teacher.id))
        if link is None:
            self.session.add(
                ClassroomTeacher(classroom_id=classroom.id, teacher_id=teacher.id)
            )
            self._record("link", "created", f"{teacher.name} -> {classroom.name}", [])
        else:
            self._record("link", "unchanged", f"{teacher.name} -> {classroom.name}", [])
        return teacher

    def students(self, payloads: list[dict], classroom: Classroom) -> None:
        existing_rows = self.session.exec(
            select(Student).where(Student.classroom_id == classroom.id)
        ).all()
        by_key: dict[tuple, list[Student]] = {}
        for row in existing_rows:
            by_key.setdefault(_student_key(row), []).append(row)

        for payload in payloads:
            values = {k: v for k, v in payload.items() if k in STUDENT_FIELDS}
            label = f"{payload['last_name']} {payload['first_name']}"
            matches = by_key.get(_student_key(payload), [])
            if len(matches) > 1:
                self.notes.append(
                    f"warning   student   {label}: {len(matches)} existing rows match; "
                    "updated the first"
                )
            if not matches:
                student = Student(classroom_id=classroom.id, **values)
                self.session.add(student)
                self._record("student", "created", label, [])
                continue
            changed = _apply(matches[0], values, STUDENT_FIELDS) if self.update else []
            self._record(
                "student", "updated" if changed else "unchanged", label, changed
            )

    def run(self, payload: dict) -> None:
        for classroom_payload in payload["classrooms"]:
            classroom = self.classroom(classroom_payload)
            for teacher_payload in classroom_payload["teachers"]:
                self.teacher(teacher_payload, classroom)
            self.students(classroom_payload["students"], classroom)
        self.session.flush()


def main() -> int:
    parser = argparse.ArgumentParser(description="Load seed.json into the database")
    parser.add_argument("--file", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report the changes and roll back instead of committing",
    )
    parser.add_argument(
        "--no-update",
        dest="update",
        action="store_false",
        help="Only insert new records; leave existing rows exactly as they are",
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Echo the SQL statements"
    )
    args = parser.parse_args()

    if not args.file.is_file():
        print(f"No seed file at {args.file}; run `make be-seed-build` first.")
        return 1

    # The shared engine echoes SQL, which buries this script's own output.
    engine.echo = args.verbose
    payload = json.loads(args.file.read_text(encoding="utf-8"))

    with Session(engine) as session:
        loader = Loader(session, update=args.update, verbose=args.verbose)
        loader.run(payload)

        for note in loader.notes:
            print(note)
        print()
        for key in sorted(loader.counts):
            print(f"{loader.counts[key]:5}  {key}")

        if args.dry_run:
            session.rollback()
            print("\nDry run: rolled back, nothing was written.")
        else:
            session.commit()
            print(f"\nCommitted {args.file}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
