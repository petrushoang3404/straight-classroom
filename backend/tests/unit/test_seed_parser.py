"""Parser tests against a miniature copy of a real exported sheet.

The fixture keeps every awkward part of the real files: a title block, a note
box, the teacher block, the student table, and the legend underneath it.
"""

import pytest

from backend.scripts.seed.parser import parse_students_file

SHEET = """SƠ YẾU LÝ LỊCH - NGHĨA SĨ 1A,,,,,,,,,,,,,,,,,,
Năm học 2025 - 2026,,,,,,,,,,,,,,,,,,
"Lưu ý:
- Tuyệt đối không tự thêm hoặc xóa tên Thiếu Nhi có trong DS này.",,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,
,Huynh Trưởng phụ trách,,SĐT,,,,,,,,,,,,,,,
,Luca Nguyễn Ngọc Hoà,,0919.354.439,,,,,,,,,,,,,,,
,Maria Nguyễn Vương Tuệ Mẫn,,0372.152.246,,,,,,,,,,,,,,,
STT,TÊN THÁNH,HỌ,TÊN,TÌNH TRẠNG HIỆN TẠI,GHI CHÚ,NGÀY SINH,NƠI SINH,NGÀY RỬA TỘI,NƠI RỬA TỘI,NGÀY RƯỚC LỄ,NƠI RƯỚC LỄ,NGÀY THÊM SỨC,NƠI THÊM SỨC,TÊN CHA,SĐT CHA,TÊN MẸ,SĐT MẸ,ĐỊA CHỈ NHÀ
1,AUGUSTINO,NGUYỄN TRẦN BẢO,AN,Đủ thông tin,,24/07/2010,TP.HCM,28/08/2010,Tân Đức,14/07/2024,Gx Tân Đức,18/07/2025,TÂN ĐỨC,Gioan Baotixita Nguyễn Minh Vạn,0854095398,Teresa Trần Thị Minh Thuỳ,0383.935.948,8 Đường 21 PLA TP Thủ Đức HCM
2,PHERO,LÊ QUỐC,ANH,Thiếu thông tin,,11/07/2011,TPHCM,,Tân Đức,21/6/2026,Gx Tân Đức,CHƯA,,Giuse Lê Như Vũ,không,Maria Nguyễn Thị Thanh,0902941500,23 ĐLII P. Phước Long TP.HCM
3,CARÔNÔ,NÌM CHÍ,THỊNH,Nghỉ luôn ,PH xác nhận năm nay bạn không tham gia.,07/08/2012,TP.HCM,27/10/2012,Tân Đức,02/07/2023,Tân Đức,18/07/2025,Tân Đức,Phaolo Nìm Giồng Chương,0908946638,Maria Nguyễn Thị Thơm,0776340275,130 đường 5 PB 9 HCM
,,,,,,,,,,,,,,,,,,
,Tình trạng hiện tại,,,,,,,,,,,,,,,,,
,Đủ thông tin ,Đủ thông tin,,,,,,,,,,,,,,,,
"""


@pytest.fixture
def sheet(tmp_path):
    path = tmp_path / "[25-26] SYLL - PĐ NGHĨA SĨ - Lớp Nghĩa Sĩ 1A.csv"
    path.write_text(SHEET, encoding="utf-8")
    return parse_students_file(path)


def test_classroom_identity_comes_from_the_file_name(sheet):
    assert sheet.name == "Nghĩa sĩ 1A"
    assert sheet.division == "Nghĩa sĩ"
    assert sheet.school_year == "2025-2026"


def test_capacity_defaults_to_the_number_of_students(sheet):
    assert sheet.capacity == 3


def test_teacher_block_is_read_and_split(sheet):
    assert sheet.teachers == [
        {
            "name": "Nguyễn Ngọc Hoà",
            "saint_name": "Luca",
            "division": "Nghĩa sĩ",
            "phone_number": "0919354439",
        },
        {
            "name": "Nguyễn Vương Tuệ Mẫn",
            "saint_name": "Maria",
            "division": "Nghĩa sĩ",
            "phone_number": "0372152246",
        },
    ]


def test_legend_rows_under_the_table_are_not_students(sheet):
    assert len(sheet.students) == 3


def test_student_is_normalised(sheet):
    student = sheet.students[0]
    assert student["saint_name"] == "Augustinô"
    assert student["last_name"] == "Nguyễn Trần Bảo"
    assert student["first_name"] == "An"
    assert student["division"] == "Nghĩa sĩ"
    assert student["date_of_birth"].isoformat() == "2010-07-24"
    assert student["place_of_birth"] == "TP. Hồ Chí Minh"
    # `Gx Tân Đức` and `TÂN ĐỨC` are the same parish.
    assert student["place_of_first_communion"] == "Tân Đức"
    assert student["place_of_confirmation"] == "Tân Đức"
    assert student["mother_name"] == "Têrêsa Trần Thị Minh Thuỳ"
    assert student["mother_phone_number"] == "0383935948"


def test_placeholder_cells_become_null(sheet):
    student = sheet.students[1]
    assert student["date_of_baptism"] is None
    assert student["date_of_confirmation"] is None
    assert student["place_of_confirmation"] is None
    assert student["father_phone_number"] is None


def test_sheet_status_is_kept_as_metadata(sheet):
    assert [student["metadata"]["status"] for student in sheet.students] == [
        "Đủ thông tin",
        "Thiếu thông tin",
        "Nghỉ luôn",
    ]
    assert sheet.students[0]["metadata"]["row"] == 1


def test_issues_report_what_a_human_should_check(sheet):
    messages = [issue.message for issue in sheet.issues]
    assert any("place recorded, date missing" in message for message in messages)
    assert any("unrecognised saint name 'Carônô'" in message for message in messages)


def test_excluded_columns_are_reported_not_dropped_silently(tmp_path):
    path = tmp_path / "[25-26] SYLL - PĐ NGHĨA SĨ - Lớp Nghĩa Sĩ 9Z.csv"
    path.write_text(
        "STT,TÊN THÁNH,HỌ,TÊN,CỘT LẠ\n1,MARIA,NGUYỄN,AN,gì đó\n", encoding="utf-8"
    )
    parsed = parse_students_file(path)
    assert parsed.name == "Nghĩa sĩ 9Z"
    assert any("unmapped column" in issue.message for issue in parsed.issues)
    assert len(parsed.students) == 1


def test_row_without_names_is_skipped_with_an_issue(tmp_path):
    path = tmp_path / "[25-26] SYLL - PĐ NGHĨA SĨ - Lớp Nghĩa Sĩ 9Z.csv"
    path.write_text(
        "STT,TÊN THÁNH,HỌ,TÊN\n1,MARIA,NGUYỄN,AN\n2,GIUSE,,\n", encoding="utf-8"
    )
    parsed = parse_students_file(path)
    assert len(parsed.students) == 1
    assert any("no family/given name" in issue.message for issue in parsed.issues)
