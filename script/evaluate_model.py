# -*- coding: utf-8 -*-
"""
BHASA SETU — MODEL EVALUATION
Evaluates the trained ISL model with confusion matrix and per-class metrics.
"""

import os
import json
import numpy as np
import pandas as pd
from sklearn.metrics import (
    confusion_matrix,
    classification_report,
    accuracy_score,
    f1_score,
    precision_score,
    recall_score
)

# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(PROJECT_ROOT, "dataset", "samples")
MODEL_DIR = os.path.join(PROJECT_ROOT, "models")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 80)
print("BHASA SETU — MODEL EVALUATION")
print("=" * 80)

print("\nLoading test data...")

X_test = np.load(os.path.join(DATA_DIR, "X_test.npy"))
y_test = np.load(os.path.join(DATA_DIR, "y_test.npy"))

print(f"Test samples: {X_test.shape[0]}")
print(f"Sequence length: {X_test.shape[1]}")
print(f"Features: {X_test.shape[2]}")


# ============================================================
# LOAD MODEL
# ============================================================

print("\nLoading model...")

import tensorflow as tf

model = tf.keras.models.load_model(
    os.path.join(MODEL_DIR, "isl_model.keras")
)

print("Model loaded!")


# ============================================================
# LOAD LABEL MAP
# ============================================================

with open(
    os.path.join(MODEL_DIR, "label_map.json"),
    "r",
    encoding="utf-8"
) as f:
    label_map = json.load(f)

# Handle both key formats
if all(str(k).isdigit() for k in label_map.keys()):
    index_to_label = {int(k): v for k, v in label_map.items()}
else:
    index_to_label = {int(v): k for k, v in label_map.items()}

class_names = [index_to_label[i] for i in range(len(index_to_label))]


# ============================================================
# PREDICTIONS
# ============================================================

print("\nRunning predictions on test set...")

y_pred_probs = model.predict(X_test, verbose=1)
y_pred = np.argmax(y_pred_probs, axis=1)


# ============================================================
# OVERALL METRICS
# ============================================================

print("\n" + "=" * 80)
print("OVERALL METRICS")
print("=" * 80)

accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, average="weighted", zero_division=0)
recall = recall_score(y_test, y_pred, average="weighted", zero_division=0)
f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)

print(f"\nAccuracy:  {accuracy * 100:.2f}%")
print(f"Precision: {precision * 100:.2f}%")
print(f"Recall:    {recall * 100:.2f}%")
print(f"F1 Score:  {f1 * 100:.2f}%")


# ============================================================
# PER-CLASS REPORT
# ============================================================

print("\n" + "=" * 80)
print("PER-CLASS CLASSIFICATION REPORT")
print("=" * 80)

report = classification_report(
    y_test,
    y_pred,
    target_names=class_names,
    zero_division=0
)

print(report)


# ============================================================
# CONFUSION MATRIX
# ============================================================

print("\n" + "=" * 80)
print("CONFUSION MATRIX")
print("=" * 80)

cm = confusion_matrix(y_test, y_pred)

# Save confusion matrix to CSV
cm_df = pd.DataFrame(
    cm,
    index=class_names,
    columns=class_names
)

cm_path = os.path.join(OUTPUT_DIR, "confusion_matrix.csv")
cm_df.to_csv(cm_path, encoding="utf-8-sig")
print(f"\nConfusion matrix saved to: {cm_path}")


# ============================================================
# WORST PERFORMING CLASSES
# ============================================================

print("\n" + "=" * 80)
print("WORST PERFORMING CLASSES (F1 < 0.5)")
print("=" * 80)

report_dict = classification_report(
    y_test,
    y_pred,
    target_names=class_names,
    output_dict=True,
    zero_division=0
)

worst = []
for class_name in class_names:
    if class_name in report_dict:
        f1_score_val = report_dict[class_name]["f1-score"]
        support = report_dict[class_name]["support"]
        if f1_score_val < 0.5 and support > 0:
            worst.append({
                "class": class_name,
                "f1_score": f1_score_val,
                "precision": report_dict[class_name]["precision"],
                "recall": report_dict[class_name]["recall"],
                "support": support
            })

worst.sort(key=lambda x: x["f1_score"])

if worst:
    print(f"\n{'Class':<25} {'Precision':>10} {'Recall':>10} {'F1':>10} {'Support':>10}")
    print("-" * 65)
    for item in worst:
        print(
            f"{item['class']:<25} "
            f"{item['precision']:>10.2%} "
            f"{item['recall']:>10.2%} "
            f"{item['f1_score']:>10.2%} "
            f"{item['support']:>10.0f}"
        )
else:
    print("\nAll classes have F1 >= 0.5!")


# ============================================================
# SAVE FULL REPORT
# ============================================================

report_path = os.path.join(OUTPUT_DIR, "evaluation_report.txt")
with open(report_path, "w", encoding="utf-8") as f:
    f.write("BHASA SETU — MODEL EVALUATION REPORT\n")
    f.write("=" * 80 + "\n\n")
    f.write(f"Accuracy:  {accuracy * 100:.2f}%\n")
    f.write(f"Precision: {precision * 100:.2f}%\n")
    f.write(f"Recall:    {recall * 100:.2f}%\n")
    f.write(f"F1 Score:  {f1 * 100:.2f}%\n\n")
    f.write("CLASSIFICATION REPORT\n")
    f.write("-" * 80 + "\n")
    f.write(report)
    f.write("\n")

print(f"\nFull report saved to: {report_path}")


# ============================================================
# COMPLETE
# ============================================================

print("\n" + "=" * 80)
print("EVALUATION COMPLETE!")
print("=" * 80)
