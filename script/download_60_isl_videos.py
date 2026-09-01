# -*- coding: utf-8 -*-
"""
BHASA SETU — DOWNLOAD 60 ISL VIDEOS
"""

import os
import pandas as pd
import requests
from urllib.parse import urlparse

# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CSV_PATH = os.path.join(PROJECT_ROOT, "data", "csv", "isl_mapping_final_v3.csv")

OUTPUT_DIR = os.path.join(PROJECT_ROOT, "videos", "training")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================
# LOAD MAPPING
# ============================================================

print("=" * 80)
print("BHASA SETU — DOWNLOAD 60 ISL VIDEOS")
print("=" * 80)

print("\nReading:")
print(CSV_PATH)

df = pd.read_csv(CSV_PATH)

# Remove duplicate phrase keys
df = df.drop_duplicates(subset=["phrase_key"])

print("\nUnique phrases found:", len(df))

# ============================================================
# DOWNLOAD FUNCTION
# ============================================================

def download_google_drive(file_id, output_path):

    url = f"https://drive.google.com/uc?export=download&id={file_id}"

    try:
        response = requests.get(url, stream=True, timeout=60)

        if response.status_code != 200:
            print("ERROR:", response.status_code)
            return False

        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)

        return True

    except Exception as e:
        print("ERROR:", e)
        return False


# ============================================================
# PROCESS VIDEOS
# ============================================================

success = 0
failed = 0
custom = 0

for index, row in df.iterrows():

    phrase_key = str(row["phrase_key"])
    video_name = str(row["video_name"])
    video_id = row.get("video_id")

    print("\n" + "-" * 80)
    print(f"{index + 1}/{len(df)}")
    print("Phrase :", phrase_key)
    print("Video  :", video_name)

    # --------------------------------------------------------
    # CUSTOM VIDEOS
    # --------------------------------------------------------

    if str(row["match_quality"]) == "CUSTOM_ISL_DICTIONARY":

        local_path = row.get("local_path")

        if pd.notna(local_path) and os.path.exists(str(local_path)):

            custom += 1

            print("CUSTOM VIDEO ALREADY EXISTS")
            print(local_path)

        else:
            print("CUSTOM VIDEO NOT FOUND")

        continue

    # --------------------------------------------------------
    # GOOGLE DRIVE VIDEO
    # --------------------------------------------------------

    if pd.isna(video_id) or not str(video_id).strip():

        print("NO GOOGLE DRIVE ID")
        failed += 1
        continue

    # Create phrase folder
    phrase_dir = os.path.join(OUTPUT_DIR, phrase_key)
    os.makedirs(phrase_dir, exist_ok=True)

    output_path = os.path.join(
        phrase_dir,
        video_name
    )

    # Skip if already downloaded
    if os.path.exists(output_path):

        print("ALREADY DOWNLOADED")
        success += 1
        continue

    print("Downloading...")

    if download_google_drive(str(video_id), output_path):

        print("DOWNLOAD SUCCESS")
        print(output_path)

        success += 1

    else:

        print("DOWNLOAD FAILED")
        failed += 1


# ============================================================
# SUMMARY
# ============================================================

print("\n")
print("=" * 80)
print("DOWNLOAD COMPLETE")
print("=" * 80)

print("Mapped phrases :", len(df))
print("Downloaded     :", success)
print("Custom videos  :", custom)
print("Failed         :", failed)

print("\nOutput folder:")
print(OUTPUT_DIR)

print("=" * 80)
