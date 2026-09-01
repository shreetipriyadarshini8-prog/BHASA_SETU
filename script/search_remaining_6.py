# -*- coding: utf-8 -*-
"""
BHASA SETU — SEARCH REMAINING 6 MISSING PHRASES
"""

import os
import re
import pandas as pd

# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INPUT_CSV = os.path.join(
    BASE_DIR,
    "data",
    "csv",
    "isl_mapping_clean.csv"
)

OUTPUT_CSV = os.path.join(
    BASE_DIR,
    "isl_remaining_6_candidates.csv"
)

# ============================================================
# REMAINING PHRASES
# ============================================================

TARGETS = {
    "P006": {
        "phrase_key": "shivering",
        "phrase": "I am shivering",
        "terms": [
            "shivering",
            "shiver",
            "trembling",
            "tremble",
            "tremor",
            "shake",
            "shaking"
        ]
    },

    "P035": {
        "phrase_key": "getting_worse",
        "phrase": "It is getting worse",
        "terms": [
            "getting worse",
            "worse",
            "worst",
            "bad",
            "badly",
            "increase",
            "increasing"
        ]
    },

    "P037": {
        "phrase_key": "started_suddenly",
        "phrase": "It started suddenly",
        "terms": [
            "suddenly",
            "sudden",
            "sudden onset",
            "abrupt",
            "abruptly"
        ]
    },

    "P038": {
        "phrase_key": "started_slowly",
        "phrase": "It started slowly",
        "terms": [
            "slowly",
            "slow",
            "gradually",
            "gradual",
            "gradual onset"
        ]
    },

    "P049": {
        "phrase_key": "pregnant",
        "phrase": "I am pregnant",
        "terms": [
            "pregnant",
            "pregnancy",
            "expecting",
            "expect baby"
        ]
    },

    "P058": {
        "phrase_key": "fainted",
        "phrase": "I fainted",
        "terms": [
            "fainted",
            "faint",
            "fainting",
            "unconscious",
            "collapse",
            "collapsed",
            "blackout"
        ]
    }
}

# ============================================================
# NORMALIZE TEXT
# ============================================================

def normalize(text):
    text = str(text).lower()
    text = text.replace("_", " ")
    text = text.replace("-", " ")
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ============================================================
# SCORE VIDEO
# ============================================================

def score_video(video_name, search_term):
    name = normalize(video_name)
    term = normalize(search_term)

    score = 0
    quality = "NO_MATCH"
    matched = []

    # Exact filename
    if name == term:
        score += 100
        quality = "EXACT_VIDEO_NAME"
        matched.append(term)

    # Filename starts with exact term
    elif name.startswith(term + " "):
        score += 80
        quality = "EXACT_TERM_VARIANT"
        matched.append(term)

    # Term appears as a complete word
    elif re.search(r"\b" + re.escape(term) + r"\b", name):
        score += 50
        quality = "TERM_WORD_MATCH"
        matched.append(term)

    # Term is contained inside another word
    elif term in name:
        score += 20
        quality = "CONTAINS_TERM"
        matched.append(term)

    # Special word relationships
    variants = {
        "shivering": ["shiver", "trembling", "tremble", "tremor", "shake", "shaking"],
        "shiver": ["shivering"],
        "worse": ["worst", "bad"],
        "getting worse": ["worse", "worst"],
        "suddenly": ["sudden"],
        "sudden": ["suddenly"],
        "slowly": ["slow", "gradually", "gradual"],
        "slow": ["slowly"],
        "gradually": ["gradual"],
        "pregnant": ["pregnancy", "expecting"],
        "pregnancy": ["pregnant"],
        "fainted": ["faint", "fainting", "unconscious", "collapse", "collapsed"],
        "faint": ["fainted", "fainting"],
        "fainting": ["faint"],
        "unconscious": ["fainted", "collapse"],
    }

    for variant in variants.get(term, []):
        if re.search(r"\b" + re.escape(variant) + r"\b", name):
            score += 40
            matched.append(variant)

    return score, quality, matched


# ============================================================
# LOAD CSV
# ============================================================

print("=" * 100)
print("BHASA SETU — SEARCH REMAINING 6 MISSING PHRASES")
print("=" * 100)

if not os.path.exists(INPUT_CSV):
    raise FileNotFoundError(
        f"\nCSV NOT FOUND:\n{INPUT_CSV}\n\n"
        f"Check that isl_mapping_clean.csv is inside {os.path.join(BASE_DIR, 'data', 'csv')}"
    )

df = pd.read_csv(INPUT_CSV, dtype=str).fillna("")

print(f"\nOriginal rows loaded: {len(df)}")

# ============================================================
# SEARCH
# ============================================================

results = []

for phrase_id, target in TARGETS.items():

    print("\n")
    print("=" * 100)
    print(f"{phrase_id} | {target['phrase_key']}")
    print(f"Phrase: {target['phrase']}")
    print("=" * 100)

    phrase_results = {}

    for term in target["terms"]:

        for _, row in df.iterrows():

            video_name = row["video_name"]

            score, quality, matched = score_video(
                video_name,
                term
            )

            if score <= 0:
                continue

            video_id = row["video_id"]

            # Keep best score for same video
            if video_id not in phrase_results:

                phrase_results[video_id] = {
                    "phrase_id": phrase_id,
                    "phrase_key": target["phrase_key"],
                    "patient_phrase": target["phrase"],
                    "search_term": term,
                    "video_name": video_name,
                    "video_id": video_id,
                    "mime_type": row["mime_type"],
                    "drive_url": row["drive_url"],
                    "score": score,
                    "match_quality": quality,
                    "matched": ", ".join(matched)
                }

            else:

                existing = phrase_results[video_id]

                if score > existing["score"]:
                    existing["score"] = score
                    existing["search_term"] = term
                    existing["match_quality"] = quality
                    existing["matched"] = ", ".join(matched)

    # Sort
    sorted_results = sorted(
        phrase_results.values(),
        key=lambda x: x["score"],
        reverse=True
    )

    if not sorted_results:

        print("\n🔴 NO CANDIDATES FOUND")

    else:

        print(f"\nCandidates found: {len(sorted_results)}")
        print("\nTOP 10 CANDIDATES")
        print("-" * 100)

        for item in sorted_results[:10]:

            print(f"""
Score        : {item['score']}
Video        : {item['video_name']}
Search term  : {item['search_term']}
Quality      : {item['match_quality']}
Matched      : {item['matched']}
Video ID     : {item['video_id']}
URL          : {item['drive_url']}
""")

        results.extend(sorted_results)

# ============================================================
# SAVE
# ============================================================

if results:

    output_df = pd.DataFrame(results)

    output_df = output_df.sort_values(
        ["phrase_id", "score"],
        ascending=[True, False]
    )

    output_df.to_csv(
        OUTPUT_CSV,
        index=False,
        encoding="utf-8-sig"
    )

else:

    output_df = pd.DataFrame()

print("\n")
print("=" * 100)
print("SEARCH COMPLETE")
print("=" * 100)

print(f"Target phrases : {len(TARGETS)}")
print(f"Candidate rows : {len(results)}")

print("\nOutput file:")
print(OUTPUT_CSV)

print("\n")
print("=" * 100)
print("NO VIDEOS WERE DOWNLOADED.")
print("ORIGINAL CSV WAS NOT MODIFIED.")
print("=" * 100)