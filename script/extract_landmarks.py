# -*- coding: utf-8 -*-

"""
BHASA SETU — EXTRACT HAND LANDMARKS
46 ISL VIDEOS → LANDMARK DATASET
"""

import os
import cv2
import mediapipe as mp
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import (
    HandLandmarker,
    HandLandmarkerOptions,
)
import pandas as pd
import numpy as np

# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MAPPING_FILE = os.path.join(PROJECT_ROOT, "data", "csv", "isl_mapping_final_v3.csv")

TRAINING_DIR = os.path.join(PROJECT_ROOT, "videos", "training")
CUSTOM_DIR = os.path.join(PROJECT_ROOT, "videos", "custom_isl")

OUTPUT_DIR = os.path.join(PROJECT_ROOT, "dataset", "landmarks")

MODEL_PATH = os.path.join(PROJECT_ROOT, "models", "hand_landmarker.task")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================
# MEDIAPIPE
# ============================================================

options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=MODEL_PATH),
    num_hands=2,
    min_hand_detection_confidence=0.5,
    min_tracking_confidence=0.5,
)

hands = HandLandmarker.create_from_options(options)

# ============================================================
# LOAD MAPPING
# ============================================================

print("=" * 80)
print("BHASA SETU — HAND LANDMARK EXTRACTION")
print("=" * 80)

print("\nReading mapping:")
print(MAPPING_FILE)

df = pd.read_csv(MAPPING_FILE)

# One video per phrase
df = df.drop_duplicates(subset=["phrase_key"])

print("\nUnique phrases:", len(df))

# ============================================================
# EXTRACTION FUNCTION
# ============================================================

def extract_video(video_path):

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        return None

    sequence = []

    while True:

        ret, frame = cap.read()

        if not ret:
            break

        frame_rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=frame_rgb,
        )

        results = hands.detect(mp_image)

        # ----------------------------------------------------
        # Default: no hands
        # 126 values for two hands
        # Each hand = 21 landmarks
        # Each landmark = x,y,z
        # ----------------------------------------------------

        left_hand = np.zeros(63, dtype=np.float32)
        right_hand = np.zeros(63, dtype=np.float32)

        if results.hand_landmarks:

            for hand_landmarks, handedness in zip(
                results.hand_landmarks,
                results.handedness,
            ):

                coords = []

                for landmark in hand_landmarks:

                    coords.extend([
                        landmark.x,
                        landmark.y,
                        landmark.z,
                    ])

                coords = np.array(
                    coords,
                    dtype=np.float32,
                )

                label = handedness[0].category_name

                if label == "Left":
                    left_hand = coords

                elif label == "Right":
                    right_hand = coords

        frame_features = np.concatenate([
            left_hand,
            right_hand,
        ])

        sequence.append(frame_features)

    cap.release()

    if len(sequence) == 0:
        return None

    return np.array(
        sequence,
        dtype=np.float32,
    )


# ============================================================
# PROCESS VIDEOS
# ============================================================

success = 0
failed = 0

print("\n")
print("=" * 80)
print("STARTING EXTRACTION")
print("=" * 80)

for index, row in df.iterrows():

    phrase = str(row["phrase_key"])
    video_name = str(row["video_name"])
    quality = str(row["match_quality"])

    print("\n" + "-" * 80)
    print(f"{index + 1}/{len(df)}")
    print("Phrase :", phrase)
    print("Video  :", video_name)

    # --------------------------------------------------------
    # FIND VIDEO
    # --------------------------------------------------------

    if quality == "CUSTOM_ISL_DICTIONARY":

        video_path = os.path.join(
            CUSTOM_DIR,
            video_name
        )

    else:

        video_path = os.path.join(
            TRAINING_DIR,
            phrase,
            video_name
        )

    if not os.path.exists(video_path):

        print("VIDEO NOT FOUND")
        failed += 1
        continue

    print("Extracting landmarks...")

    # --------------------------------------------------------
    # EXTRACT
    # --------------------------------------------------------

    data = extract_video(video_path)

    if data is None:

        print("EXTRACTION FAILED")
        failed += 1
        continue

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    output_file = os.path.join(
        OUTPUT_DIR,
        phrase + ".npy"
    )

    np.save(
        output_file,
        data
    )

    print("SUCCESS")
    print("Frames :", data.shape[0])
    print("Features per frame :", data.shape[1])
    print("Saved :", output_file)

    success += 1


# ============================================================
# CLOSE MEDIAPIPE
# ============================================================

hands.close()

# ============================================================
# FINAL RESULT
# ============================================================

print("\n")
print("=" * 80)
print("LANDMARK EXTRACTION COMPLETE")
print("=" * 80)

print("Expected phrases :", len(df))
print("Successful       :", success)
print("Failed           :", failed)

print("\nOutput folder:")
print(OUTPUT_DIR)

print("=" * 80)
