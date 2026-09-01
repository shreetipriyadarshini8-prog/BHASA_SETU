# -*- coding: utf-8 -*-
"""
BHASA SETU — FINAL 60 PHRASE MAPPING CHECK
Checks whether all 60 Bhasa Setu phrases are present
in the final ISL mapping CSV.
"""

import os
import pandas as pd


# =========================================================
# PATHS
# =========================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PHRASES_FILE = os.path.join(
    BASE_DIR,
    "data",
    "patient_phrases.csv"
)

# Use the latest mapping file
MAPPING_FILE = os.path.join(
    BASE_DIR,
    "data",
    "csv",
    "isl_mapping_final_v3.csv"
)


# =========================================================
# HEADER
# =========================================================

print("=" * 75)
print("BHASA SETU — FINAL 60 PHRASE MAPPING CHECK")
print("=" * 75)

print()
print("Patient phrases:")
print(PHRASES_FILE)

print()
print("Final mapping:")
print(MAPPING_FILE)

print()


# =========================================================
# CHECK FILES
# =========================================================

if not os.path.exists(PHRASES_FILE):
    print("ERROR: patient_phrases.csv not found.")
    raise SystemExit

if not os.path.exists(MAPPING_FILE):
    print()
    print("ERROR: Final mapping file not found:")
    print(MAPPING_FILE)
    print()
    print("Check which final CSV was created by your latest script.")
    raise SystemExit


# =========================================================
# LOAD FILES
# =========================================================

phrases = pd.read_csv(PHRASES_FILE)
mapping = pd.read_csv(MAPPING_FILE)

print("Patient phrase rows :", len(phrases))
print("Mapping rows        :", len(mapping))
print()


# =========================================================
# NORMALIZE COLUMN NAMES
# =========================================================

phrases.columns = [
    str(c).strip().lower()
    for c in phrases.columns
]

mapping.columns = [
    str(c).strip().lower()
    for c in mapping.columns
]


# =========================================================
# FIND PHRASE KEY COLUMN
# =========================================================

if "phrase_key" not in phrases.columns:
    print("ERROR: 'phrase_key' column not found in patient_phrases.csv")
    print("Columns found:", list(phrases.columns))
    raise SystemExit

if "phrase_key" not in mapping.columns:
    print("ERROR: 'phrase_key' column not found in mapping CSV")
    print("Columns found:", list(mapping.columns))
    raise SystemExit


# =========================================================
# NORMALIZE KEYS
# =========================================================

phrases["phrase_key"] = (
    phrases["phrase_key"]
    .astype(str)
    .str.strip()
    .str.lower()
)

mapping["phrase_key"] = (
    mapping["phrase_key"]
    .astype(str)
    .str.strip()
    .str.lower()
)


# =========================================================
# GET UNIQUE PHRASES
# =========================================================

expected = sorted(
    phrases["phrase_key"].dropna().unique()
)

mapped = sorted(
    mapping["phrase_key"].dropna().unique()
)


# =========================================================
# FIND MISSING
# =========================================================

missing = [
    key for key in expected
    if key not in mapped
]


# =========================================================
# FIND EXTRA
# =========================================================

extra = [
    key for key in mapped
    if key not in expected
]


# =========================================================
# PRINT SUMMARY
# =========================================================

print("=" * 75)
print("FINAL MAPPING SUMMARY")
print("=" * 75)

print()
print("Expected unique phrases :", len(expected))
print("Mapped unique phrases   :", len(mapped))
print("Missing phrases         :", len(missing))
print("Extra phrases           :", len(extra))

print()


# =========================================================
# MISSING
# =========================================================

if missing:

    print("=" * 75)
    print("🔴 MISSING PHRASES")
    print("=" * 75)

    for key in missing:
        print("-", key)

    print()

else:

    print("=" * 75)
    print("🟢 ALL 60 PHRASES ARE PRESENT")
    print("=" * 75)
    print()


# =========================================================
# EXTRA
# =========================================================

if extra:

    print("=" * 75)
    print("ℹ️ EXTRA MAPPING KEYS")
    print("=" * 75)

    for key in extra:
        print("-", key)

    print()


# =========================================================
# CHECK EACH PHRASE
# =========================================================

print("=" * 75)
print("PHRASE-BY-PHRASE CHECK")
print("=" * 75)

print()

for key in expected:

    rows = mapping[
        mapping["phrase_key"] == key
    ]

    if len(rows) == 0:

        print("🔴", key, "| MISSING")

    else:

        # Get unique video names if available
        if "video_name" in rows.columns:

            videos = (
                rows["video_name"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )

            print(
                "🟢",
                key,
                "|",
                len(rows),
                "mapping row(s)",
                "|",
                ", ".join(videos)
            )

        else:

            print(
                "🟢",
                key,
                "|",
                len(rows),
                "mapping row(s)"
            )


# =========================================================
# FINAL RESULT
# =========================================================

print()
print("=" * 75)

if len(missing) == 0:

    print("🎉 FINAL RESULT: 60/60 PHRASES ARE MAPPED")
    print()
    print("The Bhasa Setu ISL mapping is ready.")
    print()
    print("NEXT STEP:")
    print("Download and organize the 60 ISL videos.")

else:

    print(
        "⚠️ FINAL RESULT:",
        len(expected) - len(missing),
        "/",
        len(expected),
        "phrases mapped"
    )

    print()
    print("Missing phrases still need to be handled.")

print("=" * 75)
