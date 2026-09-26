# Seeding from the parish spreadsheets

The real records live in exported Google Sheets under `data/`:

```
data/
  students/[25-26] SYLL - PĐ NGHĨA SĨ - Lớp Nghĩa Sĩ 1A.csv   one file per classroom
  teachers/                                                    (not read yet, see below)
  seed/seed.json    generated: what gets written to the database
  seed/report.md    generated: every value the tool could not vouch for
```

`data/` is git-ignored: it holds children's names, birth dates and parents'
phone numbers, and none of that belongs in the repository.

## The two steps

```bash
make be-seed-build          # data/*.csv  ->  data/seed/seed.json + report.md
make be-seed-load args=--dry-run   # show what would change in the database
make be-seed-load           # apply it
```

The steps are separate on purpose. Building touches no database, so it is safe
to re-run while fixing the sheets; and the JSON in between is meant to be read
by a human before anything reaches production.

The normal loop is: build → read `data/seed/report.md` → fix the spreadsheet →
build again → dry-run → load.

### Useful flags

`make be-seed-build args="..."`

| Flag | Why |
| --- | --- |
| `--exclude-status "Nghỉ luôn"` | Skip students the sheet marks as no longer attending. Everyone is kept by default. |
| `--capacity 45` | Classroom capacity. Defaults to the number of students in the sheet, because the sheets do not record a capacity. |
| `--location "A1.1"` | Classroom location, which the sheets also do not record. Defaults to `Chưa cập nhật`. |
| `--data-dir`, `--out`, `--report` | Point at somewhere other than `data/`. |

`make be-seed-load args="..."`

| Flag | Why |
| --- | --- |
| `--dry-run` | Report the changes and roll back. Always worth running first. |
| `--no-update` | Only insert new records; leave existing rows untouched. |
| `--file <path>` | Load a JSON other than `data/seed/seed.json`. |
| `--verbose` | Echo the SQL. |

## What the build step adds

The sheets are a register, not a database export, so the tool fills in what the
`Classroom`, `Teacher` and `Student` tables need:

- **division** — from the file name (`PĐ NGHĨA SĨ`), spelled the way the app
  spells it (`Nghĩa Sĩ`, see `frontend/src/lib/divisions.ts`).
- **classroom** — name and division from the file name, so `Lớp Nghĩa Sĩ 1A`
  becomes the classroom `Nghĩa Sĩ 1A`; students are linked to it.
- **teachers** — read from the `Huynh Trưởng phụ trách` block at the top of each
  sheet, split into saint name + name, and linked to the classroom.
- **capacity / location** — not in the sheets; see the flags above.
- **status and note** — `TÌNH TRẠNG HIỆN TẠI` and `GHI CHÚ` have no column on
  the `Student` table, so they are carried in the JSON under `metadata` (and
  used by `--exclude-status`) rather than dropped. If the app ever needs to show
  who is still attending, that is the field to promote to a real column.

## What the build step corrects

Only what is unambiguous. Anything else is reported in `report.md` instead of
guessed at.

| Sheet | Seed |
| --- | --- |
| `NGUYỄN TRẦN BẢO` | `Nguyễn Trần Bảo` |
| `TÊRÊSA`, `Teresa`, `PHERO` | `Têrêsa`, `Têrêsa`, `Phêrô` |
| `Teresa Trần Thị Minh Thuỳ` (a parent) | `Têrêsa Trần Thị Minh Thuỳ` |
| `TP.HCM`, `TPHCM`, `TP HCM` | `TP. Hồ Chí Minh` |
| `Gx Tân Đức`, `GX Tân Đức`, `TÂN ĐỨC` | `Tân Đức` |
| `0919.354.439`, `+84919354439` | `0919354439` |
| `24/07/2010`, `21/6/2026` | `2010-07-24`, `2026-06-21` |
| `không`, `Không có`, `CHƯA`, `-`, `x` | `null` |

Casing that carries meaning is left alone: `GB.`, `ĐXH`, `II` and anything
already written in mixed case.

Saint names are canonicalised through an explicit list in
`backend/scripts/seed/normalizers.py` (`SAINT_NAME_ALIASES`, `KNOWN_SAINT_NAMES`).
A name that is in neither is kept as typed and reported, so a real spelling
mistake gets a human's attention instead of a silent rewrite. Add a line to
those tables rather than widening the rules.

## What the report flags

Data-quality problems the tool will not fix for you, each pointing at the row's
`STT` so it can be found in the spreadsheet:

- missing date of birth, home address, parent name or parent phone number
- a sacrament with a date but no place, or a place but no date
- a date that is unreadable, in the future, or before the date of birth
- a saint name that is not in the known list
- two rows with the same name and date of birth
- a column in the sheet that the tool does not know (never silently ignored)
- phone numbers that are not 10 digits (kept, not dropped)

## Re-running is safe

`load_seed` matches on natural keys — classroom name, teacher name + division,
student family name + given name + date of birth — not on ids. So fixing a
spreadsheet and re-running updates the existing rows instead of creating
duplicates, and re-running with no changes reports everything as `unchanged`.
That last line is the check that the import is really idempotent:

```
    1  classroom unchanged
    3  link unchanged
   41  student unchanged
    3  teacher unchanged
```

By default the spreadsheet wins over what is in the database, since the parish
register is the source of truth. Use `--no-update` when edits made in the app
should be preserved.

## Before running this against production

1. `make be-migrate` — the tables must exist.
2. Back up the database. The loader never deletes, but it does update.
3. `make be-seed-build` and read `data/seed/report.md` end to end.
4. `make be-seed-load args=--dry-run` and read the change list.
5. `make be-seed-load`, then create the login accounts with `make be-seed-user`
   (teacher accounts link to a teacher row: `role=teacher teacher_id=<id>`).

## Not handled yet

- `data/teachers/` — the separate `Huynh Trưởng` sheets have their own layout.
  Files placed there are listed as `skipped (unknown layout)` rather than
  half-parsed; teacher records currently come from the block at the top of each
  student sheet, which carries only the name and phone number.
- A student who moves between classrooms is matched within a classroom, so the
  same child in two sheets is seeded as two rows. Worth revisiting if classes
  get reshuffled mid-year.
- Addresses are cleaned up but not expanded: `PLA`, `PLB`, `ĐXH` and similar
  local abbreviations are kept as the volunteers typed them.
