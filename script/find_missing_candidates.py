# -*- coding: utf-8 -*-
"""
BHASA SETU
Find better ISL candidates for phrases that are
missing or have poor keyword matches.

This script ONLY READS the existing CSV.
It does NOT download or modify any videos.
"""

import os
import pandas as pd
import re


# ============================================================
# FILE PATH
# ============================================================

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

mapping_file = os.path.join(PROJECT_ROOT, "data", "csv", "isl_mapping_clean.csv")


# ============================================================
# LOAD EXISTING 885-RESULT MAPPING
# ============================================================

df = pd.read_csv(
    mapping_file,
    encoding="utf-8-sig"
)


# ============================================================
# PHRASES THAT NEED BETTER CANDIDATES
# ============================================================

target_phrases = {
    
    "P006": {
        "phrase_key": "shivering",
        "english": "I am shivering",
        "search_terms": [
            "shiver",
            "shivering",
            "tremble",
            "trembling",
            "cold",
            "shake",
            "shaking"
        ]
    },

    "P020": {
        "phrase_key": "vomiting",
        "english": "I feel like vomiting",
        "search_terms": [
            "vomit",
            "vomiting",
            "vomit",
            "nausea",
            "nauseous",
            "sick"
        ]
    },

    "P024": {
        "phrase_key": "breathing_difficulty",
        "english": "I have difficulty breathing",
        "search_terms": [
            "breathing",
            "breathe",
            "breath",
            "difficulty",
            "breathing difficulty",
            "shortness",
            "short breath"
        ]
    },

    "P026": {
        "phrase_key": "hurts_here",
        "english": "It hurts here",
        "search_terms": [
            "hurt",
            "pain",
            "here",
            "where",
            "pain here"
        ]
    },

    "P033": {
        "phrase_key": "started_two_days_ago",
        "english": "It started two days ago",
        "search_terms": [
            "two",
            "days",
            "day",
            "ago",
            "two days"
        ]
    },

    "P034": {
        "phrase_key": "one_week",
        "english": "I have had this for a week",
        "search_terms": [
            "week",
            "one week",
            "seven days",
            "7 days"
        ]
    },

    "P035": {
        "phrase_key": "getting_worse",
        "english": "It is getting worse",
        "search_terms": [
            "worse",
            "getting worse",
            "bad",
            "increase",
            "increasing"
        ]
    },

    "P037": {
        "phrase_key": "started_suddenly",
        "english": "It started suddenly",
        "search_terms": [
            "sudden",
            "suddenly",
            "sudden onset",
            "quick",
            "quickly"
        ]
    },

    "P038": {
        "phrase_key": "started_slowly",
        "english": "It started slowly",
        "search_terms": [
            "slow",
            "slowly",
            "gradual",
            "gradually"
        ]
    },

    "P049": {
        "phrase_key": "pregnant",
        "english": "I am pregnant",
        "search_terms": [
            "pregnant",
            "pregnancy"
        ]
    },

    "P058": {
        "phrase_key": "fainted",
        "english": "I fainted",
        "search_terms": [
            "faint",
            "fainted",
            "fainting",
            "unconscious",
            "unconsciousness",
            "collapse",
            "collapsed"
        ]
    }
}


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize(text):
    """
    Convert text into simple searchable lowercase words.
    """

    text = str(text).lower()

    text = text.replace(".mp4", " ")

    text = text.replace("_", " ")
    text = text.replace("-", " ")

    text = re.sub(
        r"\(sign\s*\d+\)",
        " ",
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
# CREATE SEARCHABLE TEXT
# ============================================================

df["searchable_video"] = (
    df["video_name"]
    .fillna("")
    .apply(normalize)
)

df["searchable_term"] = (
    df["search_term"]
    .fillna("")
    .apply(normalize)
)

df["searchable_quality"] = (
    df["match_quality"]
    .fillna("")
    .apply(normalize)
)


# ============================================================
# SEARCH FUNCTION
# ============================================================

def find_candidates(search_terms):

    matches = []

    for index, row in df.iterrows():

        video_text = row["searchable_video"]
        term_text = row["searchable_term"]

        combined_text = (
            video_text + " " + term_text
        )

        score = 0

        matched_terms = []

        for term in search_terms:

            term = normalize(term)

            if not term:
                continue

            # Exact word/phrase match
            if term in combined_text:

                matched_terms.append(term)

                # Longer/more specific terms get higher score
                score += len(term.split()) * 10

                # Prefer video-name matches
                if term in video_text:
                    score += 10

        if score > 0:

            matches.append({
                "score": score,
                "phrase_key": row["phrase_key"],
                "search_term": row["search_term"],
                "match_quality": row["match_quality"],
                "video_name": row["video_name"],
                "video_id": row["video_id"],
                "drive_url": row["drive_url"],
                "matched_terms": ", ".join(
                    sorted(set(matched_terms))
                )
            })

    if not matches:
        return pd.DataFrame()

    result = pd.DataFrame(matches)

    result = result.sort_values(
        by=[
            "score",
            "match_quality",
            "video_name"
        ],
        ascending=[
            False,
            True,
            True
        ]
    )

    # Remove duplicate videos
    result = result.drop_duplicates(
        subset=["video_id"]
    )

    return result


# ============================================================
# OUTPUT FILE
# ============================================================

output_file = os.path.join(PROJECT_ROOT, "isl_missing_candidates.csv")


all_results = []


# ============================================================
# SEARCH EACH TARGET PHRASE
# ============================================================

print()
print("=" * 100)
print("BHASA SETU — SEARCHING CANDIDATES FOR 11 PROBLEM PHRASES")
print("=" * 100)


for phrase_id, info in target_phrases.items():

    print()
    print("=" * 100)

    print(
        f"{phrase_id} | "
        f"{info['phrase_key']} | "
        f"{info['english']}"
    )

    print(
        "Search terms:",
        ", ".join(info["search_terms"])
    )

    print("-" * 100)

    candidates = find_candidates(
        info["search_terms"]
    )

    if candidates.empty:

        print("NO CANDIDATES FOUND")

        continue


    # Show top 10
    top = candidates.head(10)

    for _, row in top.iterrows():

        print()
        print(
            f"Score: {row['score']}"
        )

        print(
            f"Video       : {row['video_name']}"
        )

        print(
            f"Search term : {row['search_term']}"
        )

        print(
            f"Quality     : {row['match_quality']}"
        )

        print(
            f"Matched     : {row['matched_terms']}"
        )

        print(
            f"Video ID    : {row['video_id']}"
        )

        print(
            f"URL         : {row['drive_url']}"
        )


    # Save ALL candidates
    for _, row in candidates.iterrows():

        all_results.append({
            "phrase_id": phrase_id,
            "phrase_key": info["phrase_key"],
            "english": info["english"],
            "score": row["score"],
            "search_term": row["search_term"],
            "match_quality": row["match_quality"],
            "video_name": row["video_name"],
            "video_id": row["video_id"],
            "drive_url": row["drive_url"],
            "matched_terms": row["matched_terms"]
        })


# ============================================================
# SAVE ALL CANDIDATES
# ============================================================

if all_results:

    candidate_df = pd.DataFrame(
        all_results
    )

    candidate_df.to_csv(
        output_file,
        index=False,
        encoding="utf-8-sig"
    )

else:

    candidate_df = pd.DataFrame()


# ============================================================
# FINAL SUMMARY
# ============================================================

print()
print()
print("=" * 100)
print("SEARCH COMPLETE")
print("=" * 100)

print(
    f"Target phrases searched : "
    f"{len(target_phrases)}"
)

print(
    f"Candidate rows found    : "
    f"{len(candidate_df)}"
)

print()
print(
    "Candidate file:"
)

print(
    output_file
)

print()
print("=" * 100)
print("IMPORTANT:")
print("No videos were downloaded.")
print("No original CSV was modified.")
print("=" * 100)