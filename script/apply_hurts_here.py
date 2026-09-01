# -*- coding: utf-8 -*-

import os
import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INPUT_CSV = os.path.join(PROJECT_ROOT, "data", "csv", "isl_mapping_final.csv")
OUTPUT_CSV = os.path.join(PROJECT_ROOT, "data", "csv", "isl_mapping_final_v2.csv")

VIDEO_ID = "1yOEQyIiFQ0DoKTt1GGhqlSVcrwKnzpmt"
VIDEO_NAME = "Hurt.mp4"
VIDEO_URL = (
    "https://drive.google.com/file/d/"
    + VIDEO_ID
    + "/view"
)

print("=" * 70)
print("BHASA SETU — APPLY HURTS HERE CANDIDATE")
print("=" * 70)

df = pd.read_csv(INPUT_CSV, dtype=str).fillna("")

print("\nOriginal rows:", len(df))

# Remove existing P026 rows
mask = df["phrase_key"] == "hurts_here"

print("Existing P026 rows:", mask.sum())

df = df[~mask].copy()

# Add Hurt.mp4
new_row = {
    "phrase_key": "hurts_here",
    "patient_phrase": "It hurts here",
    "search_term": "hurt",
    "match_quality": "EXACT_VIDEO_NAME",
    "video_name": VIDEO_NAME,
    "video_id": VIDEO_ID,
    "mime_type": "video/mp4",
    "drive_url": VIDEO_URL
}

df = pd.concat(
    [df, pd.DataFrame([new_row])],
    ignore_index=True
)

df.to_csv(
    OUTPUT_CSV,
    index=False,
    encoding="utf-8-sig"
)

print("\nP026 row:")
print(
    df[df["phrase_key"] == "hurts_here"].to_string(index=False)
)

print("\nFinal rows:", len(df))

print("\nSaved to:")
print(OUTPUT_CSV)

print("\n" + "=" * 70)
print("DONE")
print("=" * 70)