# -*- coding: utf-8 -*-
"""
BHASA SETU — FIND ISL DICTIONARY SOURCE
"""

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

print("=" * 80)
print("BHASA SETU — SEARCHING FOR ORIGINAL ISL DICTIONARY DATA")
print("=" * 80)

# Folders/files that commonly contain the dictionary
possible_names = [
    "isl",
    "isl_dictionary",
    "isl dictionary",
    "dictionary",
    "google_drive",
    "videos",
    "data",
    "dataset",
    "raw",
    "source",
    "isl_data",
    "isl_videos"
]

found = []

print("\nSearching inside:")
print(BASE_DIR)
print("\nPlease wait...\n")

for root, dirs, files in os.walk(BASE_DIR):

    # Ignore Python cache folders
    dirs[:] = [
        d for d in dirs
        if d not in ["__pycache__", ".git", ".spyproject"]
    ]

    for name in dirs:

        lower = name.lower()

        if any(term in lower for term in possible_names):

            path = os.path.join(root, name)

            if path not in found:
                found.append(path)

    for name in files:

        lower = name.lower()

        # Look for likely dictionary/data files
        if (
            "isl" in lower
            or "dictionary" in lower
            or "mapping" in lower
            or lower.endswith(".csv")
            or lower.endswith(".xlsx")
            or lower.endswith(".json")
            or lower.endswith(".txt")
        ):

            path = os.path.join(root, name)

            if path not in found:
                found.append(path)


print("=" * 80)
print("POSSIBLE ISL DICTIONARY / DATA FILES")
print("=" * 80)

if not found:

    print("\n❌ No likely dictionary source found.")

else:

    for i, path in enumerate(found, 1):

        print(f"\n{i}. {path}")

print("\n")
print("=" * 80)
print("SEARCH COMPLETE")
print("=" * 80)

print(f"\nPossible sources found: {len(found)}")