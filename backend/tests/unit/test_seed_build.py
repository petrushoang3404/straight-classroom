import json

import pytest

from backend.scripts.seed.build_seed import _json_default, build
from backend.tests.unit.test_seed_parser import SHEET


@pytest.fixture
def data_dir(tmp_path):
    students = tmp_path / "students"
    students.mkdir()
    (students / "[25-26] SYLL - PĐ NGHĨA SĨ - Lớp Nghĩa Sĩ 1A.csv").write_text(
        SHEET, encoding="utf-8"
    )
    return tmp_path


def test_build_payload_is_json_serialisable(data_dir):
    payload, _ = build(data_dir)
    dumped = json.dumps(payload, ensure_ascii=False, default=_json_default)
    assert "Nghĩa Sĩ 1A" in dumped
    assert '"date_of_birth": "2010-07-24"' in json.dumps(
        payload, ensure_ascii=False, indent=2, default=_json_default
    )


def test_build_reports_every_source_file(data_dir):
    payload, _ = build(data_dir)
    assert payload["source"]["student_files"] == [
        "[25-26] SYLL - PĐ NGHĨA SĨ - Lớp Nghĩa Sĩ 1A.csv"
    ]
    assert payload["issues"], "the fixture sheet has known problems to report"


def test_exclude_status_drops_students_and_says_so(data_dir):
    payload, classrooms = build(data_dir, excluded_statuses=["Nghỉ luôn"])
    students = payload["classrooms"][0]["students"]
    assert [student["first_name"] for student in students] == ["An", "Anh"]
    assert any(
        "excluded by --exclude-status" in issue.message
        for issue in classrooms[0].issues
    )


def test_capacity_and_location_can_be_overridden(data_dir):
    payload, _ = build(data_dir, capacity=50, location="A1.1")
    classroom = payload["classrooms"][0]
    assert classroom["capacity"] == 50
    assert classroom["location"] == "A1.1"


def test_build_fails_loudly_without_source_files(tmp_path):
    with pytest.raises(FileNotFoundError):
        build(tmp_path)
