import pytest

from backend.scripts.seed.normalizers import (
    capitalize_words,
    clean_cell,
    normalize_division,
    normalize_full_name,
    normalize_phone_number,
    normalize_place,
    normalize_saint_name,
    parse_date,
    split_saint_name,
    truncate,
)


@pytest.mark.parametrize(
    "raw",
    ["", "   ", "-", "không", "Không có", "CHƯA", "chưa có", "x", "N/A"],
)
def test_clean_cell_treats_placeholders_as_empty(raw):
    assert clean_cell(raw) is None


def test_clean_cell_collapses_whitespace():
    assert clean_cell("  387 ĐXH   PLB 9 HCM ") == "387 ĐXH PLB 9 HCM"


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("NGUYỄN TRẦN BẢO", "Nguyễn Trần Bảo"),
        ("ĐINH NGỌC HUY", "Đinh Ngọc Huy"),
        ("Trần Đình Kỷ", "Trần Đình Kỷ"),
        ("GIOAN PHAOLÔ II", "Gioan Phaolô II"),
        ("GB. Ngô Khắc Hoàng Nam", "GB. Ngô Khắc Hoàng Nam"),
        ("LÊ QUỐC", "Lê Quốc"),
    ],
)
def test_capitalize_words(raw, expected):
    assert capitalize_words(raw) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("TÊRÊSA", "Têrêsa"),
        ("Teresa", "Têrêsa"),
        ("PHERO", "Phêrô"),
        ("ĐAMINH", "Đaminh"),
        ("MARIA MADALENA", "Maria Madalena"),
        ("GIOAN PHAOLÔ II", "Gioan Phaolô II"),
    ],
)
def test_normalize_saint_name(raw, expected):
    assert normalize_saint_name(raw) == expected


def test_normalize_saint_name_keeps_unknown_spelling():
    # Unknown names are reported by the parser, never silently rewritten.
    assert normalize_saint_name("CARÔNÔ") == "Carônô"


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("Luca Nguyễn Ngọc Hoà", ("Luca", "Nguyễn Ngọc Hoà")),
        ("MARIA TÊRÊSA DƯƠNG TRẦN THIÊN", ("Maria Têrêsa", "Dương Trần Thiên")),
        ("Nguyễn Hữu Đạt", (None, "Nguyễn Hữu Đạt")),
    ],
)
def test_split_saint_name(raw, expected):
    assert split_saint_name(raw) == expected


def test_normalize_full_name_canonicalises_the_saint_part():
    assert (
        normalize_full_name("Teresa Trần Thị Minh Thuỳ") == "Têrêsa Trần Thị Minh Thuỳ"
    )
    assert (
        normalize_full_name("GB. Ngô Khắc Hoàng Nam")
        == "Gioan Baotixita Ngô Khắc Hoàng Nam"
    )
    assert normalize_full_name("Không có") is None


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("TP.HCM", "TP. Hồ Chí Minh"),
        ("TPHCM", "TP. Hồ Chí Minh"),
        ("TP HCM", "TP. Hồ Chí Minh"),
        ("TP Hồ Chí Minh", "TP. Hồ Chí Minh"),
        ("Gx Tân Đức", "Tân Đức"),
        ("GX Tân Đức", "Tân Đức"),
        ("TÂN ĐỨC", "Tân Đức"),
        ("Fatima Bình Triệu", "Fatima Bình Triệu"),
    ],
)
def test_normalize_place(raw, expected):
    assert normalize_place(raw) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("PĐ NGHĨA SĨ", "Nghĩa sĩ"),
        ("Nghĩa Sĩ", "Nghĩa sĩ"),
        ("phan doan au nhi", "Ấu nhi"),
        ("THIẾU NHI", "Thiếu nhi"),
    ],
)
def test_normalize_division_matches_the_app_spelling(raw, expected):
    assert normalize_division(raw) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("0919.354.439", "0919354439"),
        ("0919 354 439", "0919354439"),
        ("+84919354439", "0919354439"),
        ("84919354439", "0919354439"),
        ("919354439", "0919354439"),
    ],
)
def test_normalize_phone_number(raw, expected):
    assert normalize_phone_number(raw) == (expected, None)


def test_normalize_phone_number_reports_but_keeps_odd_numbers():
    value, problem = normalize_phone_number("09123")
    assert value == "09123"
    assert "not 10 digits" in problem


def test_normalize_phone_number_drops_placeholders():
    assert normalize_phone_number("không") == (None, None)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("24/07/2010", "2010-07-24"),
        ("21/6/2026", "2026-06-21"),
        ("2010-07-24", "2010-07-24"),
    ],
)
def test_parse_date(raw, expected):
    value, problem = parse_date(raw)
    assert value.isoformat() == expected
    assert problem is None


def test_parse_date_reports_unreadable_values():
    value, problem = parse_date("tháng 7 năm 2010")
    assert value is None
    assert "unreadable date" in problem


def test_truncate_keeps_columns_within_varchar_255():
    assert truncate("a" * 300).endswith("…")
    assert len(truncate("a" * 300)) == 255
    assert truncate("short") == "short"
