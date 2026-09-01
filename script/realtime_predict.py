# -*- coding: utf-8 -*-

"""
BHASA SETU — REAL-TIME ISL RECOGNITION
=======================================

46 ISL CLASSES
60 FRAMES x 126 FEATURES

FLOW:

Camera
   |
MediaPipe
   |
126 landmark features
   |
60-frame sequence
   |
Wrist normalization
   |
LSTM model
   |
Confidence filtering
   |
Prediction voting
   |
3 confirmations
   |
LOCKED SIGN
   |
recognition_result.json
   |
Streamlit BHASA SETU app

Controls:
    R = Reset / recognize next sign
    Q = Quit
"""

import os
import cv2
import json
import numpy as np
import tensorflow as tf
import mediapipe as mp
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import (
    HandLandmarker,
    HandLandmarkerOptions,
)

from collections import deque, Counter


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_PATH = os.path.join(PROJECT_ROOT, "models", "isl_model.keras")

LABEL_MAP_PATH = os.path.join(PROJECT_ROOT, "models", "label_map.json")

RESULT_PATH = os.path.join(PROJECT_ROOT, "app", "recognition_result.json")

HAND_MODEL_PATH = os.path.join(PROJECT_ROOT, "models", "hand_landmarker.task")


# ============================================================
# SETTINGS
# ============================================================

SEQUENCE_LENGTH = 60

FEATURES = 126

CONFIDENCE_THRESHOLD = 0.60

PREDICTION_HISTORY = 8

MIN_VOTES = 5

MIN_HAND_FRAMES = 45

MIN_CONFIRMATIONS = 3


# ============================================================
# MEDICAL LANGUAGE MAP
# ============================================================

LANGUAGE_MAP = {
    "back_pain": {
        "english": "I have back pain.",
        "hindi": "मेरी पीठ में दर्द है।"
    },
    "bleeding": {
        "english": "I am bleeding.",
        "hindi": "मुझे खून बह रहा है।"
    },
    "body_pain": {
        "english": "I have body pain.",
        "hindi": "मेरे शरीर में दर्द है।"
    },
    "breathing_difficulty": {
        "english": "I have difficulty breathing.",
        "hindi": "मुझे सांस लेने में कठिनाई हो रही है।"
    },
    "call_for_help": {
        "english": "Please call for help.",
        "hindi": "कृपया मदद बुलाइए।"
    },
    "cannot_breathe": {
        "english": "I cannot breathe properly.",
        "hindi": "मैं ठीक से सांस नहीं ले पा रहा हूँ।"
    },
    "chest_pain": {
        "english": "I have chest pain.",
        "hindi": "मेरे सीने में दर्द है।"
    },
    "cold": {
        "english": "I have a cold.",
        "hindi": "मुझे सर्दी है।"
    },
    "constant_pain": {
        "english": "The pain is constant.",
        "hindi": "दर्द लगातार है।"
    },
    "cough": {
        "english": "I have a cough.",
        "hindi": "मुझे खांसी है।"
    },
    "diabetes": {
        "english": "I have diabetes.",
        "hindi": "मुझे मधुमेह है।"
    },
    "diarrhea": {
        "english": "I have diarrhea.",
        "hindi": "मुझे दस्त हो रहे हैं।"
    },
    "dizzy": {
        "english": "I feel dizzy.",
        "hindi": "मुझे चक्कर आ रहा है।"
    },
    "emergency_help": {
        "english": "I need emergency help.",
        "hindi": "मुझे तुरंत मदद चाहिए।"
    },
    "fainted": {
        "english": "I fainted.",
        "hindi": "मैं बेहोश हो गया था।"
    },
    "fever": {
        "english": "I have a fever.",
        "hindi": "मुझे बुखार है।"
    },
    "food_allergy": {
        "english": "I am allergic to food.",
        "hindi": "मुझे कुछ खाने की चीजों से एलर्जी है।"
    },
    "getting_better": {
        "english": "It is getting better.",
        "hindi": "यह बेहतर हो रहा है।"
    },
    "getting_worse": {
        "english": "It is getting worse.",
        "hindi": "यह और खराब हो रहा है।"
    },
    "headache": {
        "english": "I have a headache.",
        "hindi": "मुझे सिरदर्द है।"
    },
    "help": {
        "english": "Please help me.",
        "hindi": "कृपया मेरी मदद करें।"
    },
    "high_blood_pressure": {
        "english": "I have high blood pressure.",
        "hindi": "मुझे उच्च रक्तचाप है।"
    },
    "hurt": {
        "english": "I have pain or hurt.",
        "hindi": "मुझे दर्द हो रहा है।"
    },
    "joint_pain": {
        "english": "I have joint pain.",
        "hindi": "मेरे जोड़ों में दर्द है।"
    },
    "medicine": {
        "english": "I need or take medicine.",
        "hindi": "मुझे दवा चाहिए या मैं दवा ले रहा हूँ।"
    },
    "neck_pain": {
        "english": "I have neck pain.",
        "hindi": "मेरी गर्दन में दर्द है।"
    },
    "need_doctor": {
        "english": "I need a doctor.",
        "hindi": "मुझे डॉक्टर चाहिए।"
    },
    "one_week": {
        "english": "I have had this for a week.",
        "hindi": "मुझे यह समस्या एक सप्ताह से है।"
    },
    "pain": {
        "english": "I have pain.",
        "hindi": "मुझे दर्द है।"
    },
    "past_problem": {
        "english": "I had this problem before.",
        "hindi": "मुझे पहले भी यह समस्या हुई है।"
    },
    "pregnant": {
        "english": "I am pregnant.",
        "hindi": "मैं गर्भवती हूँ।"
    },
    "runny_nose": {
        "english": "I have a runny nose.",
        "hindi": "मेरी नाक बह रही है।"
    },
    "shivering": {
        "english": "I am shivering.",
        "hindi": "मुझे कंपकंपी हो रही है।"
    },
    "sore_throat": {
        "english": "I have a sore throat.",
        "hindi": "मेरे गले में खराश है।"
    },
    "started_slowly": {
        "english": "It started slowly.",
        "hindi": "यह धीरे-धीरे शुरू हुआ।"
    },
    "started_suddenly": {
        "english": "It started suddenly.",
        "hindi": "यह अचानक शुरू हुआ।"
    },
    "started_today": {
        "english": "It started today.",
        "hindi": "यह आज शुरू हुआ है।"
    },
    "started_two_days_ago": {
        "english": "It started two days ago.",
        "hindi": "यह दो दिन पहले शुरू हुआ है।"
    },
    "started_yesterday": {
        "english": "It started yesterday.",
        "hindi": "यह कल शुरू हुआ है।"
    },
    "take_to_hospital": {
        "english": "Please take me to the hospital.",
        "hindi": "कृपया मुझे अस्पताल ले जाइए।"
    },
    "tired": {
        "english": "I feel tired.",
        "hindi": "मैं थका हुआ हूँ।"
    },
    "toothache": {
        "english": "I have a toothache.",
        "hindi": "मेरे दांत में दर्द है।"
    },
    "very_sick": {
        "english": "I feel very sick.",
        "hindi": "मैं बहुत बीमार हूँ।"
    },
    "vomiting": {
        "english": "I am vomiting.",
        "hindi": "मुझे उल्टी हो रही है।"
    },
    "water": {
        "english": "I need water.",
        "hindi": "मुझे पानी चाहिए।"
    },
    "weak": {
        "english": "I feel weak.",
        "hindi": "मुझे कमजोरी महसूस हो रही है।"
    }
}


# ============================================================
# HEADER
# ============================================================

print("=" * 80)
print("BHASA SETU — REAL-TIME MEDICAL ISL RECOGNITION")
print("=" * 80)


# ============================================================
# CHECK FILES
# ============================================================

if not os.path.exists(MODEL_PATH):

    print("\nERROR: Model not found!")
    print(MODEL_PATH)
    raise SystemExit


if not os.path.exists(LABEL_MAP_PATH):

    print("\nERROR: Label map not found!")
    print(LABEL_MAP_PATH)
    raise SystemExit


# ============================================================
# LOAD MODEL
# ============================================================

print("\nLoading model...")

try:
    model = tf.keras.models.load_model(
        MODEL_PATH
    )
except Exception as e:
    print(f"\nERROR: Failed to load model!")
    print(f"Path: {MODEL_PATH}")
    print(f"Error: {e}")
    raise SystemExit

print("Model loaded successfully!")

print("\nModel input shape:")
print(model.input_shape)


# ============================================================
# CHECK MODEL INPUT
# ============================================================

if model.input_shape[-2:] != (
    SEQUENCE_LENGTH,
    FEATURES
):

    print("\nWARNING:")
    print("Expected input:", (SEQUENCE_LENGTH, FEATURES))
    print("Actual input:", model.input_shape)


# ============================================================
# LOAD LABEL MAP
# ============================================================

print("\nLoading label map...")

try:
    with open(
        LABEL_MAP_PATH,
        "r",
        encoding="utf-8"
    ) as f:

        label_map = json.load(f)
except Exception as e:
    print(f"\nERROR: Failed to load label map!")
    print(f"Path: {LABEL_MAP_PATH}")
    print(f"Error: {e}")
    raise SystemExit


if all(
    str(k).isdigit()
    for k in label_map.keys()
):

    index_to_label = {
        int(k): v
        for k, v in label_map.items()
    }

else:

    index_to_label = {
        int(v): k
        for k, v in label_map.items()
    }


print(
    "\nNumber of labels:",
    len(index_to_label)
)


# ============================================================
# MEDIAPIPE
# ============================================================

HAND_CONNECTIONS = [
    (0,1),(1,2),(2,3),(3,4),
    (0,5),(5,6),(6,7),(7,8),
    (5,9),(9,10),(10,11),(11,12),
    (9,13),(13,14),(14,15),(15,16),
    (13,17),(17,18),(18,19),(19,20),
    (0,17),
]


hand_options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=HAND_MODEL_PATH),
    num_hands=2,
    min_hand_detection_confidence=0.5,
    min_tracking_confidence=0.5,
)

hands = HandLandmarker.create_from_options(hand_options)


print("\nMediaPipe Hands ready!")


# ============================================================
# LANDMARK EXTRACTION
# ============================================================

def get_landmarks(results):

    left_hand = np.zeros(
        63,
        dtype=np.float32
    )

    right_hand = np.zeros(
        63,
        dtype=np.float32
    )


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
                    landmark.z
                ])


            coords = np.array(
                coords,
                dtype=np.float32
            )


            label = handedness[0].category_name


            if label == "Left":

                left_hand = coords

            elif label == "Right":

                right_hand = coords


    return np.concatenate([
        left_hand,
        right_hand
    ])


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_sequence(sequence):

    sequence = sequence.copy()


    for frame_idx in range(
        sequence.shape[0]
    ):

        frame = sequence[frame_idx]


        left = frame[:63].reshape(
            21,
            3
        )

        right = frame[63:].reshape(
            21,
            3
        )


        if np.any(left != 0):

            left = left - left[0]


        if np.any(right != 0):

            right = right - right[0]


        sequence[frame_idx] = np.concatenate([
            left.flatten(),
            right.flatten()
        ])


    return sequence


# ============================================================
# SAVE RESULT
# ============================================================

def save_result(sign, confidence):

    language_data = LANGUAGE_MAP.get(
        sign,
        {
            "english": sign.replace("_", " "),
            "hindi": sign.replace("_", " "),
            "hindi": sign.replace("_", " ")
        }
    )


    result = {

        "sign": sign,

        "confidence": float(confidence),

        "english": language_data["english"],

        "hindi": language_data["hindi"],

        "hindi": language_data["hindi"]

    }


    try:

        with open(
            RESULT_PATH,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                result,
                f,
                ensure_ascii=False,
                indent=4
            )


        print("\nRESULT SENT TO BHASA SETU APP")

        print("Sign:", sign)

        print(
            "Confidence:",
            f"{confidence * 100:.2f}%"
        )

        print(
            "English:",
            language_data["english"]
        )

        print(
            "Hindi:",
            language_data["hindi"]
        )

        print(
            "Odia:",
            language_data["odia"]
        )

        print(
            "File:",
            RESULT_PATH
        )


    except Exception as e:

        print(
            "\nERROR SAVING RESULT:",
            e
        )


# ============================================================
# CAMERA
# ============================================================

print("\nOpening camera...")

try:
    cap = cv2.VideoCapture(0)

    cap.set(
        cv2.CAP_PROP_FRAME_WIDTH,
        1280
    )

    cap.set(
        cv2.CAP_PROP_FRAME_HEIGHT,
        720
    )

    if not cap.isOpened():
        print("\nERROR: Camera could not be opened.")
        print("Please check that a camera is connected.")
        hands.close()
        raise SystemExit

except Exception as e:
    print(f"\nERROR: Camera initialization failed!")
    print(f"Error: {e}")
    hands.close()
    raise SystemExit


print("\nCamera started!")


print("\nInstructions:")

print("1. Show ONE ISL sign.")

print("2. Hold it steadily.")

print("3. Wait for recognition.")

print("4. Press R for the next sign.")

print("5. Press Q to quit.")


# ============================================================
# VARIABLES
# ============================================================

sequence = []

prediction_history = deque(
    maxlen=PREDICTION_HISTORY
)

current_prediction = "Waiting..."

current_confidence = 0.0

locked_prediction = "None"

locked_confidence = 0.0

confirmation_count = 0

recognizing = True


# ============================================================
# MAIN LOOP
# ============================================================

while True:

    ret, frame = cap.read()


    if not ret:

        print("Camera frame failed.")

        break


    # ========================================================
    # MIRROR
    # ========================================================

    frame = cv2.flip(
        frame,
        1
    )


    # ========================================================
    # RGB
    # ========================================================

    rgb = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )


    # ========================================================
    # MEDIAPIPE
    # ========================================================

    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb,
    )

    results = hands.detect(mp_image)


    # ========================================================
    # LANDMARKS
    # ========================================================

    features = get_landmarks(
        results
    )


    # ========================================================
    # DRAW HANDS
    # ========================================================

    if results.hand_landmarks:

        for hand_landmarks in results.hand_landmarks:

            h, w, _ = frame.shape

            for connection in HAND_CONNECTIONS:

                i, j = connection

                x1 = int(hand_landmarks[i].x * w)
                y1 = int(hand_landmarks[i].y * h)
                x2 = int(hand_landmarks[j].x * w)
                y2 = int(hand_landmarks[j].y * h)

                cv2.line(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (0, 255, 0),
                    2,
                )

            for lm in hand_landmarks:

                cx = int(lm.x * w)
                cy = int(lm.y * h)

                cv2.circle(
                    frame,
                    (cx, cy),
                    4,
                    (0, 0, 255),
                    -1,
                )


    # ========================================================
    # COLLECT SEQUENCE
    # ========================================================

    if recognizing:

        sequence.append(
            features
        )


        if len(sequence) > SEQUENCE_LENGTH:

            sequence.pop(0)


    # ========================================================
    # PREDICTION
    # ========================================================

    if (
        recognizing
        and
        len(sequence) == SEQUENCE_LENGTH
    ):

        input_data = np.array(
            sequence,
            dtype=np.float32
        )


        nonzero_frames = np.sum(

            np.any(
                input_data != 0,
                axis=1
            )

        )


        if nonzero_frames < MIN_HAND_FRAMES:

            current_prediction = (
                "SHOW HAND PROPERLY"
            )

            current_confidence = 0.0


            prediction_history.clear()

            confirmation_count = 0


        else:

            normalized = normalize_sequence(
                input_data
            )


            normalized_input = np.expand_dims(
                normalized,
                axis=0
            )


            probabilities = model.predict(
                normalized_input,
                verbose=0
            )[0]


            predicted_index = int(
                np.argmax(probabilities)
            )


            confidence = float(
                probabilities[predicted_index]
            )


            predicted_label = index_to_label.get(
                predicted_index,
                "Unknown"
            )


            current_prediction = predicted_label

            current_confidence = confidence


            # =================================================
            # CONFIDENCE FILTER
            # =================================================

            if confidence >= CONFIDENCE_THRESHOLD:

                prediction_history.append(
                    predicted_index
                )


                counts = Counter(
                    prediction_history
                )


                most_common_index, votes = (
                    counts.most_common(1)[0]
                )


                most_common_label = (
                    index_to_label.get(
                        most_common_index,
                        "Unknown"
                    )
                )


                # =================================================
                # VOTING
                # =================================================

                if votes >= MIN_VOTES:

                    if (
                        most_common_label
                        ==
                        current_prediction
                    ):

                        confirmation_count += 1

                    else:

                        confirmation_count = 0


                    print(
                        "\nCandidate:",
                        most_common_label
                    )

                    print(
                        "Confidence:",
                        f"{confidence * 100:.2f}%"
                    )

                    print(
                        "Votes:",
                        f"{votes}/{len(prediction_history)}"
                    )

                    print(
                        "Confirmation:",
                        f"{confirmation_count}/{MIN_CONFIRMATIONS}"
                    )


                    # =================================================
                    # LOCK SIGN
                    # =================================================

                    if (
                        confirmation_count
                        >=
                        MIN_CONFIRMATIONS
                    ):

                        locked_prediction = (
                            most_common_label
                        )

                        locked_confidence = (
                            confidence
                        )

                        recognizing = False


                        # SAVE RESULT FOR STREAMLIT

                        save_result(
                            locked_prediction,
                            locked_confidence
                        )


                        print(
                            "\n"
                            + "=" * 70
                        )

                        print(
                            "SIGN RECOGNIZED!"
                        )

                        print(
                            "SIGN:",
                            locked_prediction
                        )

                        print(
                            "CONFIDENCE:",
                            f"{locked_confidence * 100:.2f}%"
                        )

                        print(
                            "=" * 70
                        )


            else:

                prediction_history.clear()

                confirmation_count = 0


    # ========================================================
    # DISPLAY PANEL
    # ========================================================

    cv2.rectangle(
        frame,
        (10, 10),
        (780, 190),
        (0, 0, 0),
        -1
    )


    cv2.putText(
        frame,
        "BHASA SETU",
        (25, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2
    )


    if recognizing:

        status = "RECOGNIZING..."

    else:

        status = "SIGN LOCKED"


    cv2.putText(
        frame,
        status,
        (25, 70),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 255, 255),
        2
    )


    cv2.putText(
        frame,
        f"Current: {current_prediction}",
        (25, 105),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.60,
        (255, 255, 255),
        2
    )


    cv2.putText(
        frame,
        f"Recognized: {locked_prediction}",
        (25, 140),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 255, 255),
        2
    )


    cv2.putText(
        frame,
        f"Confidence: {current_confidence * 100:.1f}%",
        (25, 170),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        2
    )


    cv2.putText(
        frame,
        f"Frames: {len(sequence)}/{SEQUENCE_LENGTH}",
        (20, 690),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )


    if recognizing:

        bottom_status = "SHOW SIGN"

    else:

        bottom_status = "PRESS R FOR NEXT SIGN"


    cv2.putText(
        frame,
        bottom_status,
        (850, 690),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 255, 255),
        2
    )


    # ========================================================
    # SHOW CAMERA
    # ========================================================

    cv2.imshow(
        "BHASA SETU - ISL Recognition",
        frame
    )


    # ========================================================
    # KEYBOARD
    # ========================================================

    key = cv2.waitKey(1) & 0xFF


    # ========================================================
    # RESET
    # ========================================================

    if key == ord("r"):

        print(
            "\nRESETTING..."
        )


        sequence.clear()

        prediction_history.clear()

        current_prediction = "Waiting..."

        current_confidence = 0.0

        locked_prediction = "None"

        locked_confidence = 0.0

        confirmation_count = 0

        recognizing = True


        print(
            "Ready for next sign."
        )


    # ========================================================
    # QUIT
    # ========================================================

    if key == ord("q"):

        print(
            "\nQ pressed."
        )

        break


# ============================================================
# CLEANUP
# ============================================================

cap.release()

cv2.destroyAllWindows()

hands.close()


print("\n")

print("=" * 80)

print(
    "BHASA SETU REAL-TIME RECOGNITION STOPPED"
)

print("=" * 80)
