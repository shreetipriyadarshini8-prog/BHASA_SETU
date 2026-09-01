# -*- coding: utf-8 -*-

import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

VIDEO_FOLDER = os.path.join(PROJECT_ROOT, "videos", "isl_dictionary")

TARGETS = {
    "P006": [
        "shiver", "shivering", "tremble", "trembling",
        "shake", "shaking", "chill", "chills", "cold"
    ],

    "P035": [
        "worse", "worsening", "worsen", "worst",
        "bad", "deteriorate", "deteriorating"
    ],

    "P037": [
        "sudden", "suddenly", "abrupt", "abruptly"
    ],

    "P038": [
        "slow", "slowly", "gradual", "gradually",
        "progressive", "progressively"
    ],

    "P049": [
        "pregnant", "pregnancy", "expecting",
        "maternity", "mother"
    ],

    "P058": [
        "faint", "fainted", "fainting",
        "unconscious", "collapse", "collapsed",
        "blackout", "passed_out"
    ]
}

print("=" * 90)
print("BHASA SETU — SEARCH ACTUAL ISL VIDEO FOLDER")
print("=" * 90)

if not os.path.exists(VIDEO_FOLDER):
    print("\nERROR: Folder not found:")
    print(VIDEO_FOLDER)
    raise SystemExit

print("\nFolder:")
print(VIDEO_FOLDER)

videos = []

for root, dirs, files in os.walk(VIDEO_FOLDER):

    for file in files:

        if file.lower().endswith((".mp4", ".avi", ".mov", ".mkv", ".webm")):
            videos.append(file)


print("\nTotal videos found:", len(videos))


for phrase_id, terms in TARGETS.items():

    print("\n")
    print("=" * 90)
    print(phrase_id)
    print("=" * 90)

    matches = []

    for video in videos:

        name = os.path.splitext(video)[0].lower()

        for term in terms:

            if term.lower() in name:
                matches.append(video)
                break

    if not matches:

        print("\n🔴 NO VIDEO FILENAME MATCH")

    else:

        print("\n🟢 POSSIBLE VIDEOS:")

        for video in sorted(set(matches)):
            print("   ", video)


print("\n")
print("=" * 90)
print("SEARCH COMPLETE")
print("=" * 90)