"""
CropGuardian — ML Model Evaluation Script
Loads the trained model and generates:
  - Classification report (precision, recall, F1-score per class)
  - Confusion matrix heatmap
  - Sample predictions with visualizations
  - Per-crop accuracy summary

Usage:
    python ml/evaluate.py
"""

import os
import sys
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix
import tensorflow as tf
import tensorflow_datasets as tfds

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR  = os.path.join(BASE_DIR, "model")
PLOTS_DIR  = os.path.join(BASE_DIR, "plots")
os.makedirs(PLOTS_DIR, exist_ok=True)

MODEL_PATH       = os.path.join(MODEL_DIR, "crop_disease_model.h5")
CLASS_NAMES_PATH = os.path.join(MODEL_DIR, "class_names.json")

IMG_SIZE   = 224
BATCH_SIZE = 32

print("=" * 60)
print("CropGuardian — Model Evaluation")
print("=" * 60)

# ─── Load Model ───
if not os.path.exists(MODEL_PATH):
    print(f"❌  Model not found at: {MODEL_PATH}")
    print("    Run: python ml/train.py first")
    sys.exit(1)

print(f"\n📦  Loading model from {MODEL_PATH}...")
model = tf.keras.models.load_model(MODEL_PATH)
print("✅  Model loaded")

# ─── Load Class Names ───
with open(CLASS_NAMES_PATH) as f:
    class_names = json.load(f)
print(f"✅  {len(class_names)} classes loaded")

# ─── Load Test Dataset ───
print("\n📦  Loading test split from PlantVillage dataset...")
(_, _, ds_test), info = tfds.load(
    "plant_village",
    split=["train[:70%]", "train[70%:85%]", "train[85%:]"],
    as_supervised=True,
    with_info=True,
)

def preprocess(image, label):
    image = tf.image.resize(image, [IMG_SIZE, IMG_SIZE])
    image = tf.cast(image, tf.float32) / 255.0
    return image, label

AUTOTUNE = tf.data.AUTOTUNE
ds_test = ds_test.map(preprocess, num_parallel_calls=AUTOTUNE).batch(BATCH_SIZE).prefetch(AUTOTUNE)

# ─── Generate Predictions ───
print("\n🔮  Generating predictions on test set...")
y_true, y_pred = [], []
for images, labels in ds_test:
    preds = model.predict(images, verbose=0)
    y_true.extend(labels.numpy().tolist())
    y_pred.extend(np.argmax(preds, axis=1).tolist())

y_true = np.array(y_true)
y_pred = np.array(y_pred)

# ─── Overall Accuracy ───
accuracy = np.mean(y_true == y_pred)
print(f"\n{'='*50}")
print(f"  Overall Test Accuracy: {accuracy*100:.2f}%")
print(f"  Total Test Samples:    {len(y_true)}")
print(f"{'='*50}")

# ─── Classification Report ───
report = classification_report(
    y_true, y_pred,
    target_names=class_names,
    digits=4,
    zero_division=0,
)
print(f"\n📊  Classification Report:\n")
print(report)

report_path = os.path.join(PLOTS_DIR, "classification_report.txt")
with open(report_path, "w") as f:
    f.write(f"CropGuardian — Classification Report\n")
    f.write(f"Overall Accuracy: {accuracy*100:.2f}%\n\n")
    f.write(report)
print(f"📄  Report saved → {report_path}")

# ─── Confusion Matrix ───
print("\n📊  Generating confusion matrix...")
cm = confusion_matrix(y_true, y_pred)
cm_norm = cm.astype(float) / cm.sum(axis=1, keepdims=True)

fig_cm, ax = plt.subplots(figsize=(22, 18))
sns.heatmap(
    cm_norm,
    xticklabels=[cn.split("___")[-1].replace("_", " ")[:25] for cn in class_names],
    yticklabels=[cn.split("___")[-1].replace("_", " ")[:25] for cn in class_names],
    cmap="Greens",
    annot=False,
    fmt=".2f",
    linewidths=0.3,
    linecolor="#111827",
    ax=ax,
)
ax.set_title(f"CropGuardian — Confusion Matrix (Test Acc: {accuracy*100:.2f}%)",
             fontsize=14, pad=20, color="#f9fafb")
ax.set_xlabel("Predicted", fontsize=12)
ax.set_ylabel("True", fontsize=12)
ax.tick_params(axis="x", rotation=60, labelsize=7)
ax.tick_params(axis="y", rotation=0, labelsize=7)

plt.tight_layout()
cm_path = os.path.join(PLOTS_DIR, "confusion_matrix.png")
plt.savefig(cm_path, dpi=120, bbox_inches="tight", facecolor="#0d1117")
print(f"📈  Confusion matrix saved → {cm_path}")

# ─── Per-Class Accuracy Bar Chart ───
print("\n📊  Generating per-class accuracy chart...")
per_class_acc = cm_norm.diagonal()

fig_acc, ax2 = plt.subplots(figsize=(14, max(8, len(class_names) * 0.35)))
fig_acc.patch.set_facecolor("#0d1117")
ax2.set_facecolor("#111827")

short_names = [cn.replace("_", " ").replace("   ", " — ") for cn in class_names]
colors = ["#22c55e" if a >= 0.95 else "#f59e0b" if a >= 0.85 else "#ef4444" for a in per_class_acc]

bars = ax2.barh(short_names, per_class_acc, color=colors, height=0.7, edgecolor="#1a2332")
ax2.set_xlim(0, 1.05)
ax2.set_xlabel("Accuracy", color="#9ca3af", fontsize=11)
ax2.set_title("Per-Class Test Accuracy", color="#f9fafb", fontsize=13, pad=12)
ax2.tick_params(colors="#9ca3af", labelsize=8)
ax2.xaxis.set_tick_params(colors="#9ca3af")

for bar, acc in zip(bars, per_class_acc):
    ax2.text(acc + 0.005, bar.get_y() + bar.get_height() / 2,
             f"{acc*100:.1f}%", va="center", ha="left", fontsize=7, color="#9ca3af")

# Legend
from matplotlib.patches import Patch
legend = [
    Patch(facecolor="#22c55e", label="≥ 95% (Excellent)"),
    Patch(facecolor="#f59e0b", label="85–95% (Good)"),
    Patch(facecolor="#ef4444", label="< 85% (Needs improvement)"),
]
ax2.legend(handles=legend, loc="lower right", fontsize=9,
           facecolor="#1a2332", edgecolor="#374151", labelcolor="#9ca3af")

plt.tight_layout()
acc_path = os.path.join(PLOTS_DIR, "per_class_accuracy.png")
plt.savefig(acc_path, dpi=120, bbox_inches="tight", facecolor="#0d1117")
print(f"📈  Per-class chart saved → {acc_path}")

print(f"\n🎉  Evaluation complete!")
print(f"    Test Accuracy: {accuracy*100:.2f}%")
print(f"    Plots saved to: {PLOTS_DIR}")
