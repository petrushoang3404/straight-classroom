"""Turn the spreadsheets in `data/` into a reviewable `seed.json`.

    make be-seed-build

Reads every `data/students/*.csv`, normalises the cells (see `normalizers.py`),
adds the attributes the sheets do not carry (division, classroom, capacity) and
writes:

    data/seed/seed.json     what `load_seed` will write to the database
    data/seed/report.md     every value this tool could not vouch for

No database is touched here, so it is safe to run and re-run, and the JSON is
meant to be read by a human before it goes anywhere near production.
"""

import argparse
import json
from dataclasses import asdict
from datetime import UTC, date, datetime
from pathlib import Path

from backend.scripts.seed.normalizers import compare_key
from backend.scripts.seed.parser import Issue, ParsedClassroom, parse_students_file

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DATA_DIR = REPO_ROOT / "data"
DEFAULT_OUTPUT = DEFAULT_DATA_DIR / "seed" / "seed.json"
DEFAULT_REPORT = DEFAULT_DATA_DIR / "seed" / "report.md"


def _json_default(value):
    if isinstance(value, date):
        return value.isoformat()
    raise TypeError(f"cannot serialise {type(value).__name__}")


def _filter_students(
    classroom: ParsedClassroom, excluded_statuses: list[str]
) -> ParsedClassroom:
    if not excluded_statuses:
        return classroom
    excluded = {compare_key(status) for status in excluded_statuses}
    kept = []
    for student in classroom.students:
        status = student["metadata"].get("status")
        if status is not None and compare_key(status) in excluded:
            classroom.issues.append(
                Issue(
                    classroom.source_file,
                    f"row {student['metadata'].get('row')}",
                    f"excluded by --exclude-status: {status!r}",
                )
            )
            continue
        kept.append(student)
    classroom.students = kept
    return classroom


def _write_report(path: Path, classrooms: list[ParsedClassroom], data_dir: Path) -> int:
    lines = [
        "# Seed data report",
        "",
        f"Generated: {datetime.now(tz=UTC).isoformat(timespec='seconds')}",
        f"Source: `{data_dir}`",
        "",
        "Every line below is a value the tool could not vouch for. Fix it in the",
        "spreadsheet and re-run `make be-seed-build`, or accept it as-is.",
        "",
    ]
    total = 0
    for classroom in classrooms:
        lines.append(f"## {classroom.name} (`{classroom.source_file}`)")
        lines.append("")
        lines.append(
            f"- students: {len(classroom.students)}, teachers: {len(classroom.teachers)}"
        )
        if not classroom.issues:
            lines.extend(["- no issues found", ""])
            continue
        lines.append(f"- issues: {len(classroom.issues)}")
        lines.append("")
        for issue in classroom.issues:
            lines.append(f"- **{issue.location}** — {issue.message}")
            total += 1
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    return total


def build(
    data_dir: Path,
    *,
    capacity: int | None = None,
    location: str = "Chưa cập nhật",
    excluded_statuses: list[str] | None = None,
) -> tuple[dict, list[ParsedClassroom]]:
    students_dir = data_dir / "students"
    if not students_dir.is_dir():
        raise FileNotFoundError(f"no students directory at {students_dir}")

    files = sorted(students_dir.glob("*.csv"))
    if not files:
        raise FileNotFoundError(f"no CSV files in {students_dir}")

    classrooms = [
        _filter_students(
            parse_students_file(path, capacity=capacity, location=location),
            excluded_statuses or [],
        )
        for path in files
    ]

    # The teachers directory is for the separate "Huynh Trưởng" sheets, which
    # have their own layout; until one exists, say so instead of ignoring it.
    teachers_dir = data_dir / "teachers"
    unread = sorted(teachers_dir.glob("*.csv")) if teachers_dir.is_dir() else []

    payload = {
        "generated_at": datetime.now(tz=UTC).isoformat(timespec="seconds"),
        "source": {
            "data_dir": str(data_dir),
            "student_files": [path.name for path in files],
            "unread_files": [path.name for path in unread],
        },
        "classrooms": [
            {
                "name": classroom.name,
                "division": classroom.division,
                "capacity": classroom.capacity,
                "location": classroom.location,
                "school_year": classroom.school_year,
                "source_file": classroom.source_file,
                "teachers": classroom.teachers,
                "students": classroom.students,
            }
            for classroom in classrooms
        ],
        "issues": [
            asdict(issue) for classroom in classrooms for issue in classroom.issues
        ],
    }
    return payload, classrooms


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build seed.json from the spreadsheets in data/"
    )
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument(
        "--capacity",
        type=int,
        default=None,
        help="Classroom capacity; defaults to the number of students in the sheet",
    )
    parser.add_argument(
        "--location",
        default="Chưa cập nhật",
        help="Classroom location; the sheets do not record it",
    )
    parser.add_argument(
        "--exclude-status",
        action="append",
        default=[],
        metavar="STATUS",
        help="Drop students whose 'Tình trạng hiện tại' matches, e.g. 'Nghỉ luôn'",
    )
    args = parser.parse_args()

    payload, classrooms = build(
        args.data_dir,
        capacity=args.capacity,
        location=args.location,
        excluded_statuses=args.exclude_status,
    )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default) + "\n",
        encoding="utf-8",
    )
    issue_count = _write_report(args.report, classrooms, args.data_dir)

    print(f"Wrote {args.out}")
    for classroom in classrooms:
        print(
            f"  {classroom.name}: {len(classroom.students)} students, "
            f"{len(classroom.teachers)} teachers, {len(classroom.issues)} issues"
        )
    for name in payload["source"]["unread_files"]:
        print(f"  skipped (unknown layout): data/teachers/{name}")
    print(f"Wrote {args.report} ({issue_count} issues to review)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
