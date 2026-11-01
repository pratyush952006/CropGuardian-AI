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

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def build_model(num_classes):
    print(f"Building EfficientNetV2-S model for {num_classes} classes...")
    weights = models.EfficientNet_V2_S_Weights.DEFAULT
    model = models.efficientnet_v2_s(weights=weights)
    
    # Freeze early feature layers for rapid training
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
    print("=" * 65)
    print("   CROPGUARDIAN BALANCED TRAINING (20 IMAGES PER CROP)")
    print("=" * 65)
    
    dataset_dir = os.path.abspath("ml/dataset/plantvillage")
    
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
    print(f"Dataset has {num_classes} classes total.")
    
    # Map each class to its parent crop
    def get_crop_from_class(name):
        n = name.lower()
        if "tomato" in n: return "tomato"
        if "corn" in n: return "corn"
        if "apple" in n: return "apple"
        if "grape" in n: return "grape"
        if "potato" in n: return "potato"
        if "pepper" in n: return "bell pepper"
        if "strawberry" in n: return "strawberry"
        if "peach" in n: return "peach"
        if "cherry" in n: return "cherry"
        if "orange" in n: return "orange"
        if "blueberry" in n: return "blueberry"
        if "raspberry" in n: return "raspberry"
        if "soybean" in n: return "soybean"
        if "squash" in n: return "squash"
        return "other"

    crop_to_class_indices = {}
    for c_idx, c_name in enumerate(class_names):
        crop = get_crop_from_class(c_name)
        crop_to_class_indices.setdefault(crop, []).append(c_idx)

    # Collect indices for each class
    class_to_img_indices = {i: [] for i in range(num_classes)}
    for idx, (_, class_idx) in enumerate(full_dataset.imgs):
        class_to_img_indices[class_idx].append(idx)
        
    random.seed(42)
    train_indices = []
    val_indices = []
    
    TARGET_PER_CROP = 20 # Exactly 20 images total per crop
    
    print("\nAllocating 20 images per crop across healthy & disease conditions:")
    total_crops_count = 0
    for crop, c_indices in sorted(crop_to_class_indices.items()):
        total_crops_count += 1
        # Pool all images for this crop across its diseases & healthy conditions
        crop_all_imgs = []
        for c_idx in c_indices:
            imgs = class_to_img_indices[c_idx]
            random.shuffle(imgs)
            # Take evenly from each condition in this crop
            take_count = max(1, TARGET_PER_CROP // len(c_indices))
            crop_all_imgs.extend(imgs[:take_count])
            
        random.shuffle(crop_all_imgs)
        crop_selected = crop_all_imgs[:TARGET_PER_CROP]
        
        # Split 16 train, 4 val for this crop
        t_take = min(16, int(len(crop_selected) * 0.8))
        train_indices.extend(crop_selected[:t_take])
        val_indices.extend(crop_selected[t_take:])
        print(f" - Crop: {crop.capitalize():<15} -> {len(crop_selected)} images ({len(c_indices)} conditions represented)")

    total_imgs = len(train_indices) + len(val_indices)
    print(f"\nTotal Selected Dataset: {total_imgs} images ({len(train_indices)} Train, {len(val_indices)} Val)")
    
    # Save class_names.json
    with open("ml/model/class_names.json", "w", encoding="utf-8") as f:
        json.dump(class_names, f, indent=2)

    train_subset = Subset(datasets.ImageFolder(dataset_dir, transform=transform_train), train_indices)
    val_subset = Subset(datasets.ImageFolder(dataset_dir, transform=transform_val), val_indices)
    
    train_loader = DataLoader(train_subset, batch_size=16, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_subset, batch_size=16, shuffle=False, num_workers=0)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")
    
    model = build_model(num_classes).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(filter(lambda p: p.requires_grad, model.parameters()), lr=1e-3, weight_decay=1e-4)
    
    history = {'train_loss': [], 'train_acc': [], 'val_loss': [], 'val_acc': []}
    
    # 2 Epochs Phase 1
    print("\n--- Phase 1: Classification Head Tuning (2 Epochs) ---")
    start_time = time.time()
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
        
        # Val
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
        vl_loss = v_loss / v_tot if v_tot > 0 else 0
        vl_acc = v_corr / v_tot if v_tot > 0 else 0
        
        history['train_loss'].append(t_loss)
        history['train_acc'].append(t_acc)
        history['val_loss'].append(vl_loss)
        history['val_acc'].append(vl_acc)
        print(f"Epoch {epoch}/2 | Train Loss: {t_loss:.4f} Acc: {t_acc*100:.1f}% | Val Loss: {vl_loss:.4f} Acc: {vl_acc*100:.1f}%")

    # Phase 2: Fine-Tuning Top Layers
    print("\n--- Phase 2: Fine-Tuning Top Backbone Blocks (2 Epochs) ---")
    for param in model.features[-2:].parameters():
        param.requires_grad = True
    optimizer_ft = torch.optim.AdamW(filter(lambda p: p.requires_grad, model.parameters()), lr=1e-4, weight_decay=1e-4)

    for epoch in range(1, 3):
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
        vl_loss = v_loss / v_tot if v_tot > 0 else 0
        vl_acc = v_corr / v_tot if v_tot > 0 else 0
        
        history['train_loss'].append(t_loss)
        history['train_acc'].append(t_acc)
        history['val_loss'].append(vl_loss)
        history['val_acc'].append(vl_acc)
        print(f"Epoch {epoch}/2 (FT) | Train Loss: {t_loss:.4f} Acc: {t_acc*100:.1f}% | Val Loss: {vl_loss:.4f} Acc: {vl_acc*100:.1f}%")

    duration = time.time() - start_time
    print(f"\nTraining finished in {duration:.1f}s ({duration/60:.2f} mins)!")
    
    save_path = "ml/model/crop_disease_model.pth"
    torch.save(model.state_dict(), save_path)
    print(f"Saved model to: {save_path}")
    
    plt.figure(figsize=(10, 4))
    plt.subplot(1, 2, 1)
    plt.plot(history['train_loss'], label='Train Loss', marker='o')
    plt.plot(history['val_loss'], label='Val Loss', marker='s')
    plt.title('Loss Curve (20 images/crop)')
    plt.xlabel('Epoch')
    plt.legend()
    plt.grid(True)
    
    plt.subplot(1, 2, 2)
    plt.plot(history['train_acc'], label='Train Acc', marker='o')
    plt.plot(history['val_acc'], label='Val Acc', marker='s')
    plt.title('Accuracy Curve (20 images/crop)')
    plt.xlabel('Epoch')
    plt.legend()
    plt.grid(True)
    
    plot_path = "ml/plots/training_history.png"
    plt.tight_layout()
    plt.savefig(plot_path)
    plt.close()
    print(f"Saved plot to: {plot_path}")
    print("=" * 65)

if __name__ == "__main__":
    main()
