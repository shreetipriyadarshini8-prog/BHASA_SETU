# -*- coding: utf-8 -*-
"""
BHASA SETU — ISL MODEL TRAINING
60 medical ISL phrases
"""

import os
import json
import numpy as np

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Masking, BatchNormalization, Bidirectional
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.optimizers import Adam


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, "dataset", "samples")
MODEL_DIR = os.path.join(BASE_DIR, "models")

os.makedirs(MODEL_DIR, exist_ok=True)


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 80)
print("BHASA SETU — ISL MODEL TRAINING")
print("=" * 80)

print("\nLoading training data...")

X_train = np.load(os.path.join(DATA_DIR, "X_train.npy"))
y_train = np.load(os.path.join(DATA_DIR, "y_train.npy"))

X_val = np.load(os.path.join(DATA_DIR, "X_val.npy"))
y_val = np.load(os.path.join(DATA_DIR, "y_val.npy"))

X_test = np.load(os.path.join(DATA_DIR, "X_test.npy"))
y_test = np.load(os.path.join(DATA_DIR, "y_test.npy"))


print("\nTRAIN")
print("X_train:", X_train.shape)
print("y_train:", y_train.shape)

print("\nVALIDATION")
print("X_val:", X_val.shape)
print("y_val:", y_val.shape)

print("\nTEST")
print("X_test:", X_test.shape)
print("y_test:", y_test.shape)


# ============================================================
# NUMBER OF CLASSES
# ============================================================

num_classes = len(np.unique(y_train))

print("\nNumber of classes:", num_classes)


# ============================================================
# BUILD MODEL
# ============================================================

print("\n" + "=" * 80)
print("BUILDING LSTM MODEL")
print("=" * 80)

model = Sequential([
    
    Masking(
        mask_value=0.0,
        input_shape=(60, 126)
    ),

    Bidirectional(LSTM(
        128,
        return_sequences=True
    )),

    BatchNormalization(),

    Dropout(0.3),

    Bidirectional(LSTM(
        64,
        return_sequences=False
    )),

    BatchNormalization(),

    Dropout(0.3),

    Dense(
        128,
        activation="relu"
    ),

    BatchNormalization(),

    Dropout(0.3),

    Dense(
        64,
        activation="relu"
    ),

    Dropout(0.2),

    Dense(
        num_classes,
        activation="softmax"
    )
])


# ============================================================
# COMPILE
# ============================================================

model.compile(
    optimizer=Adam(learning_rate=0.001),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)


print("\nMODEL SUMMARY")
model.summary()


# ============================================================
# CALLBACKS
# ============================================================

model_path = os.path.join(
    MODEL_DIR,
    "isl_model.keras"
)

checkpoint = ModelCheckpoint(
    model_path,
    monitor="val_accuracy",
    save_best_only=True,
    verbose=1
)

early_stop = EarlyStopping(
    monitor="val_accuracy",
    patience=15,
    restore_best_weights=True,
    verbose=1
)

reduce_lr = ReduceLROnPlateau(
    monitor="val_loss",
    factor=0.5,
    patience=5,
    min_lr=1e-6,
    verbose=1
)


# ============================================================
# TRAIN
# ============================================================

print("\n" + "=" * 80)
print("STARTING TRAINING")
print("=" * 80)

history = model.fit(
    X_train,
    y_train,

    validation_data=(
        X_val,
        y_val
    ),

    epochs=100,

    batch_size=16,

    callbacks=[
        checkpoint,
        early_stop,
        reduce_lr
    ],

    verbose=1
)


# ============================================================
# TEST
# ============================================================

print("\n" + "=" * 80)
print("FINAL TEST")
print("=" * 80)

test_loss, test_accuracy = model.evaluate(
    X_test,
    y_test,
    verbose=1
)

print("\nTest Loss     :", test_loss)
print("Test Accuracy :", test_accuracy)


# ============================================================
# SAVE LABEL MAP
# ============================================================

source_label_map = os.path.join(
    BASE_DIR,
    "dataset",
    "prepared",
    "label_map.json"
)

destination_label_map = os.path.join(
    MODEL_DIR,
    "label_map.json"
)

if os.path.exists(source_label_map):

    with open(
        source_label_map,
        "r",
        encoding="utf-8"
    ) as f:

        label_map = json.load(f)

    with open(
        destination_label_map,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            label_map,
            f,
            ensure_ascii=False,
            indent=4
        )

    print("\nLabel map saved:")
    print(destination_label_map)

else:

    print("\nWARNING: label_map.json not found!")


# ============================================================
# SAVE FINAL MODEL
# ============================================================

model.save(
    os.path.join(
        MODEL_DIR,
        "isl_model_final.keras"
    )
)


# ============================================================
# COMPLETE
# ============================================================

print("\n" + "=" * 80)
print("TRAINING COMPLETE!")
print("=" * 80)

print("\nBest model:")
print(model_path)

print("\nFinal model:")
print(
    os.path.join(
        MODEL_DIR,
        "isl_model_final.keras"
    )
)

print("\nTest accuracy:", test_accuracy)

print("\n" + "=" * 80)