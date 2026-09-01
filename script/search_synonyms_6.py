# -*- coding: utf-8 -*-
"""
BHASA SETU — SEARCH SYNONYMS FOR 6 MISSING ISL PHRASES
"""

import os
import re

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

XML_PATH = os.path.join(PROJECT_ROOT, "data", "isl_dictionary.xml")


TARGETS = {
    "P006": {
        "phrase": "I am shivering",
        "terms": [
            "shiver",
            "shivering",
            "tremble",
            "trembling",
            "shake",
            "shaking",
            "chill",
            "chills",
            "cold",
            "tremor"
        ]
    },

    "P035": {
        "phrase": "It is getting worse",
        "terms": [
            "worse",
            "worsen",
            "worsening",
            "worst",
            "bad",
            "badly",
            "deteriorate",
            "deteriorating",
            "increase",
            "increasing"
        ]
    },

    "P037": {
        "phrase": "It started suddenly",
        "terms": [
            "sudden",
            "suddenly",
            "abrupt",
            "abruptly",
            "immediate",
            "immediately",
            "unexpected",
            "unexpectedly"
        ]
    },

    "P038": {
        "phrase": "It started slowly",
        "terms": [
            "slow",
            "slowly",
            "gradual",
            "gradually",
            "gradually",
            "develop",
            "developed",
            "developing",
            "progressive",
            "progressively"
        ]
    },

    "P049": {
        "phrase": "I am pregnant",
        "terms": [
            "pregnant",
            "pregnancy",
            "expecting",
            "mother",
            "baby",
            "child",
            "maternity"
        ]
    },

    "P058": {
        "phrase": "I fainted",
        "terms": [
            "faint",
            "fainted",
            "fainting",
            "unconscious",
            "unconsciousness",
            "collapse",
            "collapsed",
            "blackout",
            "passed out",
            "pass out"
        ]
    }
}


# ============================================================
# CHECK FILE
# ============================================================

print("=" * 90)
print("BHASA SETU — SYNONYM SEARCH FOR 6 MISSING PHRASES")
print("=" * 90)

if not os.path.exists(XML_PATH):
    print("\nERROR: XML file not found:")
    print(XML_PATH)
    raise SystemExit

print("\nReading:")
print(XML_PATH)

with open(XML_PATH, "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()


# ============================================================
# SEARCH
# ============================================================

for phrase_id, info in TARGETS.items():

    print("\n")
    print("=" * 90)
    print(f"{phrase_id} | {info['phrase']}")
    print("=" * 90)

    found = []

    for term in info["terms"]:

        pattern = re.compile(
            r"(?<![A-Za-z])" +
            re.escape(term) +
            r"(?![A-Za-z])",
            re.IGNORECASE
        )

        matches = list(pattern.finditer(text))

        if matches:
            found.append((term, matches))

    if not found:
        print("\n🔴 NO SYNONYM MATCH FOUND")
        continue

    print("\n🟢 POSSIBLE MATCHES FOUND")

    for term, matches in found:

        print("\n" + "-" * 70)
        print("Search term :", term)
        print("Occurrences  :", len(matches))
        print("-" * 70)

        for number, match in enumerate(matches[:3], start=1):

            start = max(0, match.start() - 300)
            end = min(len(text), match.end() + 500)

            context = text[start:end]

            context = re.sub(r"\s+", " ", context)

            print(f"\nMatch {number}:")
            print(context)


# ============================================================
# FINISHED
# ============================================================

print("\n")
print("=" * 90)
print("SEARCH COMPLETE")
print("=" * 90)

print("\nNo files were modified.")
print("No videos were downloaded.")
print("No CSV was changed.")
print("=" * 90)