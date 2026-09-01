# -*- coding: utf-8 -*-
"""
BHASA SETU — APPLY REMAINING 6 CUSTOM ISL VIDEOS
"""

import os
import pandas as pd

# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INPUT_CSV = os.path.join(PROJECT_ROOT, "data", "csv", "isl_mapping_final_v2.csv")

OUTPUT_CSV = os.path.join(PROJECT_ROOT, "data", "csv", "isl_mapping_final_v3.csv")

VIDEO_FOLDER = os.path.join(PROJECT_ROOT, "videos", "custom_isl")


# ============================================================
# SIX MISSING PHRASES
# ============================================================

CUSTOM_VIDEOS = [
    {
        "phrase_key": "shivering",
        "patient_phrase": "I am shivering",
        "search_term": "shiver",
        "match_quality": "CUSTOM_ISL_DICTIONARY",
        "video_name": "shivering.mp4",
    },
    {
        "phrase_key": "getting_worse",
        "patient_phrase": "It is getting worse",
        "search_term": "bad",
        "match_quality": "CUSTOM_ISL_DICTIONARY",
        "video_name": "getting_worse.mp4",
    },
    {
        "phrase_key": "started_suddenly",
        "patient_phrase": "It started suddenly",
        "search_term": "sudden_unexpected",
        "match_quality": "CUSTOM_ISL_DICTIONARY",
        "video_name": "started_suddenly.mp4",
    },
    {
        "phrase_key": "started_slowly",
        "patient_phrase": "It started slowly",
        "search_term": "slow",
        "match_quality": "CUSTOM_ISL_DICTIONARY",
        "video_name": "started_slowly.mp4",
    },
    {
        "phrase_key": "pregnant",
        "patient_phrase": "I am pregnant",
        "search_term": "pregnancy",
        "match_quality": "CUSTOM_ISL_DICTIONARY",
        "video_name": "pregnant.mp4",
    },
    {
        "phrase_key": "fainted",
        "patient_phrase": "I fainted",
        "search_term": "faint_pass_out_lose",
        "match_quality": "CUSTOM_ISL_DICTIONARY",
        "video_name": "fainted.mp4",
    },
]


# ============================================================
# START
# ============================================================

print("=" * 75)
print("BHASA SETU — APPLY REMAINING 6 CUSTOM ISL VIDEOS")
print("=" * 75)

print("\nLoading:")
print(INPUT_CSV)

if not os.path.exists(INPUT_CSV):
    print("\n❌ INPUT CSV NOT FOUND")
    raise SystemExit

if not os.path.exists(VIDEO_FOLDER):
    print("\n❌ CUSTOM VIDEO FOLDER NOT FOUND")
    raise SystemExit


# ============================================================
# LOAD CSV
# ============================================================

df = pd.read_csv(INPUT_CSV)

print(f"\nOriginal rows: {len(df)}")


# ============================================================
# CHECK ALL 6 VIDEOS
# ============================================================

print("\nChecking custom videos...\n")

missing_files = []

for item in CUSTOM_VIDEOS:

    video_path = os.path.join(
        VIDEO_FOLDER,
        item["video_name"]
    )

    if os.path.isfile(video_path):

        size_mb = os.path.getsize(video_path) / (1024 * 1024)

        print(
            f"🟢 FOUND | "
            f"{item['phrase_key']} | "
            f"{item['video_name']} | "
            f"{size_mb:.2f} MB"
        )

    else:

        print(
            f"🔴 MISSING | "
            f"{item['phrase_key']} | "
            f"{item['video_name']}"
        )

        missing_files.append(item["video_name"])


# ============================================================
# STOP IF ANY VIDEO IS MISSING
# ============================================================

if missing_files:

    print("\n" + "=" * 75)
    print("🔴 STOPPING")
    print("=" * 75)

    print("\nMissing files:")

    for filename in missing_files:
        print(" -", filename)

    print("\nNo CSV was modified.")

    raise SystemExit


# ============================================================
# REMOVE OLD ROWS FOR THESE 6 PHRASES
# ============================================================

phrase_keys = [
    item["phrase_key"]
    for item in CUSTOM_VIDEOS
]

print("\n" + "=" * 75)
print("REMOVING EXISTING ROWS")
print("=" * 75)

before = len(df)

df = df[
    ~df["phrase_key"].astype(str).isin(phrase_keys)
].copy()

removed = before - len(df)

print(f"\nRemoved rows: {removed}")


# ============================================================
# CREATE NEW ROWS
# ============================================================

new_rows = []

print("\n" + "=" * 75)
print("ADDING 6 CUSTOM ISL VIDEOS")
print("=" * 75)

for item in CUSTOM_VIDEOS:

    video_path = os.path.join(
        VIDEO_FOLDER,
        item["video_name"]
    )

    row = {
        "phrase_key": item["phrase_key"],
        "patient_phrase": item["patient_phrase"],
        "search_term": item["search_term"],
        "match_quality": item["match_quality"],
        "video_name": item["video_name"],
        "video_id": "",
        "mime_type": "video/mp4",
        "drive_url": "",
        "local_path": video_path,
    }

    new_rows.append(row)

    print(
        f"🟢 {item['phrase_key']} "
        f"→ {item['video_name']}"
    )


# ============================================================
# APPEND NEW ROWS
# ============================================================

new_df = pd.DataFrame(new_rows)

df = pd.concat(
    [df, new_df],
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
# FINAL REPORT
# ============================================================

print("\n" + "=" * 75)
print("CUSTOM ISL VIDEOS APPLIED")
print("=" * 75)

print("\nAdded phrases:")

for item in CUSTOM_VIDEOS:
    print(
        f"  {item['phrase_key']} "
        f"| {item['patient_phrase']} "
        f"| {item['video_name']}"
    )

print(f"\nFinal rows: {len(df)}")

print("\nSaved to:")
print(OUTPUT_CSV)

print("\n" + "=" * 75)
print("DONE")
print("=" * 75)