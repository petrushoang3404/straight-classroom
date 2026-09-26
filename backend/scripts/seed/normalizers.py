"""Text/date normalisation for the parish spreadsheets.

The CSVs are typed by hand by several people over several years, so the same
thing shows up spelled a few different ways: `TP.HCM` / `TPHCM` / `TP HCM`,
`Tân Đức` / `GX Tân Đức`, `0919.354.439` / `0919354439`, `không` for "no phone".
Everything in this module is pure (no CSV, no database) so it can be unit
tested and reviewed on its own.

Rule of thumb used throughout: rewrite only what is unambiguous, and *report*
anything that looks off instead of guessing (see `KNOWN_SAINT_NAMES`).
"""

import re
import unicodedata
from datetime import date, datetime

# Cells the volunteers use to mean "nothing here yet". Compared without
# accents/case, so `CHƯA` and `chua` both land here.
BLANK_TOKENS = frozenset(
    {
        "",
        "-",
        "--",
        ".",
        "x",
        "na",
        "n a",  # `N/A`; compare_key turns the slash into a space
        "khong",
        "khong co",
        "khong ro",
        "chua",
        "chua co",
        "chua biet",
        "chua xac dinh",
        "trong",
    }
)

# The five ngành, spelled exactly as the app spells them, see
# frontend/src/lib/divisions.ts.
DIVISIONS = ("Chiên Con", "Ấu Nhi", "Thiếu Nhi", "Nghĩa Sĩ", "Hiệp Sĩ")
_DIVISION_BY_KEY = {}
for _division in DIVISIONS:
    _DIVISION_BY_KEY[
        unicodedata.normalize("NFD", _division.lower())
        .encode("ascii", "ignore")
        .decode()
    ] = _division

# Places of birth. Only collapses spellings of the same place.
PLACE_ALIASES = {
    "tp hcm": "TP. Hồ Chí Minh",
    "tphcm": "TP. Hồ Chí Minh",
    "hcm": "TP. Hồ Chí Minh",
    "tp ho chi minh": "TP. Hồ Chí Minh",
    "thanh pho ho chi minh": "TP. Hồ Chí Minh",
    "sai gon": "TP. Hồ Chí Minh",
    "tp thu duc": "TP. Thủ Đức",
    "ba ria": "Bà Rịa",
    "ha noi": "Hà Nội",
}

# Written in front of a parish name; the parish itself is what we keep.
PARISH_PREFIXES = ("giao xu", "gx", "gh", "nha tho")

# Saint names the sheets spell in more than one way. Kept explicit so it is
# obvious what the tool rewrites; add a line rather than widening the rules.
SAINT_NAME_ALIASES = {
    "phero": "Phêrô",
    "pherô": "Phêrô",
    "phe ro": "Phêrô",
    "teresa": "Têrêsa",
    "terexa": "Têrêsa",
    "teresa maria": "Têrêsa Maria",
    "daminh": "Đaminh",
    "dominico": "Đaminh",
    "gioan kim": "Gioakim",
    "gioan baotixita": "Gioan Baotixita",
    "gb": "Gioan Baotixita",
    "augustino": "Augustinô",
    "martin": "Martinô",
    "martino": "Martinô",
    "andre": "Anrê",
    "anre": "Anrê",
    "tadeo": "Tađêô",
    "phaolo": "Phaolô",
    "anphongso": "Anphongsô",
    "phanxico": "Phanxicô",
    "vincente": "Vinh Sơn",
    "vinh son": "Vinh Sơn",
    "magarita": "Margarita",
    "isave": "Isave",
    "matta": "Matta",
    "rosa": "Rôsa",
    "emmanuel": "Emmanuel",
}

# Used to validate saint names and to split "<saint name> <full name>" strings
# (the teacher rows give both in one cell). Longest match wins, so multi-word
# entries must be listed here too.
KNOWN_SAINT_NAMES = frozenset(
    {
        "Anna",
        "Anphongsô",
        "Anrê",
        "Antôn",
        "Augustinô",
        "Bênêđictô",
        "Cêcilia",
        "Carôlô",
        "Clara",
        "Đaminh",
        "Emmanuel",
        "Gioakim",
        "Gioan",
        "Gioan Baotixita",
        "Gioan Phaolô II",
        "Giuse",
        "Isave",
        "Lucia",
        "Luca",
        "Margarita",
        "Maria",
        "Maria Madalena",
        "Maria Têrêsa",
        "Marcô",
        "Martinô",
        "Matta",
        "Mátthêu",
        "Micae",
        "Monica",
        "Phanxicô",
        "Phaolô",
        "Phêrô",
        "Rôsa",
        "Tađêô",
        "Têrêsa",
        "Têrêsa Maria",
        "Tôma",
        "Vinh Sơn",
        "Vinh Sơn Liêm",
        "Giacôbê",
    }
)

_WHITESPACE = re.compile(r"\s+")
_ROMAN = re.compile(r"^[IVX]{2,}$")
_VOWELS = frozenset("aeiouy")


def strip_accents(value: str) -> str:
    """`Nghĩa Sĩ` -> `Nghia Si`. Only for comparing, never for storing."""
    decomposed = unicodedata.normalize("NFD", value.replace("đ", "d").replace("Đ", "D"))
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def compare_key(value: str) -> str:
    """Accent- and punctuation-insensitive lookup key."""
    key = strip_accents(value).lower()
    key = re.sub(r"[.,;:/\\_+*'\"()-]", " ", key)
    return _WHITESPACE.sub(" ", key).strip()


def collapse_spaces(value: str) -> str:
    return _WHITESPACE.sub(" ", value.replace(" ", " ")).strip()


def clean_cell(value: str | None) -> str | None:
    """Trim a raw cell, returning None for the many ways of writing "empty"."""
    if value is None:
        return None
    text = collapse_spaces(value).strip(" ,;.-")
    if not text or compare_key(text) in BLANK_TOKENS:
        return None
    return text


def _keep_as_written(word: str) -> bool:
    """True for words whose casing carries information of its own."""
    if any(ch.isdigit() for ch in word):
        return True
    if not (word.isupper() or word.islower()):
        # Mixed case is assumed to be how the writer wanted it.
        return True
    # Consonant-only abbreviations: GB, TP, ĐXH.
    return word.isupper() and not (_VOWELS & set(strip_accents(word).lower()))


def capitalize_words(value: str) -> str:
    """`NGUYỄN TRẦN BẢO` -> `Nguyễn Trần Bảo`, leaving deliberate case alone.

    Roman numerals (`II`) and consonant-only abbreviations (`GB`, `TP`) stay
    upper case.
    """
    words = []
    for word in value.split(" "):
        if _keep_as_written(word):
            words.append(word)
        elif _ROMAN.match(word.strip(".")):
            words.append(word.upper())
        else:
            words.append("-".join(part.capitalize() for part in word.split("-")))
    return " ".join(words)


def normalize_person_name(value: str | None) -> str | None:
    """Family/given names: fix ALL-CAPS, leave the spelling itself untouched."""
    text = clean_cell(value)
    return capitalize_words(text) if text else None


def normalize_saint_name(value: str | None) -> str | None:
    """Canonicalise a saint name (`TÊRÊSA` -> `Têrêsa`, `PHERO` -> `Phêrô`)."""
    text = clean_cell(value)
    if text is None:
        return None
    key = compare_key(text)
    if key in SAINT_NAME_ALIASES:
        return SAINT_NAME_ALIASES[key]
    titled = capitalize_words(text)
    for known in KNOWN_SAINT_NAMES:
        if compare_key(known) == key:
            return known
    return titled


def is_known_saint_name(value: str) -> bool:
    """True for a canonical saint name or any spelling we know how to fix."""
    key = compare_key(value)
    if key in SAINT_NAME_ALIASES:
        return True
    return any(compare_key(known) == key for known in KNOWN_SAINT_NAMES)


def split_saint_name(value: str | None) -> tuple[str | None, str | None]:
    """`Luca Nguyễn Ngọc Hoà` -> (`Luca`, `Nguyễn Ngọc Hoà`).

    The teacher block writes the saint name and the civil name in one cell.
    Longest known saint name wins, so `Maria Têrêsa Dương ...` splits correctly.
    Returns (None, full name) when no saint name is recognised.
    """
    text = clean_cell(value)
    if text is None:
        return None, None
    words = capitalize_words(text).split(" ")
    for size in range(min(3, len(words) - 1), 0, -1):
        candidate = " ".join(words[:size])
        if is_known_saint_name(candidate):
            return normalize_saint_name(candidate), " ".join(words[size:])
    return None, " ".join(words)


def normalize_full_name(value: str | None) -> str | None:
    """A parent's cell holds "<saint name> <civil name>"; canonicalise both.

    `Teresa Trần Thị Minh Thuỳ` -> `Têrêsa Trần Thị Minh Thuỳ`, so parents and
    students end up spelling the same saint the same way.
    """
    saint_name, name = split_saint_name(value)
    if name is None:
        return None
    if saint_name is None:
        return name
    return f"{saint_name} {name}".strip()


def normalize_place(value: str | None) -> str | None:
    """Collapse spellings of the same place and drop the `Gx` parish prefix."""
    text = clean_cell(value)
    if text is None:
        return None

    key = compare_key(text)
    for prefix in PARISH_PREFIXES:
        if key.startswith(prefix + " "):
            text = text[len(text) - len(text.split(" ", 1)[1]) :]
            key = compare_key(text)
            break

    if key in PLACE_ALIASES:
        return PLACE_ALIASES[key]
    return capitalize_words(text)


def normalize_division(value: str | None) -> str | None:
    """Map `PĐ NGHĨA SĨ` / `NGHIA SI` onto the app's `Nghĩa sĩ`."""
    text = clean_cell(value)
    if text is None:
        return None
    key = compare_key(text)
    for prefix in ("pd ", "phan doan "):
        key = key.removeprefix(prefix)
    return _DIVISION_BY_KEY.get(key, capitalize_words(text))


def normalize_phone_number(value: str | None) -> tuple[str | None, str | None]:
    """Return (phone, problem). Digits only, local `0…` form.

    `0919.354.439` -> `0919354439`, `+84919354439` -> `0919354439`. Anything
    that is not a 10-digit Vietnamese mobile number is still returned (we do
    not want to silently drop a contact) together with a problem description.
    """
    text = clean_cell(value)
    if text is None:
        return None, None

    digits = re.sub(r"\D", "", text)
    if not digits:
        return None, f"phone number has no digits: {text!r}"
    if digits.startswith("840"):
        digits = digits[2:]
    elif digits.startswith("84") and len(digits) == 11:
        digits = "0" + digits[2:]
    if not digits.startswith("0"):
        digits = "0" + digits
    if len(digits) != 10:
        return digits, f"phone number is not 10 digits: {text!r} -> {digits}"
    return digits, None


_DATE_FORMATS = ("%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y", "%Y-%m-%d", "%d/%m/%y")


def parse_date(value: str | None) -> tuple[date | None, str | None]:
    """Return (date, problem). The sheets use day-first (`24/07/2010`)."""
    text = clean_cell(value)
    if text is None:
        return None, None
    compact = text.replace(" ", "")
    for fmt in _DATE_FORMATS:
        try:
            # Calendar dates off a spreadsheet: no time zone to speak of.
            return datetime.strptime(compact, fmt).date(), None  # noqa: DTZ007
        except ValueError:
            continue
    return None, f"unreadable date: {text!r}"


def truncate(value: str | None, limit: int = 255) -> str | None:
    """The database columns are varchar(255); keep the head, not an error."""
    if value is None or len(value) <= limit:
        return value
    return value[: limit - 1].rstrip() + "…"
