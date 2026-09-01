# -*- coding: utf-8 -*-
"""
BHASA SETU
Find better ISL candidates for 11 problematic phrases.

IMPORTANT:
- Reads only isl_mapping_clean.csv
- Does NOT download videos
- Does NOT modify the original CSV
- Searches whole words to avoid false matches
"""

import os
import pandas as pd
import re


# ============================================================
# 1. FILE PATH
# ============================================================

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

mapping_file = os.path.join(PROJECT_ROOT, "data", "csv", "isl_mapping_clean.csv")

output_file = os.path.join(PROJECT_ROOT, "isl_missing_candidates_v2.csv")


# ============================================================
# 2. LOAD CSV
# ============================================================

df = pd.read_csv(
    mapping_file,
    encoding="utf-8-sig"
)

print()
print("=" * 100)
print("BHASA SETU — IMPROVED CANDIDATE SEARCH")
print("=" * 100)

print(f"Original rows loaded: {len(df)}")


# ============================================================
# 3. TARGET PHRASES
# ============================================================

targets = {

    "P006": {
        "phrase_key": "shivering",
        "english": "I am shivering",
        "terms": [
            "shivering",
            "shiver",
            "trembling",
            "tremble",
            "shaking",
            "shake"
        ]
    },

    "P020": {
        "phrase_key": "vomiting",
        "english": "I feel like vomiting",
        "terms": [
            "vomiting",
            "vomit",
            "nausea",
            "nauseous"
        ]
    },

    "P024": {
        "phrase_key": "breathing_difficulty",
        "english": "I have difficulty breathing",
        "terms": [
            "breathing",
            "breathe",
            "breath",
            "shortness"
        ]
    },

    "P026": {
        "phrase_key": "hurts_here",
        "english": "It hurts here",
        "terms": [
            "hurt",
            "pain",
            "here"
        ]
    },

    "P033": {
        "phrase_key": "started_two_days_ago",
        "english": "It started two days ago",
        "terms": [
            "two days",
            "two_day",
            "two days ago",
            "two days before"
        ]
    },

    "P034": {
        "phrase_key": "one_week",
        "english": "I have had this for a week",
        "terms": [
            "one week",
            "week"
        ]
    },

    "P035": {
        "phrase_key": "getting_worse",
        "english": "It is getting worse",
        "terms": [
            "getting worse",
            "worse",
            "worsening"
        ]
    },

    "P037": {
        "phrase_key": "started_suddenly",
        "english": "It started suddenly",
        "terms": [
            "suddenly",
            "sudden"
        ]
    },

    "P038": {
        "phrase_key": "started_slowly",
        "english": "It started slowly",
        "terms": [
            "slowly",
            "slow",
            "gradually",
            "gradual"
        ]
    },

    "P049": {
        "phrase_key": "pregnant",
        "english": "I am pregnant",
        "terms": [
            "pregnant",
            "pregnancy"
        ]
    },

    "P058": {
        "phrase_key": "fainted",
        "english": "I fainted",
        "terms": [
            "fainted",
            "fainting",
            "faint",
            "unconscious",
            "collapse",
            "collapsed"
        ]
    }
}


# ============================================================
# 4. NORMALIZE TEXT
# ============================================================

def normalize(text):

    text = str(text).lower()

    text = text.replace(".mp4", "")
    text = text.replace("_", " ")
    text = text.replace("-", " ")

    text = re.sub(
        r"\(sign\s*\d+\)",
        "",
        text
    )

    text = re.sub(
        r"[^a-z0-9 ]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# 5. WHOLE WORD SEARCH
# ============================================================

def contains_term(text, term):

    text = normalize(text)
    term = normalize(term)

    if not text or not term:
        return False

    pattern = r"\b" + re.escape(term) + r"\b"

    return bool(
        re.search(pattern, text)
    )


# ============================================================
# 6. SEARCH ONE PHRASE
# ============================================================

def search_candidates(terms):

    results = []

    for _, row in df.iterrows():

        video_name = normalize(
            row["video_name"]
        )

        search_term = normalize(
            row["search_term"]
        )

        combined = (
            video_name + " " + search_term
        )

        score = 0
        matched = []

        for term in terms:

            term = normalize(term)

            if not term:
                continue

            # Exact phrase/name match
            if contains_term(video_name, term):

                matched.append(term)

                # Strong score for exact video-name match
                score += 50

                # Extra points for multi-word phrase
                if len(term.split()) > 1:
                    score += 30

            # Search-term match
            elif contains_term(search_term, term):

                matched.append(term)

                score += 20

        if score == 0:
            continue

        results.append({

            "score": score,

            "search_term": row["search_term"],

            "match_quality": row["match_quality"],

            "video_name": row["video_name"],

            "video_id": row["video_id"],

            "drive_url": row["drive_url"],

            "matched_terms": ", ".join(
                sorted(set(matched))
            )
        })


    if not results:

        return pd.DataFrame()


    result = pd.DataFrame(results)


    # ========================================================
    # REMOVE DUPLICATE VIDEO IDs
    # ========================================================

    result = result.drop_duplicates(
        subset=["video_id"]
    )


    # ========================================================
    # SORT BEST FIRST
    # ========================================================

    result = result.sort_values(
        by=[
            "score",
            "video_name"
        ],
        ascending=[
            False,
            True
        ]
    )


    return result


# ============================================================
# 7. SEARCH ALL 11 PHRASES
# ============================================================

all_results = []


for phrase_id, info in targets.items():

    print()
    print()
    print("=" * 100)

    print(
        f"{phrase_id} | "
        f"{info['phrase_key']}"
    )

    print(
        f"Phrase: {info['english']}"
    )

    print("=" * 100)


    candidates = search_candidates(
        info["terms"]
    )


    if candidates.empty:

        print()
        print("🔴 NO CANDIDATES FOUND")

        continue


    print()
    print(
        f"Candidates found: {len(candidates)}"
    )

    print()
    print("TOP 10 CANDIDATES")
    print("-" * 100)


    for _, row in candidates.head(10).iterrows():

        print()

        print(
            f"Score        : {row['score']}"
        )

        print(
            f"Video        : {row['video_name']}"
        )

        print(
            f"Search term  : {row['search_term']}"
        )

        print(
            f"Quality      : {row['match_quality']}"
        )

        print(
            f"Matched      : {row['matched_terms']}"
        )

        print(
            f"Video ID     : {row['video_id']}"
        )

        print(
            f"URL          : {row['drive_url']}"
        )


    # ========================================================
    # SAVE ALL CANDIDATES
    # ========================================================

    for _, row in candidates.iterrows():

        all_results.append({

            "phrase_id":
                phrase_id,

            "phrase_key":
                info["phrase_key"],

            "english":
                info["english"],

            "score":
                row["score"],

            "search_term":
                row["search_term"],

            "match_quality":
                row["match_quality"],

            "video_name":
                row["video_name"],

            "video_id":
                row["video_id"],

            "drive_url":
                row["drive_url"],

            "matched_terms":
                row["matched_terms"]
        })


# ============================================================
# 8. SAVE RESULTS
# ============================================================

if all_results:

    result_df = pd.DataFrame(
        all_results
    )

    result_df.to_csv(
        output_file,
        index=False,
        encoding="utf-8-sig"
    )

else:

    result_df = pd.DataFrame()


# ============================================================
# 9. FINAL SUMMARY
# ============================================================

print()
print()
print("=" * 100)
print("SEARCH COMPLETE")
print("=" * 100)

print(
    f"Target phrases: {len(targets)}"
)

print(
    f"Candidate rows: {len(result_df)}"
)

print()
print(
    "Output file:"
)

print(
    output_file
)

print()
print("=" * 100)
print("NO VIDEOS WERE DOWNLOADED.")
print("ORIGINAL CSV WAS NOT MODIFIED.")
print("=" * 100)