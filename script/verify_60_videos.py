import os
import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CSV_PATH = os.path.join(PROJECT_ROOT, "data", "csv", "isl_mapping_final_v3.csv")
TRAINING_DIR = os.path.join(PROJECT_ROOT, "videos", "training")
CUSTOM_DIR = os.path.join(PROJECT_ROOT, "videos", "custom_isl")

df = pd.read_csv(CSV_PATH)

# One row per phrase
df = df.drop_duplicates(subset=["phrase_key"])

found = 0
missing = 0

print("=" * 80)
print("BHASA SETU — VERIFY 60 ISL VIDEOS")
print("=" * 80)

for _, row in df.iterrows():

    phrase = str(row["phrase_key"])
    video = str(row["video_name"])
    quality = str(row["match_quality"])

    if quality == "CUSTOM_ISL_DICTIONARY":
        path = os.path.join(CUSTOM_DIR, video)
    else:
        path = os.path.join(TRAINING_DIR, phrase, video)

    if os.path.exists(path):
        print(f"🟢 {phrase:<25} {video}")
        found += 1
    else:
        print(f"🔴 {phrase:<25} MISSING")
        missing += 1

print("\n" + "=" * 80)
print("FINAL VIDEO CHECK")
print("=" * 80)

print("Expected :", len(df))
print("Found    :", found)
print("Missing  :", missing)

if missing == 0:
    print("\n🎉 ALL 60 ISL VIDEOS ARE READY!")
else:
    print("\n⚠️ Some videos are missing.")

print("=" * 80)