import pandas as pd
import os
import re

# ============================================================
# FILE PATHS
# ============================================================

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

mapping_file = os.path.join(PROJECT_ROOT, "data", "csv", "isl_mapping_final_v3.csv")

verification_file = os.path.join(PROJECT_ROOT, "isl_verification_60.csv")

output_file = os.path.join(PROJECT_ROOT, "isl_verification_60_results.csv")


# ============================================================
# LOAD FILES
# ============================================================

mapping = pd.read_csv(mapping_file, encoding="utf-8-sig")
verification = pd.read_csv(verification_file, encoding="utf-8-sig")


# ============================================================
# MATCH QUALITY PRIORITY
# ============================================================

quality_priority = {
    "EXACT_VIDEO_NAME": 1,
    "EXACT_TERM_VARIANT": 2,
    "TERM_WORD_MATCH": 3
}

mapping["quality_rank"] = (
    mapping["match_quality"]
    .map(quality_priority)
    .fillna(99)
)


# ============================================================
# NORMALIZATION FUNCTION
# ============================================================

def normalize(text):
    text = str(text).lower()
    text = re.sub(r"\.mp4$", "", text)
    text = re.sub(r"\(sign[_ ]?\d+\)", "", text)
    text = re.sub(r"[_\-]+", " ", text)
    text = re.sub(r"[^a-z0-9 ]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


# ============================================================
# CREATE BEST MATCH FOR EACH OF THE 60 PHRASES
# ============================================================

results = []

for _, phrase in verification.iterrows():

    phrase_id = phrase["phrase_id"]
    phrase_key = phrase["phrase_key"]

    candidates = mapping[
        mapping["phrase_key"].astype(str).str.lower()
        == str(phrase_key).lower()
    ].copy()

    # --------------------------------------------------------
    # No result
    # --------------------------------------------------------

    if candidates.empty:

        results.append({
            "phrase_id": phrase_id,
            "phrase_key": phrase_key,
            "english": phrase["english"],
            "hindi": phrase["hindi"],
            "odia": phrase["odia"],
            "best_isl_sign": "",
            "video_name": "",
            "video_id": "",
            "video_url": "",
            "match_quality": "",
            "match_type": "Missing",
            "status": "🔴 Missing",
            "notes": "No ISL dictionary result found"
        })

        continue


    # --------------------------------------------------------
    # Sort by match quality
    # --------------------------------------------------------

    candidates = candidates.sort_values(
        by=["quality_rank", "video_name"]
    )


    best = candidates.iloc[0]

    video_name = str(best["video_name"])
    search_term = str(best["search_term"])


    # --------------------------------------------------------
    # Determine whether this is exact or component
    # --------------------------------------------------------

    normalized_phrase = normalize(phrase_key)
    normalized_video = normalize(video_name)

    # Exact phrase-style filename
    phrase_words = set(normalized_phrase.split())
    video_words = set(normalized_video.split())

    if (
        normalized_video == normalized_phrase
        or normalized_video.replace(" ", "_") == normalized_phrase.replace(" ", "_")
    ):
        match_type = "Exact"
        status = "🟢 Exact"

    elif (
        len(phrase_words) == 1
        and normalized_phrase in normalized_video
    ):
        match_type = "Exact"
        status = "🟢 Exact"

    else:
        match_type = "Component"
        status = "🟡 Component"


    # --------------------------------------------------------
    # Notes
    # --------------------------------------------------------

    notes = (
        f"Selected from {len(candidates)} candidates; "
        f"search term: {search_term}"
    )


    results.append({
        "phrase_id": phrase_id,
        "phrase_key": phrase_key,
        "english": phrase["english"],
        "hindi": phrase["hindi"],
        "odia": phrase["odia"],
        "best_isl_sign": search_term,
        "video_name": video_name,
        "video_id": best["video_id"],
        "video_url": best["drive_url"],
        "match_quality": best["match_quality"],
        "match_type": match_type,
        "status": status,
        "notes": notes
    })


# ============================================================
# SAVE RESULT
# ============================================================

result_df = pd.DataFrame(results)

result_df.to_csv(
    output_file,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# SUMMARY
# ============================================================

print()
print("=" * 65)
print("BHASA SETU — 60 PHRASE ISL VERIFICATION")
print("=" * 65)

print()
print("Total Bhasa Setu phrases :", len(result_df))

print()
print("Status summary:")
print(
    result_df["status"]
    .value_counts()
    .to_string()
)

print()
print("Match quality summary:")
print(
    result_df["match_quality"]
    .replace("", "MISSING")
    .value_counts()
    .to_string()
)

print()
print("Missing phrases:")
missing = result_df[result_df["status"] == "🔴 Missing"]

if missing.empty:
    print("None")
else:
    for _, row in missing.iterrows():
        print(
            f"{row['phrase_id']} | "
            f"{row['phrase_key']} | "
            f"{row['english']}"
        )

print()
print("Output:")
print(output_file)

print()
print("=" * 65)