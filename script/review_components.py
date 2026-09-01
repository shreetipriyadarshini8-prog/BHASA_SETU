import os
import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

file = os.path.join(PROJECT_ROOT, "isl_verification_60_results.csv")

df = pd.read_csv(file, encoding="utf-8-sig")

components = df[df["status"] == "🟡 Component"].copy()

print("=" * 100)
print("BHASA SETU — COMPONENT MATCH REVIEW")
print("=" * 100)

for _, row in components.iterrows():

    print()
    print(f"{row['phrase_id']} | {row['phrase_key']}")
    print(f"Phrase       : {row['english']}")
    print(f"ISL sign     : {row['best_isl_sign']}")
    print(f"Video        : {row['video_name']}")
    print(f"Quality      : {row['match_quality']}")
    print(f"Match type   : {row['match_type']}")
    print(f"Video ID     : {row['video_id']}")
    print(f"URL          : {row['video_url']}")
    print("-" * 100)

print()
print("=" * 100)
print(f"Total component matches: {len(components)}")
print("=" * 100)