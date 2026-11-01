"""
High-accuracy plant disease training script for CropGuardian.
Uses MobileNetV3-Small (lightweight, highly accurate, fast on CPU).
Takes 20 images per class (760 images total across all 38 classes),
ensuring EVERY disease and healthy class is properly represented.
"""

import os
import sys
import json
import time
import random
from collections import defaultdict

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Subset
from torchvision import datasets, transforms, models

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

DATASET_DIR = "ml/dataset/plantvillage"
MODEL_SAVE_PATH = "ml/model/crop_disease_model.pth"
CLASS_NAMES_PATH = "ml/model/class_names.json"
IMG_SIZE = 224
BATCH_SIZE = 16
PER_CLASS_IMAGES = 20  # 16 train, 4 val per class = 760 total images

def build_model(num_classes: int):
    print(f"Loading pretrained MobileNetV3-Small for {num_classes} classes...")
    weights = models.MobileNet_V3_Small_Weights.DEFAULT
    model = models.mobilenet_v3_small(weights=weights)
    
    in_features = model.classifier[3].in_features
    model.classifier[3] = nn.Sequential(
        nn.Dropout(p=0.2, inplace=False),
        nn.Linear(in_features, num_classes)
    )
    return model

def main():
    print("=" * 65)
    print("   CROPGUARDIAN BALANCED RETRAINING (20 IMAGES PER CLASS)")
    print("   Architecture: MobileNetV3-Small (Fast CPU Convergence)")
    print("=" * 65)

    transform_train = transforms.Compose([
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(15),
        transforms.ColorJitter(brightness=0.15, contrast=0.15),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    transform_val = transforms.Compose([
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    print(f"Scanning dataset at {DATASET_DIR}...")
    full_dataset = datasets.ImageFolder(DATASET_DIR)
    class_names = full_dataset.classes
    num_classes = len(class_names)
    print(f"Total classes found: {num_classes}")

    with open(CLASS_NAMES_PATH, "w", encoding="utf-8") as f:
        json.dump(class_names, f, indent=2)

    class_to_indices = defaultdict(list)
    for idx, (_, class_idx) in enumerate(full_dataset.imgs):
        class_to_indices[class_idx].append(idx)

    random.seed(42)
    train_indices = []
    val_indices = []

    for c_idx, c_name in enumerate(class_names):
        imgs = class_to_indices[c_idx]
        random.shuffle(imgs)
        selected = imgs[:PER_CLASS_IMAGES]
        
        t_take = min(16, int(len(selected) * 0.8))
        train_indices.extend(selected[:t_take])
        val_indices.extend(selected[t_take:])

    print(f"Total Train images: {len(train_indices)}")
    print(f"Total Val images:   {len(val_indices)}")

    train_subset = Subset(datasets.ImageFolder(DATASET_DIR, transform=transform_train), train_indices)
    val_subset = Subset(datasets.ImageFolder(DATASET_DIR, transform=transform_val), val_indices)

    train_loader = DataLoader(train_subset, batch_size=BATCH_SIZE, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_subset, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training on device: {device}")

    model = build_model(num_classes).to(device)

    # Phase 1: Train head (2 epochs)
    for param in model.features.parameters():
        param.requires_grad = False

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(filter(lambda p: p.requires_grad, model.parameters()), lr=1e-3, weight_decay=1e-4)

    start_time = time.time()
    print("\n--- Phase 1: Classifier Training (2 Epochs) ---")
    for epoch in range(1, 3):
        model.train()
        r_loss, r_corr, total = 0.0, 0, 0
        for x, y in train_loader:
            x, y = x.to(device), y.to(device)
            optimizer.zero_grad()
            out = model(x)
            loss = criterion(out, y)
            loss.backward()
            optimizer.step()
            r_loss += loss.item() * x.size(0)
            _, preds = torch.max(out, 1)
            r_corr += torch.sum(preds == y.data).item()
            total += x.size(0)

        t_loss = r_loss / total
        t_acc = r_corr / total

        model.eval()
        v_loss, v_corr, v_tot = 0.0, 0, 0
        with torch.no_grad():
            for x, y in val_loader:
                x, y = x.to(device), y.to(device)
                out = model(x)
                loss = criterion(out, y)
                v_loss += loss.item() * x.size(0)
                _, preds = torch.max(out, 1)
                v_corr += torch.sum(preds == y.data).item()
                v_tot += x.size(0)

        vl_loss = v_loss / v_tot
        vl_acc = v_corr / v_tot
        print(f"Epoch {epoch}/2 | Train Loss: {t_loss:.4f} Acc: {t_acc*100:.1f}% | Val Loss: {vl_loss:.4f} Acc: {vl_acc*100:.1f}%")

    # Phase 2: Unfreeze top layers of backbone (4 epochs)
    print("\n--- Phase 2: Fine-Tuning Top Backbone Blocks (4 Epochs) ---")
    for param in model.features[-4:].parameters():
        param.requires_grad = True

    optimizer_ft = torch.optim.AdamW(filter(lambda p: p.requires_grad, model.parameters()), lr=2.5e-4, weight_decay=1e-4)

    best_val_acc = 0.0
    best_state = None

    for epoch in range(1, 5):
        model.train()
        r_loss, r_corr, total = 0.0, 0, 0
        for x, y in train_loader:
            x, y = x.to(device), y.to(device)
            optimizer_ft.zero_grad()
            out = model(x)
            loss = criterion(out, y)
            loss.backward()
            optimizer_ft.step()
            r_loss += loss.item() * x.size(0)
            _, preds = torch.max(out, 1)
            r_corr += torch.sum(preds == y.data).item()
            total += x.size(0)

        t_loss = r_loss / total
        t_acc = r_corr / total

        model.eval()
        v_loss, v_corr, v_tot = 0.0, 0, 0
        with torch.no_grad():
            for x, y in val_loader:
                x, y = x.to(device), y.to(device)
                out = model(x)
                loss = criterion(out, y)
                v_loss += loss.item() * x.size(0)
                _, preds = torch.max(out, 1)
                v_corr += torch.sum(preds == y.data).item()
                v_tot += x.size(0)

        vl_loss = v_loss / v_tot
        vl_acc = v_corr / v_tot
        print(f"Epoch {epoch}/4 (FT) | Train Loss: {t_loss:.4f} Acc: {t_acc*100:.1f}% | Val Loss: {vl_loss:.4f} Acc: {vl_acc*100:.1f}%")
        if vl_acc >= best_val_acc:
            best_val_acc = vl_acc
            best_state = {k: v.cpu() for k, v in model.state_dict().items()}

    os.makedirs(os.path.dirname(MODEL_SAVE_PATH), exist_ok=True)
    torch.save({
        'architecture': 'mobilenet_v3_small',
        'num_classes': num_classes,
        'state_dict': best_state if best_state is not None else {k: v.cpu() for k, v in model.state_dict().items()},
        'val_acc': best_val_acc
    }, MODEL_SAVE_PATH)

    elapsed = time.time() - start_time
    print(f"\nTraining completed in {elapsed:.1f}s ({elapsed/60:.2f} mins)!")
    print(f"Best Val Accuracy: {best_val_acc*100:.1f}%")
    print(f"Saved optimized model weights to: {MODEL_SAVE_PATH}")

if __name__ == "__main__":
    main()
