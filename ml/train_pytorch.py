"""
CropGuardian — PyTorch Training Script
EfficientNetV2-S CNN model for plant disease detection on the PlantVillage dataset.
GPU-accelerated with mixed precision training (torch.cuda.amp).

Architecture:
    EfficientNetV2-S (Pretrained on ImageNet)
    Two-Phase Transfer Learning:
      - Phase 1: 10 epochs, frozen base, lr=1e-3
      - Phase 2: 15 epochs, fine-tuning top 3 blocks, lr=1e-5
    Optimizer: Adam
    Scheduler: CosineAnnealingLR
    Data Augmentation: RandomResizedCrop, RandomHorizontalFlip, RandomVerticalFlip,
                       RandomRotation(25), ColorJitter

Usage:
    python ml/train_pytorch.py
    python ml/train_pytorch.py --batch-size 32 --epochs-phase1 10 --epochs-phase2 15

Outputs:
    ml/model/crop_disease_model.pth       (Best model weights)
    ml/model/class_names.json            (Class label names mapping)
    ml/plots/training_history.png         (Loss & accuracy curves)
    ml/plots/classification_report.txt   (Test classification report)
"""

import os
import sys

# Force UTF-8 stdout/stderr on Windows to prevent charmap UnicodeEncodeError
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import json
import time
import copy
import random
import shutil
import zipfile
import argparse
from typing import Tuple, List, Optional

import requests
import numpy as np

# Non-interactive backend for server/script execution
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, random_split
from torchvision import transforms, models
from torchvision.datasets import ImageFolder
from sklearn.metrics import classification_report, accuracy_score
from tqdm import tqdm


# ─────────────────────────────────────────────────────────────
# Helper Dataset for Applying Transforms to Subsets
# ─────────────────────────────────────────────────────────────
class TransformedSubset(Dataset):
    """
    Wraps a torch.utils.data.Subset and applies a specific torchvision
    transform to each PIL image upon retrieval.
    Enables distinct augmentation/preprocessing pipelines across splits.
    """
    def __init__(self, subset, transform=None):
        self.subset = subset
        self.transform = transform

    def __getitem__(self, index: int):
        image, label = self.subset[index]
        if self.transform is not None:
            image = self.transform(image)
        return image, label

    def __len__(self) -> int:
        return len(self.subset)


# ─────────────────────────────────────────────────────────────
# Utility Functions
# ─────────────────────────────────────────────────────────────
def set_seed(seed: int = 42):
    """Set random seed for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = False
    torch.backends.cudnn.benchmark = True


def is_valid_imagefolder(path: str) -> bool:
    """Check if directory exists and contains class subdirectories with images."""
    if not os.path.isdir(path):
        return False
    subdirs = [
        os.path.join(path, d)
        for d in os.listdir(path)
        if os.path.isdir(os.path.join(path, d))
    ]
    if len(subdirs) < 2:
        return False

    valid_extensions = (".jpg", ".jpeg", ".png", ".bmp", ".webp")
    for subdir in subdirs[:5]:
        try:
            files = [
                f for f in os.listdir(subdir)
                if f.lower().endswith(valid_extensions)
            ]
            if len(files) > 0:
                return True
        except Exception:
            continue
    return False


def find_existing_dataset(base_dir: str, target_dir: str) -> Optional[str]:
    """Scan candidate locations for an existing PlantVillage dataset."""
    candidates = [
        target_dir,
        os.path.join(base_dir, "dataset", "plantvillage"),
        os.path.join(base_dir, "dataset", "PlantVillage-Dataset-master", "raw", "color"),
        os.path.join(base_dir, "dataset", "PlantVillage", "raw", "color"),
        os.path.join(base_dir, "dataset", "color"),
    ]

    for candidate in candidates:
        if candidate and is_valid_imagefolder(candidate):
            return candidate

    dataset_root = os.path.join(base_dir, "dataset")
    if os.path.isdir(dataset_root):
        for root, dirs, _ in os.walk(dataset_root):
            depth = os.path.relpath(root, dataset_root).count(os.sep)
            if depth <= 3 and is_valid_imagefolder(root):
                return root

    return None


def download_and_extract_plantvillage(dataset_dir: str, base_dir: str) -> str:
    """
    Download and extract the PlantVillage dataset mirror from GitHub
    if not already present locally.
    """
    existing_path = find_existing_dataset(base_dir, dataset_dir)
    if existing_path:
        print(f"✅  Found existing dataset at: {existing_path}")
        return existing_path

    dataset_root = os.path.join(base_dir, "dataset")
    os.makedirs(dataset_root, exist_ok=True)
    zip_path = os.path.join(dataset_root, "plantvillage_master.zip")
    download_url = (
        "https://github.com/spMohanty/PlantVillage-Dataset/archive/refs/heads/master.zip"
    )

    print("\n" + "=" * 65)
    print("📦  PlantVillage Dataset Not Found Locally")
    print("=" * 65)
    print(f"    Target directory: {dataset_dir}")
    print(f"    Downloading from: {download_url}")
    print("    Note: Archive size is ~850MB. Download is resuming or streaming...")

    try:
        response = requests.get(
            download_url,
            stream=True,
            timeout=60,
            headers={"User-Agent": "CropGuardian-ML-Training/1.0"}
        )
        response.raise_for_status()
        total_size = int(response.headers.get("content-length", 0))

        with open(zip_path, "wb") as f, tqdm(
            desc="⬇️   Downloading dataset",
            total=total_size,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
        ) as pbar:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)
                    pbar.update(len(chunk))

        print("\n✅  Download complete! Extracting archive...")
        with zipfile.ZipFile(zip_path, "r") as zf:
            members = zf.infolist()
            with tqdm(desc="📂  Extracting files", total=len(members), unit="files") as pbar:
                for member in members:
                    zf.extract(member, dataset_root)
                    pbar.update(1)

        color_dir = os.path.join(
            dataset_root, "PlantVillage-Dataset-master", "raw", "color"
        )
        if os.path.isdir(color_dir):
            if not os.path.exists(dataset_dir):
                try:
                    shutil.move(color_dir, dataset_dir)
                    print(f"✅  Dataset moved to target: {dataset_dir}")
                    return dataset_dir
                except Exception:
                    return color_dir
            return color_dir

        verified = find_existing_dataset(base_dir, dataset_dir)
        if verified:
            return verified

        raise FileNotFoundError("Extraction succeeded but class folders were not found.")

    except Exception as exc:
        print(f"\n❌  Automatic dataset download/extraction failed: {exc}")
        print("\n💡  Manual Setup Instructions:")
        print("    1. Download PlantVillage from:")
        print("       https://github.com/spMohanty/PlantVillage-Dataset")
        print("       or Kaggle: https://www.kaggle.com/datasets/emmarex/plantdisease")
        print(f"    2. Extract the color class folders into: {dataset_dir}")
        print(f"    3. Re-run: python ml/train_pytorch.py --data-dir \"{dataset_dir}\"\n")
        raise


# ─────────────────────────────────────────────────────────────
# Model Construction & Layer Management
# ─────────────────────────────────────────────────────────────
def build_model(num_classes: int) -> nn.Module:
    """
    Build EfficientNetV2-S with ImageNet pretrained weights
    and a custom classification head.
    """
    print("🏗️   Loading pretrained EfficientNetV2-S backbone...")
    try:
        from torchvision.models import efficientnet_v2_s, EfficientNet_V2_S_Weights
        weights = EfficientNet_V2_S_Weights.DEFAULT
        model = efficientnet_v2_s(weights=weights)
    except (ImportError, AttributeError):
        model = models.efficientnet_v2_s(pretrained=True)

    # In EfficientNetV2-S, classifier is Sequential(Dropout, Linear)
    if isinstance(model.classifier, nn.Sequential):
        in_features = getattr(model.classifier[-1], "in_features", 1280)
    else:
        in_features = getattr(model.classifier, "in_features", 1280)

    # Custom classification head
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.4, inplace=False),
        nn.Linear(in_features, 512),
        nn.ReLU(inplace=False),
        nn.Dropout(p=0.2, inplace=False),
        nn.Linear(512, num_classes),
    )
    return model


def set_phase1_freeze(model: nn.Module):
    """Phase 1: Freeze all base feature extraction layers, train only classifier."""
    for param in model.features.parameters():
        param.requires_grad = False
    for param in model.classifier.parameters():
        param.requires_grad = True


def set_phase2_unfreeze(model: nn.Module, num_blocks: int = 3):
    """Phase 2: Unfreeze the last `num_blocks` stages of EfficientNet base."""
    total_blocks = len(model.features)
    unfreeze_start = max(0, total_blocks - num_blocks)

    for idx, block in enumerate(model.features):
        requires_grad = (idx >= unfreeze_start)
        for param in block.parameters():
            param.requires_grad = requires_grad

    for param in model.classifier.parameters():
        param.requires_grad = True


def count_parameters(model: nn.Module) -> Tuple[int, int]:
    """Return (trainable_params, total_params)."""
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total = sum(p.numel() for p in model.parameters())
    return trainable, total


# ─────────────────────────────────────────────────────────────
# Training and Evaluation Steps
# ─────────────────────────────────────────────────────────────
def train_one_epoch(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    optimizer: optim.Optimizer,
    scaler: Optional[Any],
    device: torch.device,
    use_amp: bool,
    epoch_desc: str = "Train",
    max_batches: Optional[int] = None,
) -> Tuple[float, float, float]:
    """Train for one epoch with mixed precision."""
    model.train()
    running_loss = 0.0
    running_correct = 0
    running_top3 = 0
    total_samples = 0

    pbar = tqdm(loader, desc=epoch_desc, unit="batch", leave=False)
    for batch_idx, (images, labels) in enumerate(pbar):
        if max_batches and batch_idx >= max_batches:
            break
        images = images.to(device, non_blocking=True)
        labels = labels.to(device, non_blocking=True)
        batch_size = images.size(0)

        optimizer.zero_grad(set_to_none=True)

        if use_amp and scaler is not None:
            with torch.amp.autocast(device_type="cuda", dtype=torch.float16):
                outputs = model(images)
                loss = criterion(outputs, labels)
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
        else:
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

        running_loss += loss.item() * batch_size
        _, preds = torch.max(outputs, 1)
        running_correct += torch.sum(preds == labels).item()

        k = min(3, outputs.size(1))
        _, top3 = torch.topk(outputs, k, dim=1)
        running_top3 += torch.sum(top3 == labels.view(-1, 1)).item()

        total_samples += batch_size
        curr_acc = (running_correct / total_samples) * 100
        pbar.set_postfix({"loss": f"{loss.item():.4f}", "acc": f"{curr_acc:.2f}%"})

    epoch_loss = running_loss / total_samples
    epoch_acc = running_correct / total_samples
    epoch_top3 = running_top3 / total_samples
    return epoch_loss, epoch_acc, epoch_top3


def validate_one_epoch(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    device: torch.device,
    use_amp: bool,
    epoch_desc: str = "Val",
    max_batches: Optional[int] = None,
) -> Tuple[float, float, float]:
    """Validate for one epoch with mixed precision."""
    model.eval()
    running_loss = 0.0
    running_correct = 0
    running_top3 = 0
    total_samples = 0

    pbar = tqdm(loader, desc=epoch_desc, unit="batch", leave=False)
    with torch.no_grad():
        for batch_idx, (images, labels) in enumerate(pbar):
            if max_batches and batch_idx >= max_batches:
                break
            images = images.to(device, non_blocking=True)
            labels = labels.to(device, non_blocking=True)
            batch_size = images.size(0)

            if use_amp:
                with torch.amp.autocast(device_type="cuda", dtype=torch.float16):
                    outputs = model(images)
                    loss = criterion(outputs, labels)
            else:
                outputs = model(images)
                loss = criterion(outputs, labels)

            running_loss += loss.item() * batch_size
            _, preds = torch.max(outputs, 1)
            running_correct += torch.sum(preds == labels).item()

            k = min(3, outputs.size(1))
            _, top3 = torch.topk(outputs, k, dim=1)
            running_top3 += torch.sum(top3 == labels.view(-1, 1)).item()

            total_samples += batch_size
            curr_acc = (running_correct / total_samples) * 100
            pbar.set_postfix({"val_loss": f"{loss.item():.4f}", "val_acc": f"{curr_acc:.2f}%"})

    epoch_loss = running_loss / total_samples
    epoch_acc = running_correct / total_samples
    epoch_top3 = running_top3 / total_samples
    return epoch_loss, epoch_acc, epoch_top3


def evaluate_test_set(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    class_names: List[str],
    device: torch.device,
    use_amp: bool,
    plots_dir: str,
    max_batches: Optional[int] = None,
) -> float:
    """Evaluate final model on held-out test set and write classification report."""
    model.eval()
    test_loss = 0.0
    test_correct = 0
    test_top3 = 0
    total_samples = 0
    y_true: List[int] = []
    y_pred: List[int] = []

    print("\n📊  Running final evaluation on held-out test set...")
    with torch.no_grad():
        for batch_idx, (images, labels) in enumerate(tqdm(loader, desc="Test Evaluation", unit="batch")):
            if max_batches and batch_idx >= max_batches:
                break
            images = images.to(device, non_blocking=True)
            labels = labels.to(device, non_blocking=True)
            batch_size = images.size(0)

            if use_amp:
                with torch.amp.autocast(device_type="cuda", dtype=torch.float16):
                    outputs = model(images)
                    loss = criterion(outputs, labels)
            else:
                outputs = model(images)
                loss = criterion(outputs, labels)

            test_loss += loss.item() * batch_size
            _, preds = torch.max(outputs, 1)
            test_correct += torch.sum(preds == labels).item()

            k = min(3, outputs.size(1))
            _, top3 = torch.topk(outputs, k, dim=1)
            test_top3 += torch.sum(top3 == labels.view(-1, 1)).item()

            total_samples += batch_size
            y_true.extend(labels.cpu().tolist())
            y_pred.extend(preds.cpu().tolist())

    acc = test_correct / total_samples
    top3_acc = test_top3 / total_samples
    avg_loss = test_loss / total_samples

    print("\n" + "=" * 60)
    print("  🏆  Final Test Set Evaluation Results")
    print("=" * 60)
    print(f"  Test Accuracy (Top-1): {acc * 100:.2f}%")
    print(f"  Test Accuracy (Top-3): {top3_acc * 100:.2f}%")
    print(f"  Test Loss:             {avg_loss:.4f}")
    print(f"  Total Test Samples:    {total_samples:,}")
    print("=" * 60)

    report = classification_report(
        y_true,
        y_pred,
        target_names=class_names,
        digits=4,
        zero_division=0,
    )
    print("\n📋  Classification Report:\n")
    print(report)

    report_path = os.path.join(plots_dir, "classification_report.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("CropGuardian — PyTorch Model Evaluation Report\n")
        f.write(f"Architecture: EfficientNetV2-S\n")
        f.write(f"Test Accuracy (Top-1): {acc * 100:.2f}%\n")
        f.write(f"Test Accuracy (Top-3): {top3_acc * 100:.2f}%\n")
        f.write(f"Test Loss:             {avg_loss:.4f}\n")
        f.write(f"Total Test Samples:    {total_samples}\n\n")
        f.write(report)
    print(f"📄  Classification report saved → {report_path}")

    return acc


def plot_training_history(history: dict, phase1_epochs: int, save_path: str):
    """Plot and save training/validation accuracy, loss, and learning rate curves."""
    total_epochs = len(history["train_loss"])
    epochs = range(1, total_epochs + 1)

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle(
        "CropGuardian — EfficientNetV2-S (PyTorch) Training History",
        fontsize=14,
        fontweight="bold",
    )

    # 1. Accuracy
    axes[0].plot(
        epochs,
        [a * 100 for a in history["train_acc"]],
        label="Train Acc (Top-1)",
        color="#22c55e",
        linewidth=2,
    )
    axes[0].plot(
        epochs,
        [a * 100 for a in history["val_acc"]],
        label="Val Acc (Top-1)",
        color="#3b82f6",
        linewidth=2,
    )
    axes[0].plot(
        epochs,
        [a * 100 for a in history["val_top3"]],
        label="Val Acc (Top-3)",
        color="#a855f7",
        linestyle=":",
        linewidth=1.5,
    )
    axes[0].axvline(
        x=phase1_epochs + 0.5,
        color="#ef4444",
        linestyle="--",
        alpha=0.7,
        label="Phase 1 → Phase 2",
    )
    axes[0].set_title("Accuracy Over Epochs (%)")
    axes[0].set_xlabel("Epoch")
    axes[0].set_ylabel("Accuracy (%)")
    axes[0].legend(loc="lower right")
    axes[0].grid(True, alpha=0.3)

    # 2. Loss
    axes[1].plot(
        epochs, history["train_loss"], label="Train Loss", color="#f59e0b", linewidth=2
    )
    axes[1].plot(
        epochs, history["val_loss"], label="Val Loss", color="#8b5cf6", linewidth=2
    )
    axes[1].axvline(
        x=phase1_epochs + 0.5,
        color="#ef4444",
        linestyle="--",
        alpha=0.7,
        label="Phase 1 → Phase 2",
    )
    axes[1].set_title("Cross-Entropy Loss Over Epochs")
    axes[1].set_xlabel("Epoch")
    axes[1].set_ylabel("Loss")
    axes[1].legend(loc="upper right")
    axes[1].grid(True, alpha=0.3)

    # 3. Learning Rate
    axes[2].plot(
        epochs, history["lr"], label="Learning Rate", color="#06b6d4", linewidth=2
    )
    axes[2].axvline(
        x=phase1_epochs + 0.5,
        color="#ef4444",
        linestyle="--",
        alpha=0.7,
        label="Phase 1 → Phase 2",
    )
    axes[2].set_title("Learning Rate Schedule")
    axes[2].set_xlabel("Epoch")
    axes[2].set_ylabel("Learning Rate")
    axes[2].set_yscale("log")
    axes[2].legend(loc="upper right")
    axes[2].grid(True, alpha=0.3)

    plt.tight_layout()
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"\n📈  Training plot saved → {save_path}")


# ─────────────────────────────────────────────────────────────
# Main Training Routine
# ─────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="CropGuardian — PyTorch Training Script")
    parser.add_argument(
        "--data-dir",
        type=str,
        default="",
        help="Path to PlantVillage dataset folder containing class subfolders",
    )
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size (default: 32)")
    parser.add_argument("--img-size", type=int, default=224, help="Input image size (default: 224)")
    parser.add_argument("--epochs-phase1", type=int, default=10, help="Phase 1 epochs (head only)")
    parser.add_argument("--epochs-phase2", type=int, default=15, help="Phase 2 epochs (fine-tune)")
    parser.add_argument("--lr1", type=float, default=1e-3, help="Phase 1 learning rate (default: 1e-3)")
    parser.add_argument("--lr2", type=float, default=1e-5, help="Phase 2 learning rate (default: 1e-5)")
    parser.add_argument(
        "--max-batches-per-epoch",
        type=int,
        default=None,
        help="Optional maximum number of batches per epoch for rapid testing without system choke",
    )
    parser.add_argument(
        "--num-workers",
        type=int,
        default=0 if sys.platform == "win32" else 2,
        help="DataLoader worker processes (default: 0 on Windows, 2 on Linux)",
    )
    parser.add_argument("--no-cuda", action="store_true", help="Force CPU execution")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    args = parser.parse_args()

    set_seed(args.seed)

    # Directory Paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_dir = os.path.join(base_dir, "model")
    plots_dir = os.path.join(base_dir, "plots")
    os.makedirs(model_dir, exist_ok=True)
    os.makedirs(plots_dir, exist_ok=True)

    model_save_path = os.path.join(model_dir, "crop_disease_model.pth")
    checkpoint_save_path = os.path.join(model_dir, "crop_disease_checkpoint.pth")
    class_names_path = os.path.join(model_dir, "class_names.json")
    plot_save_path = os.path.join(plots_dir, "training_history.png")

    print("\n" + "=" * 65)
    print("🌿  CropGuardian — PyTorch Model Training Pipeline")
    print("    Architecture: EfficientNetV2-S (Pretrained ImageNet)")
    print("=" * 65)

    # Device & Mixed Precision Setup
    if not args.no_cuda and torch.cuda.is_available():
        device = torch.device("cuda")
        device_name = torch.cuda.get_device_name(0)
        vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024 ** 3)
        print(f"✅  GPU Detected: {device_name} ({vram_gb:.1f} GB VRAM)")
        print(f"    CUDA Version: {torch.version.cuda} | PyTorch: {torch.__version__}")
        print("✅  Mixed Precision Enabled: torch.cuda.amp (float16)")
        use_amp = True
    else:
        device = torch.device("cpu")
        print("⚠️   No GPU detected (or --no-cuda passed). Training on CPU.")
        print("    Tip: Use a CUDA-enabled GPU for dramatically faster training.")
        use_amp = False

    # Dataset Setup
    target_data_dir = args.data_dir.strip()
    if not target_data_dir:
        target_data_dir = os.path.join(base_dir, "dataset", "plantvillage")

    dataset_path = download_and_extract_plantvillage(target_data_dir, base_dir)

    print("\n📦  Loading dataset via torchvision.datasets.ImageFolder...")
    raw_dataset = ImageFolder(dataset_path, transform=None)
    class_names = raw_dataset.classes
    num_classes = len(class_names)
    total_samples = len(raw_dataset)

    print(f"✅  Found {num_classes} classes and {total_samples:,} total images.")

    # Save class names for inference
    with open(class_names_path, "w", encoding="utf-8") as f:
        json.dump(class_names, f, indent=2)
    print(f"✅  Class names saved → {class_names_path}")

    # 70 / 15 / 15 Train / Val / Test Split
    train_size = int(0.70 * total_samples)
    val_size = int(0.15 * total_samples)
    test_size = total_samples - train_size - val_size

    split_generator = torch.Generator().manual_seed(args.seed)
    train_subset, val_subset, test_subset = random_split(
        raw_dataset, [train_size, val_size, test_size], generator=split_generator
    )

    print(f"\n📂  Dataset Splits (70% / 15% / 15%):")
    print(f"    Train: {len(train_subset):,} images")
    print(f"    Val:   {len(val_subset):,} images")
    print(f"    Test:  {len(test_subset):,} images")

    # Data Transforms & Augmentation
    imagenet_mean = [0.485, 0.456, 0.406]
    imagenet_std = [0.229, 0.224, 0.225]

    train_transform = transforms.Compose([
        transforms.RandomResizedCrop(args.img_size, scale=(0.8, 1.0)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomVerticalFlip(p=0.5),
        transforms.RandomRotation(degrees=25),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1),
        transforms.ToTensor(),
        transforms.Normalize(mean=imagenet_mean, std=imagenet_std),
    ])

    val_transform = transforms.Compose([
        transforms.Resize((args.img_size, args.img_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=imagenet_mean, std=imagenet_std),
    ])

    train_dataset = TransformedSubset(train_subset, transform=train_transform)
    val_dataset = TransformedSubset(val_subset, transform=val_transform)
    test_dataset = TransformedSubset(test_subset, transform=val_transform)

    train_loader = DataLoader(
        train_dataset,
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=args.num_workers,
        pin_memory=(device.type == "cuda"),
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
        pin_memory=(device.type == "cuda"),
    )
    test_loader = DataLoader(
        test_dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
        pin_memory=(device.type == "cuda"),
    )

    # Build Model
    model = build_model(num_classes=num_classes)
    model = model.to(device)

    criterion = nn.CrossEntropyLoss()
    if use_amp:
        try:
            scaler = torch.amp.GradScaler("cuda", enabled=True)
        except Exception:
            scaler = torch.cuda.amp.GradScaler(enabled=True)
    else:
        scaler = None

    best_val_acc = 0.0
    best_model_weights = None
    best_epoch = 0

    history = {
        "train_loss": [],
        "val_loss": [],
        "train_acc": [],
        "val_acc": [],
        "val_top3": [],
        "lr": [],
    }

    # ─────────────────────────────────────────────────────────────
    # Phase 1: Train Classification Head Only (Base Frozen)
    # ─────────────────────────────────────────────────────────────
    print("\n" + "=" * 65)
    print("🚀  Phase 1: Training Classification Head (Base Frozen)")
    print(f"    Epochs: {args.epochs_phase1} | Learning Rate: {args.lr1} | Optimizer: Adam")
    print("=" * 65)

    set_phase1_freeze(model)
    trainable_p1, total_p1 = count_parameters(model)
    print(f"    Trainable parameters: {trainable_p1:,} / {total_p1:,} ({trainable_p1 / total_p1 * 100:.2f}%)")

    optimizer1 = optim.Adam(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=args.lr1,
    )
    scheduler1 = optim.lr_scheduler.CosineAnnealingLR(
        optimizer1,
        T_max=args.epochs_phase1,
        eta_min=1e-6,
    )

    for epoch in range(1, args.epochs_phase1 + 1):
        start_t = time.time()
        curr_lr = optimizer1.param_groups[0]["lr"]

        t_loss, t_acc, _ = train_one_epoch(
            model, train_loader, criterion, optimizer1, scaler, device, use_amp,
            epoch_desc=f"Phase 1 [{epoch:2d}/{args.epochs_phase1}] Train",
            max_batches=args.max_batches_per_epoch,
        )
        v_loss, v_acc, v_top3 = validate_one_epoch(
            model, val_loader, criterion, device, use_amp,
            epoch_desc=f"Phase 1 [{epoch:2d}/{args.epochs_phase1}] Val",
            max_batches=args.max_batches_per_epoch,
        )
        scheduler1.step()
        elapsed = time.time() - start_t

        history["train_loss"].append(t_loss)
        history["val_loss"].append(v_loss)
        history["train_acc"].append(t_acc)
        history["val_acc"].append(v_acc)
        history["val_top3"].append(v_top3)
        history["lr"].append(curr_lr)

        is_best = v_acc > best_val_acc
        star = " 🌟 [BEST]" if is_best else ""
        if is_best:
            best_val_acc = v_acc
            best_epoch = epoch
            best_model_weights = copy.deepcopy(model.state_dict())
            torch.save(best_model_weights, model_save_path)

        print(
            f"  Epoch [{epoch:2d}/{args.epochs_phase1}] | "
            f"Train Loss: {t_loss:.4f} | Train Acc: {t_acc * 100:6.2f}% | "
            f"Val Loss: {v_loss:.4f} | Val Acc: {v_acc * 100:6.2f}% | "
            f"LR: {curr_lr:.1e} | {elapsed:4.1f}s{star}"
        )

    print(f"\n✅  Phase 1 Complete. Best Val Acc: {best_val_acc * 100:.2f}%")

    # ─────────────────────────────────────────────────────────────
    # Phase 2: Fine-Tuning Top 3 Blocks of EfficientNet
    # ─────────────────────────────────────────────────────────────
    print("\n" + "=" * 65)
    print("🔬  Phase 2: Fine-Tuning Top 3 Blocks of EfficientNetV2-S")
    print(f"    Epochs: {args.epochs_phase2} | Learning Rate: {args.lr2} | Optimizer: Adam")
    print("=" * 65)

    # Unfreeze top 3 blocks of backbone
    set_phase2_unfreeze(model, num_blocks=3)
    trainable_p2, total_p2 = count_parameters(model)
    print(f"    Trainable parameters: {trainable_p2:,} / {total_p2:,} ({trainable_p2 / total_p2 * 100:.2f}%)")

    optimizer2 = optim.Adam(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=args.lr2,
    )
    scheduler2 = optim.lr_scheduler.CosineAnnealingLR(
        optimizer2,
        T_max=args.epochs_phase2,
        eta_min=1e-7,
    )

    for epoch_idx in range(1, args.epochs_phase2 + 1):
        global_epoch = args.epochs_phase1 + epoch_idx
        start_t = time.time()
        curr_lr = optimizer2.param_groups[0]["lr"]

        t_loss, t_acc, _ = train_one_epoch(
            model, train_loader, criterion, optimizer2, scaler, device, use_amp,
            epoch_desc=f"Phase 2 [{epoch_idx:2d}/{args.epochs_phase2}] Train",
            max_batches=args.max_batches_per_epoch,
        )
        v_loss, v_acc, v_top3 = validate_one_epoch(
            model, val_loader, criterion, device, use_amp,
            epoch_desc=f"Phase 2 [{epoch_idx:2d}/{args.epochs_phase2}] Val",
            max_batches=args.max_batches_per_epoch,
        )
        scheduler2.step()
        elapsed = time.time() - start_t

        history["train_loss"].append(t_loss)
        history["val_loss"].append(v_loss)
        history["train_acc"].append(t_acc)
        history["val_acc"].append(v_acc)
        history["val_top3"].append(v_top3)
        history["lr"].append(curr_lr)

        is_best = v_acc > best_val_acc
        star = " 🌟 [BEST]" if is_best else ""
        if is_best:
            best_val_acc = v_acc
            best_epoch = global_epoch
            best_model_weights = copy.deepcopy(model.state_dict())
            torch.save(best_model_weights, model_save_path)

        print(
            f"  Epoch [{epoch_idx:2d}/{args.epochs_phase2}] (Global {global_epoch:2d}) | "
            f"Train Loss: {t_loss:.4f} | Train Acc: {t_acc * 100:6.2f}% | "
            f"Val Loss: {v_loss:.4f} | Val Acc: {v_acc * 100:6.2f}% | "
            f"LR: {curr_lr:.1e} | {elapsed:4.1f}s{star}"
        )

    print(f"\n✅  Phase 2 Complete. Overall Best Val Acc: {best_val_acc * 100:.2f}% (Epoch {best_epoch})")

    # ─────────────────────────────────────────────────────────────
    # Final Model Saving & Artifacts
    # ─────────────────────────────────────────────────────────────
    if best_model_weights is not None:
        print(f"\n💾  Reloading best weights from epoch {best_epoch} for test evaluation...")
        model.load_state_dict(best_model_weights)
        torch.save(best_model_weights, model_save_path)
        print(f"✅  Best model weights saved → {model_save_path}")

        # Also save comprehensive checkpoint
        torch.save(
            {
                "epoch": best_epoch,
                "model_state_dict": best_model_weights,
                "val_acc": best_val_acc,
                "class_names": class_names,
                "arch": "efficientnet_v2_s",
                "num_classes": num_classes,
                "history": history,
            },
            checkpoint_save_path,
        )
        print(f"✅  Full training checkpoint saved → {checkpoint_save_path}")
    else:
        torch.save(model.state_dict(), model_save_path)

    # Plot and save history curves
    plot_training_history(history, args.epochs_phase1, plot_save_path)

    # Held-out Test Set Evaluation & Classification Report
    test_acc = evaluate_test_set(
        model=model,
        loader=test_loader,
        criterion=criterion,
        class_names=class_names,
        device=device,
        use_amp=use_amp,
        plots_dir=plots_dir,
        max_batches=args.max_batches_per_epoch,
    )

    print("\n" + "=" * 65)
    print("🎉  CropGuardian PyTorch Training Pipeline Complete!")
    print("=" * 65)
    print(f"  Model saved to:       {model_save_path}")
    print(f"  Class names saved to: {class_names_path}")
    print(f"  Plots saved to:       {plot_save_path}")
    print(f"  Best Val Accuracy:    {best_val_acc * 100:.2f}% (Epoch {best_epoch})")
    print(f"  Final Test Accuracy:  {test_acc * 100:.2f}%")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    main()
