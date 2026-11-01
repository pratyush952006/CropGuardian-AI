"""
CropGuardian — ML Training Script
CNN model (EfficientNetV2-S) for plant disease detection
Trained on the PlantVillage dataset (38 classes, ~54K images)
GPU-accelerated with mixed precision training.

Usage:
    python ml/train.py

Output:
    ml/model/crop_disease_model.h5
    ml/model/class_names.json
    ml/plots/training_history.png
"""

import os
import json
import sys
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, mixed_precision
from tensorflow.keras.callbacks import (
    EarlyStopping, ModelCheckpoint, ReduceLROnPlateau, TensorBoard
)
import tensorflow_datasets as tfds

# ─────────────────────────────────────────────
# GPU Setup & Mixed Precision
# ─────────────────────────────────────────────
print("=" * 60)
print("CropGuardian — Model Training")
print("=" * 60)

gpus = tf.config.list_physical_devices('GPU')
if gpus:
    print(f"✅  GPU detected: {len(gpus)} device(s)")
    for gpu in gpus:
        tf.config.experimental.set_memory_growth(gpu, True)
    mixed_precision.set_global_policy('mixed_float16')
    print("✅  Mixed precision enabled (float16)")
else:
    print("⚠️  No GPU found — training on CPU (this will be slow)")
    print("   Tip: Install CUDA toolkit and tensorflow-gpu for GPU support")

# ─────────────────────────────────────────────
# Hyperparameters
# ─────────────────────────────────────────────
IMG_SIZE       = 224       # EfficientNetV2-S native input size
BATCH_SIZE     = 32
EPOCHS_PHASE1  = 10       # Train only the head (frozen base)
EPOCHS_PHASE2  = 20       # Fine-tune top layers
LEARNING_RATE1 = 1e-3
LEARNING_RATE2 = 1e-5
DROPOUT_RATE   = 0.4
NUM_CLASSES    = 38

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR  = os.path.join(BASE_DIR, "model")
PLOTS_DIR  = os.path.join(BASE_DIR, "plots")
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(PLOTS_DIR, exist_ok=True)

MODEL_PATH       = os.path.join(MODEL_DIR, "crop_disease_model.h5")
CLASS_NAMES_PATH = os.path.join(MODEL_DIR, "class_names.json")

# ─────────────────────────────────────────────
# Dataset Loading (PlantVillage via tfds)
# ─────────────────────────────────────────────
print("\n📦  Loading PlantVillage dataset...")
print("    (First run will download ~800MB — subsequent runs use cache)")

(ds_train, ds_val, ds_test), info = tfds.load(
    "plant_village",
    split=["train[:70%]", "train[70%:85%]", "train[85%:]"],
    as_supervised=True,
    with_info=True,
    shuffle_files=True,
)

class_names = info.features["label"].names
NUM_CLASSES = len(class_names)
print(f"✅  Dataset loaded: {NUM_CLASSES} classes")
print(f"    Train: {len(ds_train)} | Val: {len(ds_val)} | Test: {len(ds_test)}")

# Save class names for inference
with open(CLASS_NAMES_PATH, "w") as f:
    json.dump(class_names, f, indent=2)
print(f"✅  Class names saved → {CLASS_NAMES_PATH}")

# ─────────────────────────────────────────────
# Data Preprocessing & Augmentation
# ─────────────────────────────────────────────
AUTOTUNE = tf.data.AUTOTUNE

def preprocess(image, label):
    """Resize and normalize image to [0, 1]."""
    image = tf.image.resize(image, [IMG_SIZE, IMG_SIZE])
    image = tf.cast(image, tf.float32) / 255.0
    return image, label

# Strong augmentation pipeline for training
data_augmentation = keras.Sequential([
    layers.RandomFlip("horizontal_and_vertical"),
    layers.RandomRotation(0.25),
    layers.RandomZoom(0.2),
    layers.RandomContrast(0.2),
    layers.RandomBrightness(0.15),
    layers.RandomTranslation(0.1, 0.1),
], name="data_augmentation")

def preprocess_train(image, label):
    image, label = preprocess(image, label)
    image = data_augmentation(image, training=True)
    return image, label

ds_train = (
    ds_train
    .map(preprocess_train, num_parallel_calls=AUTOTUNE)
    .shuffle(buffer_size=2000)
    .batch(BATCH_SIZE)
    .prefetch(AUTOTUNE)
)

ds_val = (
    ds_val
    .map(preprocess, num_parallel_calls=AUTOTUNE)
    .batch(BATCH_SIZE)
    .prefetch(AUTOTUNE)
)

ds_test = (
    ds_test
    .map(preprocess, num_parallel_calls=AUTOTUNE)
    .batch(BATCH_SIZE)
    .prefetch(AUTOTUNE)
)

# ─────────────────────────────────────────────
# Model Architecture — EfficientNetV2-S
# ─────────────────────────────────────────────
print("\n🏗️   Building EfficientNetV2-S model...")

def build_model(num_classes: int, learning_rate: float, trainable_base: bool = False):
    """Build EfficientNetV2-S with custom classification head."""
    
    # Pre-trained EfficientNetV2-S backbone (ImageNet weights)
    base_model = keras.applications.EfficientNetV2S(
        include_top=False,
        weights="imagenet",
        input_shape=(IMG_SIZE, IMG_SIZE, 3),
    )
    base_model.trainable = trainable_base

    inputs = keras.Input(shape=(IMG_SIZE, IMG_SIZE, 3), name="input_image")
    x = base_model(inputs, training=False)
    x = layers.GlobalAveragePooling2D(name="global_avg_pool")(x)
    x = layers.BatchNormalization(name="batch_norm")(x)
    x = layers.Dropout(DROPOUT_RATE, name="dropout")(x)
    x = layers.Dense(512, activation="relu", name="dense_512")(x)
    x = layers.Dropout(0.2, name="dropout_2")(x)
    # float32 output for mixed precision stability
    outputs = layers.Dense(num_classes, activation="softmax", dtype="float32", name="predictions")(x)

    model = keras.Model(inputs, outputs, name="CropGuardian_EfficientNetV2S")
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy", keras.metrics.SparseTopKCategoricalAccuracy(k=3, name="top3_acc")]
    )
    return model, base_model


# ─────────────────────────────────────────────
# Phase 1: Train Classification Head Only
# ─────────────────────────────────────────────
print("\n🚀  Phase 1: Training classification head (base frozen)...")
model, base_model = build_model(NUM_CLASSES, LEARNING_RATE1, trainable_base=False)
model.summary()

callbacks_phase1 = [
    EarlyStopping(monitor="val_accuracy", patience=5, restore_best_weights=True, verbose=1),
    ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=3, min_lr=1e-6, verbose=1),
    ModelCheckpoint(MODEL_PATH, monitor="val_accuracy", save_best_only=True, verbose=1),
    TensorBoard(log_dir=os.path.join(BASE_DIR, "logs", "phase1")),
]

history1 = model.fit(
    ds_train,
    epochs=EPOCHS_PHASE1,
    validation_data=ds_val,
    callbacks=callbacks_phase1,
    verbose=1,
)

print(f"\n✅  Phase 1 complete. Best val accuracy: {max(history1.history['val_accuracy']):.4f}")


# ─────────────────────────────────────────────
# Phase 2: Fine-Tune Top Layers
# ─────────────────────────────────────────────
print("\n🔬  Phase 2: Fine-tuning top layers of EfficientNetV2-S...")

# Unfreeze the top 100 layers of the base model
base_model.trainable = True
fine_tune_at = len(base_model.layers) - 100
for layer in base_model.layers[:fine_tune_at]:
    layer.trainable = False

trainable_count = sum(1 for l in base_model.layers if l.trainable)
print(f"    Unfreezing top {trainable_count}/{len(base_model.layers)} layers")

# Recompile with lower learning rate
model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=LEARNING_RATE2),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy", keras.metrics.SparseTopKCategoricalAccuracy(k=3, name="top3_acc")]
)

callbacks_phase2 = [
    EarlyStopping(monitor="val_accuracy", patience=7, restore_best_weights=True, verbose=1),
    ReduceLROnPlateau(monitor="val_loss", factor=0.3, patience=4, min_lr=1e-7, verbose=1),
    ModelCheckpoint(MODEL_PATH, monitor="val_accuracy", save_best_only=True, verbose=1),
    TensorBoard(log_dir=os.path.join(BASE_DIR, "logs", "phase2")),
]

history2 = model.fit(
    ds_train,
    epochs=EPOCHS_PHASE2,
    validation_data=ds_val,
    callbacks=callbacks_phase2,
    verbose=1,
)

print(f"\n✅  Phase 2 complete. Best val accuracy: {max(history2.history['val_accuracy']):.4f}")


# ─────────────────────────────────────────────
# Final Evaluation on Test Set
# ─────────────────────────────────────────────
print("\n📊  Evaluating on held-out test set...")
test_loss, test_acc, test_top3 = model.evaluate(ds_test, verbose=1)
print(f"\n{'='*40}")
print(f"  Test Accuracy:      {test_acc*100:.2f}%")
print(f"  Test Top-3 Accuracy:{test_top3*100:.2f}%")
print(f"  Test Loss:          {test_loss:.4f}")
print(f"{'='*40}")


# ─────────────────────────────────────────────
# Plot Training History
# ─────────────────────────────────────────────
def merge_history(h1, h2):
    """Merge two training histories into one for plotting."""
    merged = {}
    for key in h1.history:
        merged[key] = h1.history[key] + h2.history[key]
    return merged

history = merge_history(history1, history2)
phase1_end = len(history1.history["accuracy"])

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle("CropGuardian — EfficientNetV2-S Training History", fontsize=14, fontweight="bold")

# Accuracy plot
axes[0].plot(history["accuracy"], label="Train Accuracy", color="#22c55e", linewidth=2)
axes[0].plot(history["val_accuracy"], label="Val Accuracy", color="#3b82f6", linewidth=2)
axes[0].axvline(x=phase1_end - 1, color="#ef4444", linestyle="--", alpha=0.7, label="Phase 1→2")
axes[0].set_title("Accuracy Over Epochs")
axes[0].set_xlabel("Epoch"); axes[0].set_ylabel("Accuracy")
axes[0].legend(); axes[0].grid(alpha=0.3)

# Loss plot
axes[1].plot(history["loss"], label="Train Loss", color="#f59e0b", linewidth=2)
axes[1].plot(history["val_loss"], label="Val Loss", color="#8b5cf6", linewidth=2)
axes[1].axvline(x=phase1_end - 1, color="#ef4444", linestyle="--", alpha=0.7, label="Phase 1→2")
axes[1].set_title("Loss Over Epochs")
axes[1].set_xlabel("Epoch"); axes[1].set_ylabel("Loss")
axes[1].legend(); axes[1].grid(alpha=0.3)

plt.tight_layout()
plot_path = os.path.join(PLOTS_DIR, "training_history.png")
plt.savefig(plot_path, dpi=150, bbox_inches="tight")
print(f"\n📈  Training plot saved → {plot_path}")

# Save final model
model.save(MODEL_PATH)
print(f"💾  Model saved → {MODEL_PATH}")

print("\n🎉  Training complete! Model is ready for CropGuardian.")
print(f"    Model path: {MODEL_PATH}")
print(f"    Classes:    {NUM_CLASSES}")
print(f"    Test Acc:   {test_acc*100:.2f}%")
