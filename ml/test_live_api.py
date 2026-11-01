import requests, glob, os, sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

test_cases = [
    ("Tomato Late Blight (diseased)",   "ml/dataset/plantvillage/Tomato___Late_blight"),
    ("Corn Common Rust (diseased)",     "ml/dataset/plantvillage/Corn_(maize)___Common_rust_"),
    ("Apple Scab (diseased)",           "ml/dataset/plantvillage/Apple___Apple_scab"),
    ("Tomato Healthy",                  "ml/dataset/plantvillage/Tomato___healthy"),
    ("Strawberry Leaf Scorch",          "ml/dataset/plantvillage/Strawberry___Leaf_scorch"),
    ("Potato Early Blight (diseased)",  "ml/dataset/plantvillage/Potato___Early_blight"),
    ("Grape Black Rot (diseased)",      "ml/dataset/plantvillage/Grape___Black_rot"),
    ("Corn Healthy",                    "ml/dataset/plantvillage/Corn_(maize)___healthy"),
]

print("--- Live API Disease Detection Test (MobileNetV3-Small) ---")
healthy_correct = 0
disease_correct = 0

for label, folder in test_cases:
    files = glob.glob(folder + "/*.JPG") + glob.glob(folder + "/*.jpg")
    img_path = files[50] if len(files) > 50 else files[-1]
    with open(img_path, "rb") as f:
        resp = requests.post("http://localhost:5000/api/predict",
                             files={"image": ("test.jpg", f, "image/jpeg")})
    d = resp.json()
    p = d["prediction"]
    cn = p["class_name"]
    conf = p["confidence"]
    is_healthy = p["is_healthy"]

    should_healthy = "Healthy" in label
    status = "OK" if (is_healthy == should_healthy) else "WRONG"
    if is_healthy == should_healthy:
        if should_healthy:
            healthy_correct += 1
        else:
            disease_correct += 1

    print(f"  [{status}] {label}")
    print(f"        -> {cn} ({conf}%) | Healthy={is_healthy}")

n_healthy = sum(1 for l, _ in test_cases if "Healthy" in l)
n_disease = len(test_cases) - n_healthy
print(f"\nHealthy detection: {healthy_correct}/{n_healthy}")
print(f"Disease detection: {disease_correct}/{n_disease}")
