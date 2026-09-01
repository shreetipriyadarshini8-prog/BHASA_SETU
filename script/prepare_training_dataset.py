# -*- coding: utf-8 -*-

"""
BHASA SETU — PREPARE TRAINING DATASET

60 ISL landmark files
        ↓
Normalize sequences
        ↓
Create TRAIN / VALIDATION / TEST
        ↓
Save labels + dataset
"""

import os
import numpy as np
import pandas as pd
import json

# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LANDMARK_DIR = os.path.join(PROJECT_ROOT, "dataset", "landmarks")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "dataset", "prepared")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================
# SETTINGS
# ============================================================

SEQUENCE_LENGTH = 60

# ============================================================
# LOAD LANDMARK FILES
# ============================================================

print("=" * 80)
print("BHASA SETU — PREPARE TRAINING DATASET")
print("=" * 80)

files = sorted([
    f for f in os.listdir(LANDMARK_DIR)
    if f.endswith(".npy")
])

print("\nLandmark files found:", len(files))

if len(files) != 46:
    print("\nWARNING: Expected 46 landmark files.")

# ============================================================
# RESIZE SEQUENCE
# ============================================================

def prepare_sequence(data, target_length=60):

    # data shape:
    # frames × 126

    frames = data.shape[0]

    if frames == target_length:
        return data

    # --------------------------------------------------------
    # If video has MORE frames
    # --------------------------------------------------------

    if frames > target_length:

        indexes = np.linspace(
            0,
            frames - 1,
            target_length
        ).astype(int)

        return data[indexes]

    # --------------------------------------------------------
    # If video has FEWER frames
    # --------------------------------------------------------

    result = np.zeros(
        (target_length, data.shape[1]),
        dtype=np.float32
    )

    result[:frames] = data

    # Repeat final frame
    if frames > 0:
        result[frames:] = data[-1]

    return result


# ============================================================
# CREATE DATASET
# ============================================================

X = []
y = []

labels = []

print("\n")
print("=" * 80)
print("PROCESSING LANDMARKS")
print("=" * 80)

for index, filename in enumerate(files):

    phrase = os.path.splitext(filename)[0]

    path = os.path.join(
        LANDMARK_DIR,
        filename
    )

    data = np.load(path)

    print(
        f"{index + 1:02d}/46  "
        f"{phrase:<30} "
        f"Original frames: {data.shape[0]}"
    )

    # --------------------------------------------------------
    # Check feature count
    # --------------------------------------------------------

    if data.shape[1] != 126:

        print(
            "   🔴 WRONG FEATURE COUNT:",
            data.shape[1]
        )

        continue

    # --------------------------------------------------------
    # Prepare fixed-length sequence
    # --------------------------------------------------------

    sequence = prepare_sequence(
        data,
        SEQUENCE_LENGTH
    )

    X.append(sequence)

    labels.append(phrase)

# ============================================================
# LABEL ENCODING
# ============================================================

unique_labels = sorted(labels)

label_to_id = {
    label: i
    for i, label in enumerate(unique_labels)
}

for label in labels:
    y.append(label_to_id[label])

X = np.array(X, dtype=np.float32)
y = np.array(y, dtype=np.int64)

print("\n")
print("=" * 80)
print("DATASET CREATED")
print("=" * 80)

print("X shape:", X.shape)
print("y shape:", y.shape)

print("Number of classes:", len(unique_labels))

# ============================================================
# TRAIN / VALIDATION / TEST SPLIT
# ============================================================
#
# IMPORTANT:
# We currently have ONE video per phrase.
#
# Therefore we cannot make a reliable random
# train/validation/test split yet.
#
# Instead, save the complete dataset first.
#
# We will create multiple training samples from
# each video in the next stage.
# ============================================================

# Save complete dataset

np.save(
    os.path.join(
        OUTPUT_DIR,
        "X_all.npy"
    ),
    X
)

np.save(
    os.path.join(
        OUTPUT_DIR,
        "y_all.npy"
    ),
    y
)

# ============================================================
# SAVE LABEL MAP
# ============================================================

with open(
    os.path.join(
        OUTPUT_DIR,
        "label_map.json"
    ),
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        label_to_id,
        f,
        ensure_ascii=False,
        indent=4
    )

# ============================================================
# SAVE LABEL LIST
# ============================================================

label_df = pd.DataFrame({
    "label_id": range(len(unique_labels)),
    "phrase_key": unique_labels
})

label_df.to_csv(
    os.path.join(
        OUTPUT_DIR,
        "labels.csv"
    ),
    index=False
)

# ============================================================
# FINAL RESULT
# ============================================================

print("\n")
print("=" * 80)
print("PREPARATION COMPLETE")
print("=" * 80)

print("Classes :", len(unique_labels))
print("Samples :", len(X))
print("Frames  :", SEQUENCE_LENGTH)
print("Features:", X.shape[2])

print("\nSaved files:")

print(
    os.path.join(
        OUTPUT_DIR,
        "X_all.npy"
    )
)

print(
    os.path.join(
        OUTPUT_DIR,
        "y_all.npy"
    )
)

print(
    os.path.join(
        OUTPUT_DIR,
        "label_map.json"
    )
)

print(
    os.path.join(
        OUTPUT_DIR,
        "labels.csv"
    )
)

print("\nDATASET PREPARATION COMPLETE!")

print("=" * 80)
