"""
CropGuardian — Standalone Server (Zero Dependencies)
Uses only Python's built-in libraries — no pip install needed!

Serves:
  - Static frontend files (HTML/CSS/JS)
  - /api/predict   — Demo disease predictions
  - /api/status    — Server status
  - /api/health    — Health check
  - /api/diseases  — Disease list

Usage:
    python server.py

Then open: http://localhost:5000
"""

import os
import sys
import json
import random
import io
import mimetypes
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
PORT         = 5000

# ─────────────────────────────────────────────
# Demo Disease Data (realistic scenarios)
# ─────────────────────────────────────────────
DEMO_SCENARIOS = [
    {
        "class_name": "Tomato___Late_blight",
        "prediction": {
            "class_name": "Tomato___Late_blight",
            "disease": "Late Blight",
            "crop": "Tomato",
            "confidence": 96.47,
            "confidence_raw": 0.9647,
            "is_healthy": False,
            "severity": "Critical",
            "severity_color": "#dc2626",
            "pathogen": "Phytophthora infestans (Oomycete)",
            "description": "Late blight is one of the most devastating tomato diseases. Under favorable conditions, it can destroy an entire crop within a week. The same pathogen caused the Irish Famine of 1845.",
            "symptoms": [
                "Large, irregular, water-soaked greenish-gray spots on leaves",
                "White mold visible on undersides of leaves in humid conditions",
                "Rapidly expanding lesions killing leaves and stems",
                "Large, firm, dark-brown irregular blotches on fruit",
                "Greasy/oily appearance to infected tissue"
            ],
            "causes": [
                "Phytophthora infestans oomycete thrives in cool (10–20°C), wet conditions",
                "Infected transplants or nearby potato plants",
                "Wind-dispersed sporangia spreading the disease",
                "High humidity (>90%) promotes rapid spread"
            ],
            "treatment": {
                "organic": [
                    "Apply copper-based fungicides (Bordeaux mixture) immediately at first sight",
                    "Remove and bag infected plants — do NOT compost",
                    "Apply copper hydroxide spray every 5–7 days",
                    "Ensure plants are not overcrowded for airflow"
                ],
                "chemical": [
                    "Metalaxyl + Mancozeb (Ridomil Gold MZ) — most effective systemic option",
                    "Cymoxanil + Mancozeb (Curzate M8) — systemic + contact protection",
                    "Dimethomorph (Acrobat) — excellent curative action",
                    "Fluopicolide + Propamocarb (Infinito) — premium dual-mode protection"
                ]
            },
            "prevention": [
                "Avoid planting near potato fields",
                "Use resistant varieties with Ph-3 resistance gene",
                "Apply preventive fungicide sprays before and during rainy weather",
                "Do not irrigate at night — leaves must stay dry",
                "Remove and destroy volunteer tomato/potato plants"
            ]
        },
        "top3": [
            {"class_name": "Tomato___Late_blight", "disease": "Late Blight", "crop": "Tomato", "confidence": 96.47},
            {"class_name": "Potato___Late_blight", "disease": "Late Blight", "crop": "Potato", "confidence": 2.81},
            {"class_name": "Tomato___Early_blight", "disease": "Early Blight", "crop": "Tomato", "confidence": 0.72}
        ]
    },
    {
        "class_name": "Tomato___Early_blight",
        "prediction": {
            "class_name": "Tomato___Early_blight",
            "disease": "Early Blight",
            "crop": "Tomato",
            "confidence": 92.31,
            "confidence_raw": 0.9231,
            "is_healthy": False,
            "severity": "Medium",
            "severity_color": "#f59e0b",
            "pathogen": "Alternaria solani (Fungus)",
            "description": "Early blight is the most common foliar disease of tomato worldwide, causing premature defoliation and reduced fruit quality and yield.",
            "symptoms": [
                "Dark brown spots with concentric rings (bull's-eye pattern)",
                "Yellow chlorotic halo surrounding lesions",
                "Lesions first appear on older lower leaves",
                "Defoliation progressing upward through the plant",
                "Dark, sunken lesions on stem and fruit near calyx"
            ],
            "causes": [
                "Alternaria solani fungal spores surviving in soil and infected debris",
                "Warm (24–29°C), humid conditions with wet foliage",
                "Plant stress (drought, nutrient deficiency) triggers outbreak",
                "Splashing rain or overhead irrigation spreads spores"
            ],
            "treatment": {
                "organic": [
                    "Remove infected lower leaves immediately and dispose of them",
                    "Apply copper-based fungicide spray every 7–10 days",
                    "Neem oil + liquid copper combined spray as preventive",
                    "Ensure adequate calcium and potassium nutrition"
                ],
                "chemical": [
                    "Mancozeb (75 WP) at 2g/L water — apply every 7 days",
                    "Chlorothalonil — broad-spectrum protective fungicide",
                    "Azoxystrobin — systemic + protective dual action",
                    "Difenoconazole — DMI fungicide with excellent curative results"
                ]
            },
            "prevention": [
                "Use certified disease-free transplants",
                "Mulch around plants to prevent soil splash onto leaves",
                "Stake/cage plants to improve air circulation",
                "Practice 3-year crop rotation avoiding tomato/potato/pepper",
                "Remove and destroy all crop debris after harvest"
            ]
        },
        "top3": [
            {"class_name": "Tomato___Early_blight", "disease": "Early Blight", "crop": "Tomato", "confidence": 92.31},
            {"class_name": "Potato___Early_blight", "disease": "Early Blight", "crop": "Potato", "confidence": 5.41},
            {"class_name": "Tomato___Septoria_leaf_spot", "disease": "Septoria Leaf Spot", "crop": "Tomato", "confidence": 2.28}
        ]
    },
    {
        "class_name": "Potato___Late_blight",
        "prediction": {
            "class_name": "Potato___Late_blight",
            "disease": "Late Blight",
            "crop": "Potato",
            "confidence": 98.12,
            "confidence_raw": 0.9812,
            "is_healthy": False,
            "severity": "Critical",
            "severity_color": "#dc2626",
            "pathogen": "Phytophthora infestans (Oomycete)",
            "description": "Late blight is the most devastating potato disease in history, responsible for the Irish Famine. It can destroy an entire field in 7–10 days under ideal conditions.",
            "symptoms": [
                "Water-soaked, dark green to brown lesions on leaves",
                "White cottony mold on undersides of leaves in humid conditions",
                "Lesions rapidly expand to kill entire leaves and stems",
                "Dark, firm rot on tubers with pink-red coloration beneath skin",
                "Foul smell from infected tubers"
            ],
            "causes": [
                "Phytophthora infestans oomycete in cool (10–20°C), wet conditions",
                "Infected seed tubers introduce pathogen to new fields",
                "Airborne sporangia spread up to 20km during rain events",
                "Cull piles and volunteer plants act as inoculum sources"
            ],
            "treatment": {
                "organic": [
                    "Apply copper-based fungicides immediately upon first symptom detection",
                    "Remove and destroy infected plant material (do NOT compost)",
                    "Bordeaux mixture (copper sulfate + lime) as protective spray",
                    "Hill up soil around tubers to prevent spore washdown"
                ],
                "chemical": [
                    "Metalaxyl + Mancozeb (Ridomil Gold MZ) — gold standard treatment",
                    "Cymoxanil + Mancozeb (Curzate) — fast-acting systemic + contact",
                    "Dimethomorph — excellent curative action within 24 hours",
                    "Propamocarb — specific anti-oomycete for resistant strains"
                ]
            },
            "prevention": [
                "Use only certified disease-free seed potatoes",
                "Plant resistant potato varieties (e.g., Sarpo Mira, Defender)",
                "Apply preventive fungicides based on local blight forecasting service",
                "Destroy all infected crop debris and cull piles immediately",
                "Harvest on dry days and cure tubers before storage at 10–15°C"
            ]
        },
        "top3": [
            {"class_name": "Potato___Late_blight", "disease": "Late Blight", "crop": "Potato", "confidence": 98.12},
            {"class_name": "Tomato___Late_blight", "disease": "Late Blight", "crop": "Tomato", "confidence": 1.48},
            {"class_name": "Potato___Early_blight", "disease": "Early Blight", "crop": "Potato", "confidence": 0.40}
        ]
    },
    {
        "class_name": "Corn_(maize)___Northern_Leaf_Blight",
        "prediction": {
            "class_name": "Corn_(maize)___Northern_Leaf_Blight",
            "disease": "Northern Corn Leaf Blight",
            "crop": "Corn (Maize)",
            "confidence": 93.18,
            "confidence_raw": 0.9318,
            "is_healthy": False,
            "severity": "High",
            "severity_color": "#ef4444",
            "pathogen": "Exserohilum turcicum (Fungus)",
            "description": "Northern corn leaf blight (NCLB) is a major foliar disease that can cause 30–50% yield loss in susceptible hybrids when infection occurs early in the season.",
            "symptoms": [
                "Large, cigar-shaped lesions 2.5–15 cm long on leaves",
                "Tan to grayish-green lesions with distinctive wavy margins",
                "Dark olive-green sporulation visible inside lesions",
                "Lesions coalesce to blight entire leaves in severe cases",
                "Premature death of leaves reducing grain fill"
            ],
            "causes": [
                "Fungal spores from infected crop residue in soil",
                "Moderate temperatures (18–27°C) combined with frequent rainfall",
                "Extended periods of leaf wetness exceeding 6 hours",
                "Susceptible corn hybrids without Ht resistance genes"
            ],
            "treatment": {
                "organic": [
                    "Practice crop rotation with soybean or wheat for 2 years",
                    "Deep tillage to bury infected crop residue below soil surface",
                    "Apply Bacillus subtilis-based biofungicides (Serenade)",
                    "Improve field drainage to reduce periods of leaf wetness"
                ],
                "chemical": [
                    "Azoxystrobin + Propiconazole (Quilt Xcel) — most widely recommended",
                    "Pyraclostrobin (Headline) — excellent protective strobilurin",
                    "Tebuconazole — DMI fungicide with good curative activity",
                    "Picoxystrobin + Cyproconazole — dual-mode premium protection"
                ]
            },
            "prevention": [
                "Select NCLB-resistant corn hybrids carrying the Ht1 or HtN resistance gene",
                "Practice 2-year crop rotation with non-host crops",
                "Apply fungicide preventively at silking stage (VT/R1) in high-risk areas",
                "Scout fields from V6 stage onward for early lesion detection",
                "Avoid late planting dates when conditions favor disease"
            ]
        },
        "top3": [
            {"class_name": "Corn_(maize)___Northern_Leaf_Blight", "disease": "Northern Leaf Blight", "crop": "Corn", "confidence": 93.18},
            {"class_name": "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot", "disease": "Gray Leaf Spot", "crop": "Corn", "confidence": 5.12},
            {"class_name": "Corn_(maize)___Common_rust_", "disease": "Common Rust", "crop": "Corn", "confidence": 1.70}
        ]
    },
    {
        "class_name": "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
        "prediction": {
            "class_name": "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
            "disease": "Tomato Yellow Leaf Curl Virus (TYLCV)",
            "crop": "Tomato",
            "confidence": 95.34,
            "confidence_raw": 0.9534,
            "is_healthy": False,
            "severity": "Critical",
            "severity_color": "#dc2626",
            "pathogen": "Begomovirus (Virus) — transmitted by silverleaf whitefly",
            "description": "TYLCV is one of the most devastating tomato viruses worldwide, capable of causing up to 100% yield loss in susceptible varieties. There is no cure; management focuses on vector control and resistant varieties.",
            "symptoms": [
                "Severe upward curling and cupping of leaves (spoon-shaped)",
                "Interveinal yellowing of young leaves at shoot tips",
                "Severely stunted plant growth and bushy appearance",
                "Flower drop resulting in very few or no fruit",
                "Purplish discoloration of veins on undersides of leaves"
            ],
            "causes": [
                "Virus transmitted exclusively by silverleaf whitefly (Bemisia tabaci)",
                "Infected seedlings or transplants introduced into the field",
                "High whitefly populations in warm, dry conditions",
                "No mechanical or seed transmission of this virus"
            ],
            "treatment": {
                "organic": [
                    "Remove and immediately destroy infected plants to prevent spread",
                    "Install yellow sticky traps to monitor and reduce whitefly populations",
                    "Use reflective silver/aluminum mulches to repel whiteflies",
                    "Spray neem oil or insecticidal soap every 5 days for whitefly control"
                ],
                "chemical": [
                    "Imidacloprid — systemic neonicotinoid, apply at transplanting as soil drench",
                    "Thiamethoxam — highly effective neonicotinoid for whitefly management",
                    "Spirotetramat (Movento) — phloem-mobile for nymph control",
                    "Pymetrozine (Chess) — selective, inhibits whitefly feeding behavior"
                ]
            },
            "prevention": [
                "Plant TYLCV-resistant tomato varieties (e.g., Tylka, Shanty, Hazera series)",
                "Apply imidacloprid soil drench at transplanting for 4–6 weeks protection",
                "Use 40-mesh insect-proof netting in nurseries to raise virus-free seedlings",
                "Eliminate weed hosts of whitefly (parthenium, amaranthus) around field",
                "Destroy infected plants before whitefly populations can transmit virus"
            ]
        },
        "top3": [
            {"class_name": "Tomato___Tomato_Yellow_Leaf_Curl_Virus", "disease": "Yellow Leaf Curl Virus", "crop": "Tomato", "confidence": 95.34},
            {"class_name": "Tomato___Tomato_mosaic_virus", "disease": "Mosaic Virus", "crop": "Tomato", "confidence": 3.31},
            {"class_name": "Tomato___Bacterial_spot", "disease": "Bacterial Spot", "crop": "Tomato", "confidence": 1.35}
        ]
    },
    {
        "class_name": "Apple___Apple_scab",
        "prediction": {
            "class_name": "Apple___Apple_scab",
            "disease": "Apple Scab",
            "crop": "Apple",
            "confidence": 97.02,
            "confidence_raw": 0.9702,
            "is_healthy": False,
            "severity": "Medium",
            "severity_color": "#f59e0b",
            "pathogen": "Venturia inaequalis (Fungus)",
            "description": "Apple scab is one of the most common and economically important diseases of apple trees globally, capable of rendering fruit unmarketable.",
            "symptoms": [
                "Olive-green to brown velvety spots on upper leaf surfaces",
                "Yellowing and premature leaf drop in severe infections",
                "Dark scabby lesions on fruit surface causing cracking",
                "Deformed, small, and cracked fruit with poor marketability",
                "Lesions on young shoots appearing as blisters"
            ],
            "causes": [
                "Venturia inaequalis fungal spores released during wet spring weather",
                "Infected fallen leaves from previous season as primary inoculum",
                "High humidity and optimal temperatures of 16–24°C",
                "10+ hours of continuous leaf wetness needed for infection"
            ],
            "treatment": {
                "organic": [
                    "Apply sulfur-based fungicide every 7–10 days during wet periods",
                    "Use copper-based sprays (Bordeaux mixture) at bud break stage",
                    "Remove and destroy infected leaves and mummified fruit",
                    "Apply neem oil spray every 2 weeks as preventive measure"
                ],
                "chemical": [
                    "Captan (50 WP) at 2.5g/L water — primary protective fungicide",
                    "Mancozeb (75 WP) at 2g/L water — excellent contact protection",
                    "Myclobutanil (Rally) — systemic DMI fungicide, curative up to 96h post-infection",
                    "Trifloxystrobin + Tebuconazole — broad-spectrum premium protection"
                ]
            },
            "prevention": [
                "Plant scab-resistant apple varieties (Liberty, Redfree, Enterprise)",
                "Ensure good air circulation through annual pruning",
                "Rake and destroy fallen leaves in autumn to eliminate inoculum",
                "Apply protective fungicide program starting at green tip stage",
                "Use drip irrigation instead of overhead sprinklers"
            ]
        },
        "top3": [
            {"class_name": "Apple___Apple_scab", "disease": "Apple Scab", "crop": "Apple", "confidence": 97.02},
            {"class_name": "Apple___Black_rot", "disease": "Black Rot", "crop": "Apple", "confidence": 2.23},
            {"class_name": "Apple___Cedar_apple_rust", "disease": "Cedar Apple Rust", "crop": "Apple", "confidence": 0.75}
        ]
    },
    {
        "class_name": "Tomato___Spider_mites Two-spotted_spider_mite",
        "prediction": {
            "class_name": "Tomato___Spider_mites Two-spotted_spider_mite",
            "disease": "Two-Spotted Spider Mite Infestation",
            "crop": "Tomato",
            "confidence": 88.76,
            "confidence_raw": 0.8876,
            "is_healthy": False,
            "severity": "High",
            "severity_color": "#ef4444",
            "pathogen": "Tetranychus urticae (Pest — Arachnid Mite)",
            "description": "Two-spotted spider mites are tiny arachnid pests (not insects) that rapidly colonize tomato plants in hot, dry weather, causing severe damage through sap extraction.",
            "symptoms": [
                "Fine stippling (tiny yellow pinpoint dots) on upper leaf surface",
                "Bronze or silvery discoloration and shimmer on leaves",
                "Fine silk webbing on leaf undersides and between leaves",
                "Leaves turn yellow-brown then die and drop prematurely",
                "Tiny mites visible with 10× hand lens on leaf undersides"
            ],
            "causes": [
                "Hot, dry weather above 28°C with low humidity accelerates breeding",
                "Overuse of broad-spectrum insecticides killing natural predatory mites",
                "Dusty field conditions and drought stress on plants",
                "Mites can complete a life cycle in just 5–7 days in hot weather"
            ],
            "treatment": {
                "organic": [
                    "Strong blast of water to physically knock mites off leaves",
                    "Apply neem oil or insecticidal soap spray every 5–7 days",
                    "Introduce predatory mites (Phytoseiulus persimilis or Neoseiulus californicus)",
                    "Apply sulfur-based acaricide in cool morning hours"
                ],
                "chemical": [
                    "Abamectin (Agri-Mek) — most effective, disrupts mite nervous system",
                    "Bifenazate (Floramite) — selective miticide, rapid knockdown",
                    "Hexythiazox — ovicidal (kills eggs), excellent for resistance management",
                    "Spiromesifen (Oberon) — long residual activity, effective on all stages"
                ]
            },
            "prevention": [
                "Scout plants weekly using a 10× hand lens from the start of summer",
                "Avoid excessive nitrogen fertilization which promotes soft mite-susceptible growth",
                "Maintain adequate irrigation (mites prefer drought-stressed plants)",
                "Conserve natural enemies by avoiding broad-spectrum insecticide sprays",
                "Rotate miticide chemical classes to prevent resistance development"
            ]
        },
        "top3": [
            {"class_name": "Tomato___Spider_mites Two-spotted_spider_mite", "disease": "Two-Spotted Spider Mite", "crop": "Tomato", "confidence": 88.76},
            {"class_name": "Tomato___Leaf_Mold", "disease": "Leaf Mold", "crop": "Tomato", "confidence": 7.24},
            {"class_name": "Tomato___Target_Spot", "disease": "Target Spot", "crop": "Tomato", "confidence": 4.00}
        ]
    },
    {
        "class_name": "Tomato___healthy",
        "prediction": {
            "class_name": "Tomato___healthy",
            "disease": "Healthy",
            "crop": "Tomato",
            "confidence": 98.87,
            "confidence_raw": 0.9887,
            "is_healthy": True,
            "severity": "None",
            "severity_color": "#22c55e",
            "pathogen": "None",
            "description": "Excellent news! Your tomato plant appears completely healthy with no signs of disease, pest damage, or nutritional deficiency. Continue your current management practices.",
            "symptoms": [],
            "causes": [],
            "treatment": {
                "organic": [],
                "chemical": []
            },
            "prevention": [
                "Continue regular watering at soil level (drip irrigation preferred)",
                "Stake or cage plants for support and better air circulation",
                "Mulch with straw or compost to retain moisture and prevent soil splash",
                "Monitor weekly for early signs of pests or disease",
                "Apply balanced fertilizer (N-P-K) every 2–3 weeks during fruit set"
            ]
        },
        "top3": [
            {"class_name": "Tomato___healthy", "disease": "Healthy", "crop": "Tomato", "confidence": 98.87},
            {"class_name": "Tomato___Early_blight", "disease": "Early Blight", "crop": "Tomato", "confidence": 0.67},
            {"class_name": "Tomato___Septoria_leaf_spot", "disease": "Septoria Leaf Spot", "crop": "Tomato", "confidence": 0.46}
        ]
    },
    {
        "class_name": "Grape___Black_rot",
        "prediction": {
            "class_name": "Grape___Black_rot",
            "disease": "Black Rot",
            "crop": "Grape",
            "confidence": 94.45,
            "confidence_raw": 0.9445,
            "is_healthy": False,
            "severity": "High",
            "severity_color": "#ef4444",
            "pathogen": "Guignardia bidwellii (Fungus)",
            "description": "Black rot is the most destructive grape disease in humid climates, capable of destroying 80% of the crop in a single season under favorable conditions.",
            "symptoms": [
                "Circular brown spots with dark borders on leaves (reddish-brown centers)",
                "Tan lesions containing black pycnidia (tiny black dots = fruiting bodies)",
                "Young green berries turning brown, then shriveling into black mummies",
                "Infected shoots with dark elongated cankers",
                "Mummified berries often remaining attached to cluster"
            ],
            "causes": [
                "Guignardia bidwellii fungal spores from overwintering mummified berries",
                "Warm (20–30°C) wet weather during the growing season",
                "Spore release and spread triggered by rainfall events",
                "Mummified berries in clusters and on ground are primary inoculum"
            ],
            "treatment": {
                "organic": [
                    "Remove and destroy ALL mummified berries and infected debris",
                    "Apply lime sulfur sprays during the dormant season",
                    "Use copper-based fungicides from bud break through fruit set",
                    "Apply Bacillus subtilis biological control (Serenade) as supplement"
                ],
                "chemical": [
                    "Myclobutanil (Rally) — highly effective DMI fungicide for black rot",
                    "Mancozeb — excellent protective contact fungicide",
                    "Tebuconazole — systemic with strong curative activity",
                    "Captan + Myclobutanil — combined contact + systemic protection"
                ]
            },
            "prevention": [
                "Remove ALL mummified fruit clusters before bud break each spring",
                "Prune for open canopy to maximize air circulation and sun penetration",
                "Apply first fungicide spray at bud break (1–2 inch shoot stage)",
                "Continue sprays every 7–10 days through 4 weeks after fruit set",
                "Train vines on trellis system to keep fruit off ground"
            ]
        },
        "top3": [
            {"class_name": "Grape___Black_rot", "disease": "Black Rot", "crop": "Grape", "confidence": 94.45},
            {"class_name": "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)", "disease": "Leaf Blight", "crop": "Grape", "confidence": 3.81},
            {"class_name": "Grape___Esca_(Black_Measles)", "disease": "Esca (Black Measles)", "crop": "Grape", "confidence": 1.74}
        ]
    },
    {
        "class_name": "Corn_(maize)___Common_rust_",
        "prediction": {
            "class_name": "Corn_(maize)___Common_rust_",
            "disease": "Common Rust",
            "crop": "Corn (Maize)",
            "confidence": 91.23,
            "confidence_raw": 0.9123,
            "is_healthy": False,
            "severity": "Medium",
            "severity_color": "#f59e0b",
            "pathogen": "Puccinia sorghi (Fungus — Obligate Rust)",
            "description": "Common rust is a widespread and easily recognizable corn disease. While often manageable, early and severe infection can significantly reduce photosynthetic capacity and grain yield.",
            "symptoms": [
                "Small, circular to elongated brick-red to cinnamon-colored pustules on both leaf surfaces",
                "Pustules later turn dark brown to black as they mature",
                "Chlorotic (yellow) halos surrounding pustule clusters",
                "Severe infection causes premature leaf death and weakened stalks",
                "Pustules rupture easily releasing powdery rusty-orange spores"
            ],
            "causes": [
                "Wind-blown urediniospores dispersed long distances from alternate hosts",
                "Cool temperatures (16–23°C) combined with high relative humidity",
                "Susceptible corn hybrids lacking rust resistance genes",
                "Dew periods exceeding 6 hours favor spore germination and infection"
            ],
            "treatment": {
                "organic": [
                    "Apply sulfur-based fungicides at first sign of rust pustules",
                    "Use neem oil spray as a preventive deterrent measure",
                    "Remove and dispose of severely infected leaves to slow spread",
                    "Ensure good plant nutrition — potassium improves rust tolerance"
                ],
                "chemical": [
                    "Trifloxystrobin — most effective strobilurin for corn rust",
                    "Propiconazole (Tilt) — DMI fungicide with good curative activity",
                    "Azoxystrobin + Propiconazole (Quilt Xcel) — dual-mode protection",
                    "Mancozeb — economical protective option for early intervention"
                ]
            },
            "prevention": [
                "Plant rust-resistant corn hybrids with Rp (rust resistance) genes",
                "Early planting to avoid peak spore dispersal period",
                "Monitor fields regularly from V8 growth stage onward",
                "Apply fungicide if more than 50% of plants show rust pustules before silking",
                "Maintain balanced soil fertility — avoid excessive nitrogen"
            ]
        },
        "top3": [
            {"class_name": "Corn_(maize)___Common_rust_", "disease": "Common Rust", "crop": "Corn", "confidence": 91.23},
            {"class_name": "Corn_(maize)___Northern_Leaf_Blight", "disease": "Northern Leaf Blight", "crop": "Corn", "confidence": 6.21},
            {"class_name": "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot", "disease": "Gray Leaf Spot", "crop": "Corn", "confidence": 2.56}
        ]
    }
]

scenario_index = 0

ALL_DISEASES = {
    "Tomato___Late_blight": {"disease": "Late Blight", "crop": "Tomato", "severity": "Critical", "pathogen": "Phytophthora infestans"},
    "Tomato___Early_blight": {"disease": "Early Blight", "crop": "Tomato", "severity": "Medium", "pathogen": "Alternaria solani"},
    "Tomato___healthy": {"disease": "Healthy", "crop": "Tomato", "severity": "None", "pathogen": "None"},
    "Potato___Late_blight": {"disease": "Late Blight", "crop": "Potato", "severity": "Critical", "pathogen": "Phytophthora infestans"},
    "Potato___Early_blight": {"disease": "Early Blight", "crop": "Potato", "severity": "Medium", "pathogen": "Alternaria solani"},
    "Potato___healthy": {"disease": "Healthy", "crop": "Potato", "severity": "None", "pathogen": "None"},
    "Corn_(maize)___Common_rust_": {"disease": "Common Rust", "crop": "Corn", "severity": "Medium", "pathogen": "Puccinia sorghi"},
    "Corn_(maize)___Northern_Leaf_Blight": {"disease": "Northern Leaf Blight", "crop": "Corn", "severity": "High", "pathogen": "Exserohilum turcicum"},
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": {"disease": "Gray Leaf Spot", "crop": "Corn", "severity": "High", "pathogen": "Cercospora zeae-maydis"},
    "Corn_(maize)___healthy": {"disease": "Healthy", "crop": "Corn", "severity": "None", "pathogen": "None"},
    "Apple___Apple_scab": {"disease": "Apple Scab", "crop": "Apple", "severity": "Medium", "pathogen": "Venturia inaequalis"},
    "Apple___Black_rot": {"disease": "Black Rot", "crop": "Apple", "severity": "High", "pathogen": "Botryosphaeria obtusa"},
    "Apple___Cedar_apple_rust": {"disease": "Cedar Apple Rust", "crop": "Apple", "severity": "Medium", "pathogen": "Gymnosporangium juniperi"},
    "Apple___healthy": {"disease": "Healthy", "crop": "Apple", "severity": "None", "pathogen": "None"},
    "Grape___Black_rot": {"disease": "Black Rot", "crop": "Grape", "severity": "High", "pathogen": "Guignardia bidwellii"},
    "Grape___Esca_(Black_Measles)": {"disease": "Esca (Black Measles)", "crop": "Grape", "severity": "High", "pathogen": "Phaeomoniella chlamydospora"},
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": {"disease": "Leaf Blight", "crop": "Grape", "severity": "Medium", "pathogen": "Isariopsis clavispora"},
    "Grape___healthy": {"disease": "Healthy", "crop": "Grape", "severity": "None", "pathogen": "None"},
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": {"disease": "Yellow Leaf Curl Virus", "crop": "Tomato", "severity": "Critical", "pathogen": "Begomovirus"},
    "Tomato___Tomato_mosaic_virus": {"disease": "Mosaic Virus", "crop": "Tomato", "severity": "High", "pathogen": "Tobamovirus"},
    "Tomato___Spider_mites Two-spotted_spider_mite": {"disease": "Two-Spotted Spider Mite", "crop": "Tomato", "severity": "High", "pathogen": "Tetranychus urticae"},
    "Tomato___Septoria_leaf_spot": {"disease": "Septoria Leaf Spot", "crop": "Tomato", "severity": "Medium", "pathogen": "Septoria lycopersici"},
    "Tomato___Bacterial_spot": {"disease": "Bacterial Spot", "crop": "Tomato", "severity": "High", "pathogen": "Xanthomonas vesicatoria"},
    "Tomato___Leaf_Mold": {"disease": "Leaf Mold", "crop": "Tomato", "severity": "Medium", "pathogen": "Passalora fulva"},
    "Tomato___Target_Spot": {"disease": "Target Spot", "crop": "Tomato", "severity": "Medium", "pathogen": "Corynespora cassiicola"},
    "Pepper,_bell___Bacterial_spot": {"disease": "Bacterial Spot", "crop": "Bell Pepper", "severity": "High", "pathogen": "Xanthomonas euvesicatoria"},
    "Pepper,_bell___healthy": {"disease": "Healthy", "crop": "Bell Pepper", "severity": "None", "pathogen": "None"},
    "Peach___Bacterial_spot": {"disease": "Bacterial Spot", "crop": "Peach", "severity": "High", "pathogen": "Xanthomonas arboricola"},
    "Peach___healthy": {"disease": "Healthy", "crop": "Peach", "severity": "None", "pathogen": "None"},
    "Cherry_(including_sour)___Powdery_mildew": {"disease": "Powdery Mildew", "crop": "Cherry", "severity": "Medium", "pathogen": "Podosphaera clandestina"},
    "Cherry_(including_sour)___healthy": {"disease": "Healthy", "crop": "Cherry", "severity": "None", "pathogen": "None"},
    "Orange___Haunglongbing_(Citrus_greening)": {"disease": "Citrus Greening (HLB)", "crop": "Orange", "severity": "Critical", "pathogen": "Candidatus Liberibacter asiaticus"},
    "Strawberry___Leaf_scorch": {"disease": "Leaf Scorch", "crop": "Strawberry", "severity": "Medium", "pathogen": "Diplocarpon earlianum"},
    "Strawberry___healthy": {"disease": "Healthy", "crop": "Strawberry", "severity": "None", "pathogen": "None"},
    "Squash___Powdery_mildew": {"disease": "Powdery Mildew", "crop": "Squash", "severity": "Medium", "pathogen": "Erysiphe cichoracearum"},
    "Blueberry___healthy": {"disease": "Healthy", "crop": "Blueberry", "severity": "None", "pathogen": "None"},
    "Raspberry___healthy": {"disease": "Healthy", "crop": "Raspberry", "severity": "None", "pathogen": "None"},
    "Soybean___healthy": {"disease": "Healthy", "crop": "Soybean", "severity": "None", "pathogen": "None"},
}


# ─────────────────────────────────────────────
# Multipart Form Parser (pure Python)
# ─────────────────────────────────────────────
def parse_multipart(body_bytes, content_type):
    """Minimal multipart/form-data parser."""
    boundary = None
    for part in content_type.split(";"):
        part = part.strip()
        if part.startswith("boundary="):
            boundary = part[len("boundary="):].strip().strip('"')
            break
    if not boundary:
        return {}

    delimiter = ("--" + boundary).encode()
    end_delimiter = ("--" + boundary + "--").encode()
    fields = {}

    parts = body_bytes.split(delimiter)
    for raw_part in parts[1:]:
        if raw_part.strip() == b"--" or raw_part.strip() == b"" or raw_part.startswith(b"--"):
            continue
        # Split headers and body
        if b"\r\n\r\n" in raw_part:
            headers_raw, content = raw_part.split(b"\r\n\r\n", 1)
        elif b"\n\n" in raw_part:
            headers_raw, content = raw_part.split(b"\n\n", 1)
        else:
            continue

        # Strip trailing boundary delimiter
        content = content.rstrip(b"\r\n")
        if content.endswith(b"--"):
            content = content[:-2].rstrip(b"\r\n")

        # Parse Content-Disposition header
        headers_str = headers_raw.decode("utf-8", errors="replace")
        name = None
        filename = None
        for line in headers_str.splitlines():
            if "content-disposition" in line.lower():
                for seg in line.split(";"):
                    seg = seg.strip()
                    if seg.startswith("name="):
                        name = seg[5:].strip().strip('"')
                    elif seg.startswith("filename="):
                        filename = seg[9:].strip().strip('"')
        if name:
            fields[name] = content
            if filename:
                fields["_filename"] = filename

    return fields


# ─────────────────────────────────────────────
# HTTP Request Handler
# ─────────────────────────────────────────────
class CropGuardianHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        print(f"  [{datetime.now().strftime('%H:%M:%S')}] {format % args}")

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def send_file(self, filepath):
        try:
            with open(filepath, "rb") as f:
                content = f.read()
            mime, _ = mimetypes.guess_type(filepath)
            mime = mime or "application/octet-stream"
            self.send_response(200)
            self.send_header("Content-Type", mime)
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path   = parsed.path.rstrip("/") or "/"

        # API routes
        if path == "/api/health":
            self.send_json({"status": "ok", "timestamp": datetime.now().isoformat()})

        elif path == "/api/status":
            self.send_json({
                "mode": "demo",
                "model_loaded": False,
                "num_classes": len(ALL_DISEASES),
                "message": "Running in Demo Mode — train model to enable real predictions"
            })

        elif path == "/api/diseases":
            self.send_json({
                "success": True,
                "count": len(ALL_DISEASES),
                "diseases": ALL_DISEASES
            })

        # Static files
        elif path == "/" or path == "/index.html":
            self.send_file(os.path.join(FRONTEND_DIR, "index.html"))

        else:
            # Serve static file from frontend directory
            file_path = os.path.join(FRONTEND_DIR, path.lstrip("/"))
            if os.path.isfile(file_path):
                self.send_file(file_path)
            else:
                # Fallback to index.html for SPA routing
                self.send_file(os.path.join(FRONTEND_DIR, "index.html"))

    def do_POST(self):
        parsed = urlparse(self.path)
        path   = parsed.path

        if path == "/api/predict":
            global scenario_index

            content_length = int(self.headers.get("Content-Length", 0))
            content_type   = self.headers.get("Content-Type", "")
            body = self.rfile.read(content_length)

            # Parse multipart to get the image (we don't process it in demo mode)
            if "multipart/form-data" not in content_type:
                self.send_json({"success": False, "error": "Expected multipart/form-data"}, 400)
                return

            fields = parse_multipart(body, content_type)
            if "image" not in fields:
                self.send_json({"success": False, "error": "No image field in request"}, 400)
                return

            # Smart scenario selection based on filename keywords or cycle
            fn = str(fields.get("_filename", "")).lower()
            matched_scenario = None
            if "corn" in fn or "maize" in fn:
                matched = [s for s in DEMO_SCENARIOS if "corn" in s["class_name"].lower()]
                if matched:
                    matched_scenario = random.choice(matched)
            elif "apple" in fn:
                matched = [s for s in DEMO_SCENARIOS if "apple" in s["class_name"].lower()]
                if matched:
                    matched_scenario = random.choice(matched)
            elif "grape" in fn:
                matched = [s for s in DEMO_SCENARIOS if "grape" in s["class_name"].lower()]
                if matched:
                    matched_scenario = random.choice(matched)
            elif "tomato" in fn:
                matched = [s for s in DEMO_SCENARIOS if "tomato" in s["class_name"].lower()]
                if "healthy" in fn:
                    matched = [s for s in matched if "healthy" in s["class_name"].lower()]
                if matched:
                    matched_scenario = random.choice(matched)
            elif "potato" in fn:
                matched = [s for s in DEMO_SCENARIOS if "potato" in s["class_name"].lower()]
                if matched:
                    matched_scenario = random.choice(matched)
            elif "healthy" in fn:
                matched = [s for s in DEMO_SCENARIOS if "healthy" in s["class_name"].lower()]
                if matched:
                    matched_scenario = random.choice(matched)

            if matched_scenario:
                scenario = matched_scenario
            else:
                scenario = DEMO_SCENARIOS[scenario_index % len(DEMO_SCENARIOS)]
                scenario_index += 1

            # Add slight confidence variation for realism
            noise = random.uniform(-0.015, 0.015)
            conf  = max(0.50, min(0.999, scenario["prediction"]["confidence_raw"] + noise))
            response_prediction = dict(scenario["prediction"])
            response_prediction["confidence"] = round(conf * 100, 2)
            response_prediction["confidence_raw"] = conf

            response = {
                "success": True,
                "mode": "demo",
                "timestamp": datetime.now().isoformat(),
                "prediction": response_prediction,
                "top3": scenario["top3"],
            }
            self.send_json(response)

        else:
            self.send_json({"success": False, "error": "Not found"}, 404)


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────
if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), CropGuardianHandler)

    print("\n" + "=" * 55)
    print("  🌿  CropGuardian — Standalone Server")
    print("  Mode:    🎭 Demo (No dependencies needed)")
    print(f"  URL:     http://localhost:{PORT}")
    print(f"  Classes: {len(ALL_DISEASES)} disease conditions")
    print("=" * 55)
    print("\n  Press Ctrl+C to stop\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n  🛑  Server stopped.")
        server.server_close()
