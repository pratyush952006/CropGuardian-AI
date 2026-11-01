# 🌿 CropGuardian AI 2.0 — Plant Disease Detection & Agronomic Intelligence

CropGuardian AI is a computer vision-based plant disease detection system designed to help farmers identify crop diseases using leaf images and receive actionable treatment recommendations.

The project uses an EfficientNetV2-S deep learning model trained on the PlantVillage dataset to classify plant diseases across multiple crops.

## 🌟 Key Features

- **Plant Disease Detection:** Classifies 38 disease and healthy plant categories across 14 crop types.
- **AI-Powered Diagnosis:** Uses an EfficientNetV2-S convolutional neural network.
- **Interactive Leaf Scanner:** Modern, responsive interface for uploading and scanning leaf images.
- **Camera Capture:** Capture crop images directly using a mobile or desktop camera.
- **Disease Information:** Provides disease descriptions and potential causes.
- **Treatment Recommendations:** Offers organic and chemical treatment guidance with safety precautions.
- **Voice Assistant:** Reads diagnoses and recommendations aloud.
- **Scan History:** Stores recent scans locally for easy access.
- **PDF Reports:** Generates downloadable diagnostic reports.
- **Offline Fallback:** Provides a simulated diagnostic experience when the backend is unavailable.

## 🏗️ Project Architecture

```text
CROPGUARDIAN/
├── ml/
│   ├── train_pytorch.py
│   ├── train.py
│   ├── evaluate.py
│   ├── requirements.txt
│   └── model/
│       ├── crop_disease_model.pth
│       └── class_names.json
├── backend/
│   ├── app.py
│   ├── disease_kb.py
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── server.py
├── requirements.txt
├── Dockerfile
└── README.md
```

## 🚀 Local Setup

### 1. Create and activate the virtual environment

```powershell
python -m venv venv312
.\venv312\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the backend

```bash
python backend/app.py
```

### 4. Open the application

Navigate to:

```text
http://localhost:5000
```

## 🧠 Model Training

To train or fine-tune the PyTorch model:

```bash
python ml/train_pytorch.py --batch-size 32 --epochs-phase1 10 --epochs-phase2 15
```

The training pipeline uses transfer learning and saves the trained model weights and class mappings in the `ml/model/` directory.

## 🧪 Supported Crop Categories

The project covers crops including:

- Tomato
- Potato
- Corn (Maize)
- Bell Pepper
- Apple
- Grape
- Peach
- Cherry
- Orange
- Strawberry
- Blueberry
- Raspberry
- Soybean
- Squash

## 🛡️ Important Disclaimer

CropGuardian AI provides AI-generated disease predictions and treatment suggestions for informational purposes. Users should verify diagnoses and follow local agricultural expert recommendations before applying treatments.

## 📄 License

Please refer to the repository's license information for usage and distribution terms.
