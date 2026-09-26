"""Tooling that turns the parish spreadsheets in `data/` into seed data.

Two steps, on purpose:

1. `build_seed` reads the exported CSVs, normalises them and writes a reviewable
   `seed.json` (plus the data-quality warnings it found).
2. `load_seed` writes that JSON into the database, idempotently.

Splitting them keeps the messy part (cleaning real, hand-typed data) out of the
part that touches production, and lets a human read the diff in between.
"""
