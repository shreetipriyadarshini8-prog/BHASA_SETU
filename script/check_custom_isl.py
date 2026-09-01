# -*- coding: utf-8 -*-
"""
BHASA SETU — CHECK CUSTOM ISL VIDEOS
"""

import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CUSTOM_FOLDER = os.path.join(PROJECT_ROOT, "videos", "custom_isl")

REQUIRED_FILES = [
    "shivering.mp4",
    "getting_worse.mp4",
    "started_suddenly.mp4",
    "started_slowly.mp4",
    "pregnant.mp4",
    "fainted.mp4",
]

print("=" * 70)
print("BHASA SETU — CUSTOM ISL VIDEO CHECK")
print("=" * 70)

print("\nFolder:")
print(CUSTOM_FOLDER)

if not os.path.exists(CUSTOM_FOLDER):
    print("\n❌ FOLDER NOT FOUND")
    print("Please create:")
    print(CUSTOM_FOLDER)
    raise SystemExit

print("\nChecking files...\n")

all_found = True

for filename in REQUIRED_FILES:

    path = os.path.join(CUSTOM_FOLDER, filename)

    if os.path.isfile(path):
        size_mb = os.path.getsize(path) / (1024 * 1024)

        print(f"🟢 FOUND  | {filename}")
        print(f"           Size: {size_mb:.2f} MB")

    else:
        print(f"🔴 MISSING | {filename}")
        all_found = False

print("\n" + "=" * 70)

if all_found:
    print("🟢 ALL 6 CUSTOM ISL VIDEOS FOUND")
    print("=" * 70)
    print("\nReady for the mapping step.")
else:
    print("🔴 SOME VIDEOS ARE MISSING")
    print("=" * 70)
    print("\nDo NOT modify the CSV yet.")

print("=" * 70)