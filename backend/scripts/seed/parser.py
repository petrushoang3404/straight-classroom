"""Read one exported "Sơ yếu lý lịch" sheet into normalised records.

The sheets are Google Sheets exports, so a file is not a plain table: there is a
title, a note box, a block of teachers in charge, the student table itself, and
a legend at the bottom.

    SƠ YẾU LÝ LỊCH - NGHĨA SĨ 1A
    Năm học 2025 - 2026
    Lưu ý: ...
    ,Huynh Trưởng phụ trách,,SĐT
    ,Luca Nguyễn Ngọc Hoà,,0919.354.439
    STT,TÊN THÁNH,HỌ,TÊN,...      <- the real header
    1,AUGUSTINO,NGUYỄN TRẦN BẢO,AN,...
    ...
    ,Tình trạng hiện tại           <- legend, not students

So the parser finds the blocks by their labels instead of by fixed row numbers,
and reports anything it cannot place rather than dropping it.
"""

import csv
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from backend.scripts.seed.normalizers import (
    clean_cell,
    compare_key,
    is_known_saint_name,
    normalize_division,
    normalize_full_name,
    normalize_person_name,
    normalize_phone_number,
    normalize_place,
    normalize_saint_name,
    parse_date,
    split_saint_name,
    truncate,
)

# Spreadsheet header -> Student field. Keys are accent/case-insensitive
# (`compare_key`), and synonyms map onto the same field so a renamed column in
# next year's sheet keeps working.
STUDENT_COLUMNS = {
    "stt": "_row_number",
    "ten thanh": "saint_name",
    "ho": "last_name",
    "ho va ten dem": "last_name",
    "ten": "first_name",
    "ten goi": "first_name",
    "tinh trang hien tai": "_status",
    "tinh trang": "_status",
    "ghi chu": "_note",
    "ngay sinh": "date_of_birth",
    "noi sinh": "place_of_birth",
    "ngay rua toi": "date_of_baptism",
    "noi rua toi": "place_of_baptism",
    "ngay ruoc le": "date_of_first_communion",
    "noi ruoc le": "place_of_first_communion",
    "ngay them suc": "date_of_confirmation",
    "noi them suc": "place_of_confirmation",
    "ten cha": "father_name",
    "sdt cha": "father_phone_number",
    "dt cha": "father_phone_number",
    "so dien thoai cha": "father_phone_number",
    "ten me": "mother_name",
    "sdt me": "mother_phone_number",
    "dt me": "mother_phone_number",
    "so dien thoai me": "mother_phone_number",
    "dia chi nha": "address",
    "dia chi": "address",
}

DATE_FIELDS = (
    "date_of_birth",
    "date_of_baptism",
    "date_of_first_communion",
    "date_of_confirmation",
)
PLACE_FIELDS = (
    "place_of_birth",
    "place_of_baptism",
    "place_of_first_communion",
    "place_of_confirmation",
)
PHONE_FIELDS = ("father_phone_number", "mother_phone_number")

# `saint_name` is NOT NULL in the database, and a student without one still has
# to be seeded, so this stands in until the parish fills it in.
UNKNOWN_SAINT_NAME = "Chưa rõ"

# Nobody in a catechism class was born before this; a date older than that is a
# typo (usually a mis-keyed year) worth a human look.
EARLIEST_PLAUSIBLE_BIRTH_YEAR = 1990


@dataclass
class Issue:
    """Something a human should look at, not a reason to stop parsing."""

    source: str
    location: str
    message: str

    def __str__(self) -> str:
        return f"{self.source}: {self.location}: {self.message}"


@dataclass
class ParsedClassroom:
    name: str
    division: str
    capacity: int
    location: str
    school_year: str | None
    source_file: str
    teachers: list[dict] = field(default_factory=list)
    students: list[dict] = field(default_factory=list)
    issues: list[Issue] = field(default_factory=list)


def _row(rows: list[list[str]], index: int, width: int) -> list[str]:
    row = rows[index]
    return list(row) + [""] * (width - len(row))


def _find_header_row(rows: list[list[str]]) -> int | None:
    for index, row in enumerate(rows):
        if any(compare_key(cell) == "stt" for cell in row):
            return index
    return None


def _find_teacher_block(rows: list[list[str]]) -> tuple[int, int, int] | None:
    """Locate the "Huynh Trưởng phụ trách" block: (row, name col, phone col)."""
    for index, row in enumerate(rows):
        for column, cell in enumerate(row):
            if "huynh truong" in compare_key(cell):
                phone_column = next(
                    (
                        other
                        for other, value in enumerate(row)
                        if other != column
                        and compare_key(value) in {"sdt", "so dien thoai", "dt"}
                    ),
                    column + 2,
                )
                return index, column, phone_column
    return None


def _parse_school_year(rows: list[list[str]], filename: str) -> str | None:
    """`Năm học 2025 - 2026` -> `2025-2026`, else `[25-26]` -> `2025-2026`."""
    for row in rows[:10]:
        for cell in row:
            key = compare_key(cell)
            if key.startswith("nam hoc"):
                years = [part for part in key.split(" ") if part.isdigit()]
                if len(years) == 2:
                    return f"{years[0]}-{years[1]}"
    head = filename.split("]")[0].lstrip("[")
    parts = head.split("-")
    if len(parts) == 2 and all(part.strip().isdigit() for part in parts):
        return f"20{parts[0].strip()}-20{parts[1].strip()}"
    return None


def _parse_classroom_identity(path: Path, rows: list[list[str]]) -> tuple[str, str]:
    """Pull (classroom name, division) out of the file name.

    `[25-26] SYLL - PĐ NGHĨA SĨ - Lớp Nghĩa Sĩ 1A.csv` gives division
    `Nghĩa sĩ` (spelled as the app's dropdown does) and classroom `Nghĩa sĩ 1A`.
    Falls back to the sheet title row, then to the file name as a whole.
    """
    parts = [part.strip() for part in path.stem.split(" - ")]
    division = None
    label = None
    for part in parts:
        key = compare_key(part)
        if key.startswith(("pd ", "phan doan ")):
            division = normalize_division(part)
        elif key.startswith("lop "):
            label = part.split(" ", 1)[1].strip()

    if label is None:
        for row in rows[:5]:
            for cell in row:
                if compare_key(cell).startswith("so yeu ly lich") and " - " in cell:
                    label = cell.split(" - ", 1)[1].strip()
                    break
            if label:
                break
    if label is None:
        label = parts[-1] if parts else path.stem
    if division is None:
        division = normalize_division(label) or label

    # `Nghĩa Sĩ 1A` with division `Nghĩa sĩ` -> `Nghĩa sĩ 1A`, so the same words
    # are not stored with two different spellings.
    words = label.split(" ")
    division_word_count = len(division.split(" "))
    if compare_key(" ".join(words[:division_word_count])) == compare_key(division):
        suffix = " ".join(words[division_word_count:]).strip()
        name = f"{division} {suffix}".strip()
    else:
        name = normalize_person_name(label) or label
    return name, division


def _parse_teachers(
    rows: list[list[str]],
    width: int,
    source: str,
    division: str,
    issues: list[Issue],
    stop: int,
) -> list[dict]:
    """Read the teacher block. `stop` is the student header row: the block ends
    at the first blank name, and never runs into the student table."""
    block = _find_teacher_block(rows)
    if block is None:
        issues.append(
            Issue(source, "teachers", "no 'Huynh Trưởng phụ trách' block found")
        )
        return []

    start, name_column, phone_column = block
    teachers: list[dict] = []
    for index in range(start + 1, min(stop, len(rows))):
        row = _row(rows, index, width)
        raw_name = clean_cell(row[name_column])
        if raw_name is None:
            break

        location = f"teacher row {index + 1}"
        saint_name, name = split_saint_name(raw_name)
        if saint_name is None:
            issues.append(
                Issue(
                    source,
                    location,
                    f"no saint name recognised in {raw_name!r}; stored as name only",
                )
            )
        phone_number, problem = normalize_phone_number(row[phone_column])
        if problem:
            issues.append(Issue(source, location, problem))

        teachers.append(
            {
                "name": truncate(name),
                "saint_name": truncate(saint_name),
                "division": division,
                "phone_number": phone_number,
            }
        )
    return teachers


def _check_dates(
    student: dict, source: str, location: str, issues: list[Issue]
) -> None:
    # Local vs UTC is immaterial for a plausibility check on a birth date.
    today = datetime.now(tz=UTC).date()
    birth = student.get("date_of_birth")
    if birth is None:
        issues.append(Issue(source, location, "missing date of birth"))
    elif birth > today:
        issues.append(
            Issue(source, location, f"date of birth is in the future: {birth}")
        )
    elif birth.year < EARLIEST_PLAUSIBLE_BIRTH_YEAR:
        issues.append(Issue(source, location, f"implausible date of birth: {birth}"))

    for field_name in DATE_FIELDS[1:]:
        value = student.get(field_name)
        if value is None:
            continue
        if birth is not None and value < birth:
            issues.append(
                Issue(
                    source,
                    location,
                    f"{field_name} ({value}) is before the date of birth ({birth})",
                )
            )
        if value > today:
            issues.append(
                Issue(source, location, f"{field_name} is in the future: {value}")
            )


SACRAMENTS = (
    ("date_of_baptism", "place_of_baptism", "rửa tội"),
    ("date_of_first_communion", "place_of_first_communion", "rước lễ"),
    ("date_of_confirmation", "place_of_confirmation", "thêm sức"),
)


def _check_sacraments(
    student: dict, source: str, location: str, issues: list[Issue]
) -> None:
    """Half-recorded sacraments: a date with no place, or a place with no date."""
    for date_field, place_field, label in SACRAMENTS:
        has_date = student.get(date_field) is not None
        has_place = student.get(place_field) is not None
        if has_date and not has_place:
            issues.append(
                Issue(source, location, f"{label}: date recorded, place missing")
            )
        elif has_place and not has_date:
            issues.append(
                Issue(source, location, f"{label}: place recorded, date missing")
            )


def _check_contacts(
    student: dict, source: str, location: str, issues: list[Issue]
) -> None:
    """A student the parish cannot phone anybody about is worth surfacing."""
    if not (student.get("father_name") or student.get("mother_name")):
        issues.append(Issue(source, location, "no parent or guardian name"))
    if not (student.get("father_phone_number") or student.get("mother_phone_number")):
        issues.append(Issue(source, location, "no parent phone number"))


def _parse_student(
    raw: dict[str, str],
    *,
    division: str,
    source: str,
    location: str,
    issues: list[Issue],
) -> dict | None:
    last_name = normalize_person_name(raw.get("last_name"))
    first_name = normalize_person_name(raw.get("first_name"))
    if not last_name or not first_name:
        issues.append(Issue(source, location, "skipped: row has no family/given name"))
        return None

    saint_name = normalize_saint_name(raw.get("saint_name"))
    if saint_name is None:
        issues.append(
            Issue(
                source,
                location,
                f"missing saint name; stored as {UNKNOWN_SAINT_NAME!r}",
            )
        )
        saint_name = UNKNOWN_SAINT_NAME
    elif not is_known_saint_name(saint_name):
        issues.append(
            Issue(
                source,
                location,
                f"unrecognised saint name {saint_name!r}; check spelling",
            )
        )

    student: dict = {
        "saint_name": truncate(saint_name),
        "first_name": truncate(first_name),
        "last_name": truncate(last_name),
        "division": division,
    }

    for field_name in DATE_FIELDS:
        value, problem = parse_date(raw.get(field_name))
        if problem:
            issues.append(Issue(source, location, f"{field_name}: {problem}"))
        student[field_name] = value

    for field_name in PLACE_FIELDS:
        student[field_name] = truncate(normalize_place(raw.get(field_name)))

    for field_name in PHONE_FIELDS:
        value, problem = normalize_phone_number(raw.get(field_name))
        if problem:
            issues.append(Issue(source, location, f"{field_name}: {problem}"))
        student[field_name] = value

    student["father_name"] = truncate(normalize_full_name(raw.get("father_name")))
    student["mother_name"] = truncate(normalize_full_name(raw.get("mother_name")))

    address = clean_cell(raw.get("address"))
    if address is None:
        issues.append(Issue(source, location, "missing home address"))
    student["address"] = truncate(address)

    _check_dates(student, source, location, issues)
    _check_sacraments(student, source, location, issues)
    _check_contacts(student, source, location, issues)

    # Not columns on the Student table; carried along so the sheet's own view of
    # who is still attending survives into the reviewable seed file.
    row_number = clean_cell(raw.get("_row_number"))
    student["metadata"] = {
        "row": int(row_number) if row_number and row_number.isdigit() else None,
        "status": clean_cell(raw.get("_status")),
        "note": clean_cell(raw.get("_note")),
    }
    return student


def parse_students_file(
    path: Path,
    *,
    capacity: int | None = None,
    location: str = "Chưa cập nhật",
) -> ParsedClassroom:
    """Parse one classroom sheet. Never raises on bad data; collects issues."""
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = [row for row in csv.reader(handle)]

    source = path.name
    issues: list[Issue] = []
    width = max((len(row) for row in rows), default=0)

    name, division = _parse_classroom_identity(path, rows)
    school_year = _parse_school_year(rows, path.stem)

    header_index = _find_header_row(rows)
    teachers = _parse_teachers(
        rows,
        width,
        source,
        division,
        issues,
        stop=header_index if header_index is not None else len(rows),
    )

    if header_index is None:
        issues.append(
            Issue(source, "header", "no 'STT' header row found; no students read")
        )
        return ParsedClassroom(
            name=name,
            division=division,
            capacity=capacity or 1,
            location=location,
            school_year=school_year,
            source_file=source,
            teachers=teachers,
            issues=issues,
        )

    header = _row(rows, header_index, width)
    fields: dict[int, str] = {}
    for column, cell in enumerate(header):
        label = clean_cell(cell)
        if label is None:
            continue
        field_name = STUDENT_COLUMNS.get(compare_key(label))
        if field_name is None:
            issues.append(
                Issue(
                    source,
                    f"column {column + 1}",
                    f"unmapped column {label!r}; ignored",
                )
            )
            continue
        fields[column] = field_name

    missing = {"saint_name", "first_name", "last_name"} - set(fields.values())
    if missing:
        issues.append(
            Issue(
                source,
                "header",
                f"header is missing required columns: {sorted(missing)}",
            )
        )

    students: list[dict] = []
    seen: dict[tuple, str] = {}
    for index in range(header_index + 1, len(rows)):
        row = _row(rows, index, width)
        raw = {name_: row[column] for column, name_ in fields.items()}
        row_number = clean_cell(raw.get("_row_number")) or ""
        has_name = bool(clean_cell(raw.get("last_name"))) and bool(
            clean_cell(raw.get("first_name"))
        )
        if not row_number.isdigit():
            if not has_name:
                # Blank line or the legend block at the bottom: table is over.
                break
            issues.append(
                Issue(
                    source, f"row {index + 1}", "row has names but no STT; kept anyway"
                )
            )

        display_name = " ".join(
            part
            for part in (
                normalize_person_name(raw.get("last_name")),
                normalize_person_name(raw.get("first_name")),
            )
            if part
        )
        student = _parse_student(
            raw,
            division=division,
            source=source,
            location=f"STT {row_number or '?'} {display_name} (csv line {index + 1})",
            issues=issues,
        )
        if student is None:
            continue

        key = (
            compare_key(student["last_name"]),
            compare_key(student["first_name"]),
            student["date_of_birth"],
        )
        if key in seen:
            issues.append(
                Issue(
                    source,
                    f"csv line {index + 1}",
                    f"same name and date of birth as {seen[key]}; possible duplicate",
                )
            )
        else:
            seen[key] = f"STT {row_number}"
        students.append(student)

    return ParsedClassroom(
        name=name,
        division=division,
        capacity=capacity or max(len(students), 1),
        location=location,
        school_year=school_year,
        source_file=source,
        teachers=teachers,
        students=students,
        issues=issues,
    )
