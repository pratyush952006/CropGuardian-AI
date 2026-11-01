import os
import sys
import time
import random
import json
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Subset
from torchvision import datasets, transforms, models
import matplotlib.pyplot as plt

# Windows UTF-8 console output fix
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def build_model(num_classes):
    print("Initializing EfficientNetV2-S backbone...")
    weights = models.EfficientNet_V2_S_Weights.DEFAULT
    model = models.efficientnet_v2_s(weights=weights)
    
    # Freeze early feature layers for fast warm-up
    for param in model.features.parameters():
        param.requires_grad = False
        
    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.3, inplace=False),
        nn.Linear(in_features, 512),
        nn.BatchNorm1d(512),
        nn.ReLU(inplace=False),
        nn.Dropout(p=0.2, inplace=False),
        nn.Linear(512, num_classes)
    )
    return model

def main():
    print("=" * 60)
    print("   CROPGUARDIAN ULTRA-FAST TRAINING (200 IMAGES)")
    print("=" * 60)
    
    dataset_dir = os.path.abspath("ml/dataset/plantvillage")
    if not os.path.exists(dataset_dir):
        # check alternative subfolder if needed
        sub = os.path.join(dataset_dir, "PlantVillage")
        if os.path.exists(sub):
            dataset_dir = sub
        else:
            raise FileNotFoundError(f"Dataset directory not found: {dataset_dir}")
            
    print(f"Loading dataset from: {dataset_dir}")
    
    transform_train = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(15),
        transforms.ColorJitter(brightness=0.1, contrast=0.1),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    transform_val = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    full_dataset = datasets.ImageFolder(dataset_dir)
    class_names = full_dataset.classes
    num_classes = len(class_names)
    print(f"Detected {num_classes} classes and {len(full_dataset)} total images.")
    
    # Save class_names.json
    os.makedirs("ml/model", exist_ok=True)
    os.makedirs("ml/plots", exist_ok=True)
    with open("ml/model/class_names.json", "w", encoding="utf-8") as f:
        json.dump(class_names, f, indent=2)
    print("Saved class names to ml/model/class_names.json")
    
    # Stratified sampling of exactly ~200 images (approx 5-6 per class)
    # Collect indices per class
    class_to_indices = {i: [] for i in range(num_classes)}
    for idx, (_, class_idx) in enumerate(full_dataset.imgs):
        class_to_indices[class_idx].append(idx)
        
    random.seed(42)
    train_indices = []
    val_indices = []
    
    target_train_count = 160
    target_val_count = 40
    per_class_train = max(2, target_train_count // num_classes)
    per_class_val = 1
    
    for c in range(num_classes):
        indices = class_to_indices[c]
        random.shuffle(indices)
        train_take = min(len(indices), per_class_train)
        train_indices.extend(indices[:train_take])
        val_take = min(len(indices) - train_take, per_class_val)
        if val_take > 0:
            val_indices.extend(indices[train_take:train_take + val_take])
            
    # Trim or ensure roughly 200 total images
    total_selected = len(train_indices) + len(val_indices)
    print(f"Selected subset: {len(train_indices)} train images, {len(val_indices)} validation images (Total: {total_selected} images)")
    
    train_subset = Subset(datasets.ImageFolder(dataset_dir, transform=transform_train), train_indices)
    val_subset = Subset(datasets.ImageFolder(dataset_dir, transform=transform_val), val_indices)
    
    train_loader = DataLoader(train_subset, batch_size=16, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_subset, batch_size=16, shuffle=False, num_workers=0)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    model = build_model(num_classes).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(filter(lambda p: p.requires_grad, model.parameters()), lr=1e-3, weight_decay=1e-4)
    
    history = {'train_loss': [], 'train_acc': [], 'val_loss': [], 'val_acc': []}
    
    # 2 Epochs Phase 1 (Frozen Backbone)
    epochs_p1 = 2
    print(f"\n--- Phase 1: Training Classification Head ({epochs_p1} Epochs) ---")
    start_time = time.time()
    for epoch in range(1, epochs_p1 + 1):
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        for x, y in train_loader:
            x, y = x.to(device), y.to(device)
            optimizer.zero_grad()
            out = model(x)
            loss = criterion(out, y)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item() * x.size(0)
            _, preds = torch.max(out, 1)
            correct += torch.sum(preds == y.data).item()
            total += x.size(0)
            
        train_loss = running_loss / total
        train_acc = correct / total
        
        # Validation
        model.eval()
        v_loss = 0.0
        v_correct = 0
        v_total = 0
        with torch.no_grad():
            for x, y in val_loader:
                x, y = x.to(device), y.to(device)
                out = model(x)
                loss = criterion(out, y)
                v_loss += loss.item() * x.size(0)
                _, preds = torch.max(out, 1)
                v_correct += torch.sum(preds == y.data).item()
                v_total += x.size(0)
                
        val_loss = v_loss / v_total if v_total > 0 else 0
        val_acc = v_correct / v_total if v_total > 0 else 0
        
        history['train_loss'].append(train_loss)
        history['train_acc'].append(train_acc)
        history['val_loss'].append(val_loss)
        history['val_acc'].append(val_acc)
        
        print(f"Epoch {epoch}/{epochs_p1} | Train Loss: {train_loss:.4f} Acc: {train_acc*100:.2f}% | Val Loss: {val_loss:.4f} Acc: {val_acc*100:.2f}%")

    # Phase 2: Fine-Tuning top backbone layers (2 Epochs)
    epochs_p2 = 2
    print(f"\n--- Phase 2: Fine-Tuning Top Layers ({epochs_p2} Epochs) ---")
    # Unfreeze last 2 blocks of features
    for param in model.features[-2:].parameters():
        param.requires_grad = True
    optimizer_ft = torch.optim.AdamW(filter(lambda p: p.requires_grad, model.parameters()), lr=1e-4, weight_decay=1e-4)
    
    for epoch in range(1, epochs_p2 + 1):
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        for x, y in train_loader:
            x, y = x.to(device), y.to(device)
            optimizer_ft.zero_grad()
            out = model(x)
            loss = criterion(out, y)
            loss.backward()
            optimizer_ft.step()
            
            running_loss += loss.item() * x.size(0)
            _, preds = torch.max(out, 1)
            correct += torch.sum(preds == y.data).item()
            total += x.size(0)
            
        train_loss = running_loss / total
        train_acc = correct / total
        
        model.eval()
        v_loss = 0.0
        v_correct = 0
        v_total = 0
        with torch.no_grad():
            for x, y in val_loader:
                x, y = x.to(device), y.to(device)
                out = model(x)
                loss = criterion(out, y)
                v_loss += loss.item() * x.size(0)
                _, preds = torch.max(out, 1)
                v_correct += torch.sum(preds == y.data).item()
                v_total += x.size(0)
                
        val_loss = v_loss / v_total if v_total > 0 else 0
        val_acc = v_correct / v_total if v_total > 0 else 0
        
        history['train_loss'].append(train_loss)
        history['train_acc'].append(train_acc)
        history['val_loss'].append(val_loss)
        history['val_acc'].append(val_acc)
        
        print(f"Epoch {epoch}/{epochs_p2} (Fine-Tune) | Train Loss: {train_loss:.4f} Acc: {train_acc*100:.2f}% | Val Loss: {val_loss:.4f} Acc: {val_acc*100:.2f}%")
        
    duration = time.time() - start_time
    print(f"\nTraining completed in {duration:.1f}s ({duration/60:.2f} mins)!")
    
    # Save Model Weights
    save_path = "ml/model/crop_disease_model.pth"
    torch.save(model.state_dict(), save_path)
    print(f"Model saved successfully to: {save_path}")
    
    # Save Loss and Accuracy Plots
    plt.figure(figsize=(10, 4))
    plt.subplot(1, 2, 1)
    plt.plot(history['train_loss'], label='Train Loss', marker='o')
    plt.plot(history['val_loss'], label='Val Loss', marker='s')
    plt.title('Loss Curve')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True)
    
    plt.subplot(1, 2, 2)
    plt.plot(history['train_acc'], label='Train Acc', marker='o')
    plt.plot(history['val_acc'], label='Val Acc', marker='s')
    plt.title('Accuracy Curve')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.grid(True)
    
    plot_path = "ml/plots/training_history.png"
    plt.tight_layout()
    plt.savefig(plot_path)
    plt.close()
    print(f"Plot saved to: {plot_path}")
    print("=" * 60)

if __name__ == "__main__":
    main()
