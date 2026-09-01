# -*- coding: utf-8 -*-

"""
BHASA SETU — CREATE TRAINING SAMPLES
60 ISL signs → augmented sequences → train/validation/test
"""

import os
import json
import numpy as np

# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INPUT_DIR = os.path.join(PROJECT_ROOT, "dataset", "prepared")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "dataset", "samples")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================
# SETTINGS
# ============================================================

RANDOM_SEED = 42

# Number of augmented samples per original video
SAMPLES_PER_CLASS = 50

# ============================================================
# LOAD DATA
# ============================================================

print("=" * 80)
print("BHASA SETU — CREATE TRAINING SAMPLES")
print("=" * 80)

X = np.load(
    os.path.join(INPUT_DIR, "X_all.npy")
)

y = np.load(
    os.path.join(INPUT_DIR, "y_all.npy")
)

with open(
    os.path.join(INPUT_DIR, "label_map.json"),
    "r",
    encoding="utf-8"
) as f:
    label_map = json.load(f)

print("\nOriginal dataset:")
print("X:", X.shape)
print("y:", y.shape)
print("Classes:", len(label_map))

# ============================================================
# NORMALIZATION
# ============================================================

def normalize_sequence(sequence):
    """
    Normalize each frame relative to the wrist.

    Each hand:
        21 landmarks × 3 coordinates = 63

    Two hands:
        126 features
    """

    sequence = sequence.copy()

    for frame_idx in range(sequence.shape[0]):

        frame = sequence[frame_idx]

        # Left hand
        left = frame[:63].reshape(21, 3)

        # Right hand
        right = frame[63:].reshape(21, 3)

        # Left wrist = landmark 0
        if np.any(left != 0):
            left = left - left[0]

        # Right wrist = landmark 0
        if np.any(right != 0):
            right = right - right[0]

        sequence[frame_idx] = np.concatenate([
            left.flatten(),
            right.flatten()
        ])

    return sequence


# ============================================================
# AUGMENTATION
# ============================================================

rng = np.random.default_rng(RANDOM_SEED)


def augment(sequence):
    """
    Enhanced augmentation:
    - Small landmark noise
    - Scale variation
    - Temporal speed variation (frame skipping/interpolation)
    - Random frame dropout
    """

    result = sequence.copy()
    num_frames = result.shape[0]

    # Small Gaussian noise (increased variance)
    noise = rng.normal(
        loc=0.0,
        scale=0.012,
        size=result.shape
    ).astype(np.float32)

    # Don't add noise to completely absent hands
    mask = result != 0
    result[mask] += noise[mask]

    # Small global scale variation
    scale = rng.uniform(0.93, 1.07)
    result *= scale

    # Temporal speed variation (0.85x to 1.15x)
    speed = rng.uniform(0.85, 1.15)
    if speed != 1.0:
        original_indices = np.arange(num_frames)
        new_indices = np.linspace(0, num_frames - 1, num_frames) / speed
        new_indices = np.clip(new_indices, 0, num_frames - 1)
        for f in range(num_frames):
            idx_low = int(new_indices[f])
            idx_high = min(idx_low + 1, num_frames - 1)
            weight = new_indices[f] - idx_low
            result[f] = (1 - weight) * result[idx_low] + weight * result[idx_high]

    # Random frame dropout (zero out 5-10% of frames)
    dropout_rate = rng.uniform(0.05, 0.10)
    num_dropout = int(num_frames * dropout_rate)
    if num_dropout > 0:
        dropout_indices = rng.choice(num_frames, size=num_dropout, replace=False)
        result[dropout_indices] = 0.0

    return result.astype(np.float32)


# ============================================================
# CREATE AUGMENTED DATA
# ============================================================

all_samples = []
all_labels = []

print("\n")
print("=" * 80)
print("CREATING AUGMENTED SAMPLES")
print("=" * 80)

for class_index in range(len(X)):

    original = X[class_index]
    label = int(y[class_index])

    # Normalize original
    normalized = normalize_sequence(original)

    for sample_index in range(SAMPLES_PER_CLASS):

        if sample_index == 0:
            # Keep one clean version
            sample = normalized.copy()
        else:
            sample = augment(normalized)

        all_samples.append(sample)
        all_labels.append(label)

    print(
        f"{class_index + 1:02d}/46  "
        f"Class ID: {label:<3} "
        f"Samples: {SAMPLES_PER_CLASS}"
    )

X_aug = np.array(
    all_samples,
    dtype=np.float32
)

y_aug = np.array(
    all_labels,
    dtype=np.int64
)

print("\n")
print("=" * 80)
print("AUGMENTATION COMPLETE")
print("=" * 80)

print("Total samples:", len(X_aug))
print("Shape:", X_aug.shape)

# ============================================================
# STRATIFIED SPLIT
# ============================================================
#
# Every class gets:
# 35 training
# 8 validation
# 7 testing
#
# 50 samples/class total
# ============================================================

X_train = []
y_train = []

X_val = []
y_val = []

X_test = []
y_test = []

for class_id in range(len(label_map)):

    indices = np.where(y_aug == class_id)[0]

    rng.shuffle(indices)

    train_indices = indices[:35]
    val_indices = indices[35:43]
    test_indices = indices[43:50]

    X_train.extend(X_aug[train_indices])
    y_train.extend(y_aug[train_indices])

    X_val.extend(X_aug[val_indices])
    y_val.extend(y_aug[val_indices])

    X_test.extend(X_aug[test_indices])
    y_test.extend(y_aug[test_indices])

# Convert to arrays

X_train = np.array(X_train, dtype=np.float32)
y_train = np.array(y_train, dtype=np.int64)

X_val = np.array(X_val, dtype=np.float32)
y_val = np.array(y_val, dtype=np.int64)

X_test = np.array(X_test, dtype=np.float32)
y_test = np.array(y_test, dtype=np.int64)

# ============================================================
# SHUFFLE TRAINING DATA
# ============================================================

train_order = rng.permutation(len(X_train))

X_train = X_train[train_order]
y_train = y_train[train_order]

# ============================================================
# SAVE
# ============================================================

np.save(
    os.path.join(OUTPUT_DIR, "X_train.npy"),
    X_train
)

np.save(
    os.path.join(OUTPUT_DIR, "y_train.npy"),
    y_train
)

np.save(
    os.path.join(OUTPUT_DIR, "X_val.npy"),
    X_val
)

np.save(
    os.path.join(OUTPUT_DIR, "y_val.npy"),
    y_val
)

np.save(
    os.path.join(OUTPUT_DIR, "X_test.npy"),
    X_test
)

np.save(
    os.path.join(OUTPUT_DIR, "y_test.npy"),
    y_test
)

with open(
    os.path.join(OUTPUT_DIR, "label_map.json"),
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        label_map,
        f,
        ensure_ascii=False,
        indent=4
    )

# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n")
print("=" * 80)
print("TRAINING DATASET READY")
print("=" * 80)

print("\nTRAIN")
print("X_train:", X_train.shape)
print("y_train:", y_train.shape)

print("\nVALIDATION")
print("X_val:", X_val.shape)
print("y_val:", y_val.shape)

print("\nTEST")
print("X_test:", X_test.shape)
print("y_test:", y_test.shape)

print("\nTotal:")
print(
    len(X_train)
    + len(X_val)
    + len(X_test)
)

print("\nSaved to:")
print(OUTPUT_DIR)

print("\nTRAIN / VALIDATION / TEST DATA CREATED!")

print("=" * 80)