# -*- coding: utf-8 -*-
"""
BHASA SETU — INSPECT ORIGINAL ISL DICTIONARY

Searches isl_dictionary.xml for the 6 missing concepts.
"""

import os
import re
import xml.etree.ElementTree as ET


# ============================================================
# PATH
# ============================================================

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

XML_PATH = os.path.join(PROJECT_ROOT, "data", "isl_dictionary.xml")


# ============================================================
# MISSING PHRASES
# ============================================================

TARGETS = {
    "P006": {
        "key": "shivering",
        "phrase": "I am shivering",
        "terms": ["shivering", "shiver", "trembling", "tremble", "shake", "shaking"]
    },

    "P035": {
        "key": "getting_worse",
        "phrase": "It is getting worse",
        "terms": ["worse", "worst", "worsening", "bad"]
    },

    "P037": {
        "key": "started_suddenly",
        "phrase": "It started suddenly",
        "terms": ["suddenly", "sudden"]
    },

    "P038": {
        "key": "started_slowly",
        "phrase": "It started slowly",
        "terms": ["slowly", "slow", "gradually", "gradual"]
    },

    "P049": {
        "key": "pregnant",
        "phrase": "I am pregnant",
        "terms": ["pregnant", "pregnancy"]
    },

    "P058": {
        "key": "fainted",
        "phrase": "I fainted",
        "terms": ["fainted", "faint", "fainting", "unconscious", "collapse", "collapsed"]
    }
}


# ============================================================
# CHECK FILE
# ============================================================

print("=" * 80)
print("BHASA SETU — ORIGINAL ISL DICTIONARY INSPECTION")
print("=" * 80)

if not os.path.exists(XML_PATH):
    print("\nERROR: XML file not found!")
    print(XML_PATH)
    raise SystemExit

print("\nDictionary:")
print(XML_PATH)

print("\nReading XML...")


# ============================================================
# READ XML AS TEXT
# ============================================================

with open(XML_PATH, "r", encoding="utf-8", errors="ignore") as f:
    xml_text = f.read()


# ============================================================
# SEARCH
# ============================================================

print("\n" + "=" * 80)
print("SEARCH RESULTS")
print("=" * 80)


for phrase_id, info in TARGETS.items():

    print("\n")
    print("=" * 80)
    print(f"{phrase_id} | {info['key']}")
    print(f"Phrase: {info['phrase']}")
    print("=" * 80)

    found_any = False

    for term in info["terms"]:

        pattern = re.compile(re.escape(term), re.IGNORECASE)

        matches = list(pattern.finditer(xml_text))

        if not matches:
            continue

        found_any = True

        print(f"\nTERM: {term}")
        print(f"Matches found: {len(matches)}")

        # Show maximum 5 useful contexts
        for i, match in enumerate(matches[:5], start=1):

            start = max(0, match.start() - 250)
            end = min(len(xml_text), match.end() + 350)

            context = xml_text[start:end]

            # Clean excessive whitespace
            context = re.sub(r"\s+", " ", context)

            print(f"\n--- Match {i} ---")
            print(context)

    if not found_any:
        print("\n🔴 NO TEXT MATCH FOUND IN XML")


# ============================================================
# COMPLETE
# ============================================================

print("\n")
print("=" * 80)
print("INSPECTION COMPLETE")
print("=" * 80)
print("\nIMPORTANT:")
print("This script ONLY reads the XML.")
print("It does NOT modify isl_mapping_clean.csv.")
print("It does NOT download any videos.")
print("=" * 80)