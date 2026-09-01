# -*- coding: utf-8 -*-

import pandas as pd
import os

# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INPUT_CSV = os.path.join(PROJECT_ROOT, "data", "csv", "isl_mapping_clean.csv")

OUTPUT_CSV = os.path.join(PROJECT_ROOT, "data", "csv", "isl_mapping_final.csv")


# ============================================================
# VOMITING VIDEO
# ============================================================

VOMITING_ID = "1CsCIKcMrUfvtFQyI62rH4zYWwpcqmcCx"

VOMITING_VIDEO = "Vomiting.mp4"

VOMITING_URL = (
    "https://drive.google.com/file/d/"
    + VOMITING_ID
    + "/view"
)


# ============================================================
# LOAD CSV
# ============================================================

print("=" * 70)
print("BHASA SETU — APPLY VOMITING CANDIDATE")
print("=" * 70)

print("\nLoading:")
print(INPUT_CSV)

df = pd.read_csv(INPUT_CSV, dtype=str).fillna("")

print("\nOriginal rows:", len(df))


# ============================================================
# CHECK P020
# ============================================================

mask = df["phrase_key"] == "vomiting"

if mask.sum() == 0:
    print("\nERROR: P020 / vomiting was not found.")
    raise SystemExit

print("\nExisting P020 rows:", mask.sum())


# ============================================================
# REMOVE OLD P020 ROWS
# ============================================================

df = df[~mask].copy()

print("Removed old P020 rows.")


# ============================================================
# ADD CORRECT VOMITING VIDEO
# ============================================================

new_row = {
    "phrase_key": "vomiting",
    "patient_phrase": "I feel like vomiting",
    "search_term": "vomiting",
    "match_quality": "EXACT_VIDEO_NAME",
    "video_name": VOMITING_VIDEO,
    "video_id": VOMITING_ID,
    "mime_type": "video/mp4",
    "drive_url": VOMITING_URL
}

df = pd.concat(
    [df, pd.DataFrame([new_row])],
    ignore_index=True
)


# ============================================================
# SAVE
# ============================================================

df.to_csv(
    OUTPUT_CSV,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# VERIFY
# ============================================================

print("\n" + "=" * 70)
print("VOMITING CANDIDATE APPLIED")
print("=" * 70)

print("\nP020 row:")

print(
    df[df["phrase_key"] == "vomiting"].to_string(index=False)
)

print("\nFinal rows:", len(df))

print("\nSaved to:")
print(OUTPUT_CSV)

print("\n" + "=" * 70)
print("DONE")
print("=" * 70)