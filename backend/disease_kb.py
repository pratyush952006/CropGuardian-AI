"""
CropGuardian — Disease Knowledge Base
All 38 PlantVillage classes with treatment recommendations,
symptoms, severity levels, and preventive measures.
"""

DISEASE_KB = {
    # ─────────── APPLE ───────────
    "Apple___Apple_scab": {
        "crop": "Apple",
        "disease": "Apple Scab",
        "pathogen": "Venturia inaequalis (Fungus)",
        "severity": "Medium",
        "description": "Apple scab is one of the most common and serious diseases of apple trees, caused by the fungus Venturia inaequalis. It affects leaves, blossoms, and fruit.",
        "symptoms": [
            "Olive-green to brown velvety spots on leaves",
            "Yellowing and premature leaf drop",
            "Dark scabby lesions on fruit surface",
            "Deformed and cracked fruit",
        ],
        "causes": [
            "Fungal spores released during wet spring weather",
            "Infected fallen leaves from previous season",
            "High humidity and temperature 16–24°C",
        ],
        "treatment": {
            "organic": [
                "Apply sulfur-based fungicide every 7–10 days during wet periods",
                "Use copper-based sprays (Bordeaux mixture) at bud break",
                "Remove and destroy infected leaves and fruit",
                "Apply neem oil spray every 2 weeks",
            ],
            "chemical": [
                "Captan (50 WP) — apply at 2.5g/L water",
                "Mancozeb (75 WP) — apply at 2g/L water",
                "Myclobutanil — systemic fungicide for severe infections",
                "Trifloxystrobin + Tebuconazole — broad-spectrum protection",
            ],
        },
        "prevention": [
            "Plant scab-resistant apple varieties",
            "Ensure good air circulation by proper pruning",
            "Rake and destroy fallen leaves in autumn",
            "Apply preventive fungicide before wet season",
            "Avoid overhead irrigation",
        ],
    },

    "Apple___Black_rot": {
        "crop": "Apple",
        "disease": "Black Rot",
        "pathogen": "Botryosphaeria obtusa (Fungus)",
        "severity": "High",
        "description": "Black rot is a fungal disease affecting apple trees, causing fruit rot, leaf spots, and cankers on branches.",
        "symptoms": [
            "Purple-bordered brown spots on leaves (frog-eye leaf spot)",
            "Black mummified fruit remaining on tree",
            "Cankers on branches with reddish-brown wood",
            "Fruit turning black and shriveling",
        ],
        "causes": [
            "Fungal infection through wounds and insect damage",
            "Mummified fruit acting as inoculum",
            "Wet, warm weather (24–30°C)",
        ],
        "treatment": {
            "organic": [
                "Remove and destroy all mummified fruit and cankers",
                "Apply copper-based fungicides in early spring",
                "Prune infected wood 15cm below visible infection",
                "Use Bacillus subtilis biological control",
            ],
            "chemical": [
                "Captan — primary fungicide for black rot",
                "Thiophanate-methyl — systemic protection",
                "Ziram — protective fungicide",
                "Boscalid + Pyraclostrobin — dual-action protection",
            ],
        },
        "prevention": [
            "Remove dead wood and mummified fruit",
            "Maintain tree vigor with proper nutrition",
            "Control insects that create wound entry points",
            "Apply dormant copper spray in late winter",
        ],
    },

    "Apple___Cedar_apple_rust": {
        "crop": "Apple",
        "disease": "Cedar Apple Rust",
        "pathogen": "Gymnosporangium juniperi-virginianae (Fungus)",
        "severity": "Medium",
        "description": "Cedar apple rust requires two host plants (apple/crabapple and Eastern red cedar/juniper) to complete its life cycle.",
        "symptoms": [
            "Bright orange-yellow spots on upper leaf surface",
            "Tube-like structures on leaf undersides",
            "Orange-red spots on fruit and stems",
            "Premature defoliation in severe cases",
        ],
        "causes": [
            "Fungal spores from nearby cedar/juniper trees",
            "Wet spring conditions during bud break",
            "Wind-carried spores from infected cedars",
        ],
        "treatment": {
            "organic": [
                "Apply sulfur-based fungicides starting at pink bud stage",
                "Use copper hydroxide sprays",
                "Remove nearby eastern red cedar trees if possible",
                "Neem oil applications during early infection",
            ],
            "chemical": [
                "Myclobutanil (Rally) — highly effective systemic fungicide",
                "Propiconazole — DMI fungicide",
                "Trifloxystrobin — strobilurin class, excellent curative action",
                "Fenarimol — older but effective option",
            ],
        },
        "prevention": [
            "Plant rust-resistant apple varieties",
            "Remove eastern red cedar/juniper trees within 1 mile",
            "Apply preventive fungicide from pink bud stage",
            "Monitor local cedar trees for galls in spring",
        ],
    },

    "Apple___healthy": {
        "crop": "Apple",
        "disease": "Healthy",
        "pathogen": "None",
        "severity": "None",
        "description": "Your apple plant appears healthy! No disease detected.",
        "symptoms": [],
        "causes": [],
        "treatment": {"organic": [], "chemical": []},
        "prevention": [
            "Maintain regular irrigation schedule",
            "Apply balanced NPK fertilizer seasonally",
            "Prune annually for good air circulation",
            "Monitor regularly for early signs of disease",
            "Keep weeds around base under control",
        ],
    },

    # ─────────── BLUEBERRY ───────────
    "Blueberry___healthy": {
        "crop": "Blueberry",
        "disease": "Healthy",
        "pathogen": "None",
        "severity": "None",
        "description": "Your blueberry plant is healthy! Continue good agricultural practices.",
        "symptoms": [],
        "causes": [],
        "treatment": {"organic": [], "chemical": []},
        "prevention": [
            "Maintain soil pH between 4.5–5.5",
            "Mulch with pine bark or sawdust",
            "Prune dead canes each winter",
            "Apply ammonium sulfate fertilizer",
        ],
    },

    # ─────────── CHERRY ───────────
    "Cherry_(including_sour)___Powdery_mildew": {
        "crop": "Cherry",
        "disease": "Powdery Mildew",
        "pathogen": "Podosphaera clandestina (Fungus)",
        "severity": "Medium",
        "description": "Powdery mildew affects cherry trees, particularly young shoots and leaves, reducing fruit quality and yield.",
        "symptoms": [
            "White powdery coating on leaves, shoots, and fruit",
            "Curling and distortion of young leaves",
            "Stunted shoot growth",
            "Russeted patches on fruit surface",
        ],
        "causes": [
            "Fungal infection in warm (20–27°C), dry conditions",
            "High humidity with poor air circulation",
            "Dense canopy promoting fungal growth",
        ],
        "treatment": {
            "organic": [
                "Spray baking soda solution (1 tbsp/L water + few drops of soap)",
                "Apply potassium bicarbonate sprays",
                "Use sulfur dust or wettable sulfur",
                "Neem oil spray every 7–14 days",
            ],
            "chemical": [
                "Myclobutanil — DMI fungicide, systemic",
                "Trifloxystrobin — strobilurin, preventive + curative",
                "Fenbuconazole — effective systemic option",
                "Azoxystrobin — broad-spectrum protection",
            ],
        },
        "prevention": [
            "Prune for good air circulation",
            "Avoid excess nitrogen fertilization",
            "Plant resistant varieties",
            "Apply preventive sulfur sprays in early season",
        ],
    },

    "Cherry_(including_sour)___healthy": {
        "crop": "Cherry",
        "disease": "Healthy",
        "pathogen": "None",
        "severity": "None",
        "description": "Your cherry plant is healthy!",
        "symptoms": [],
        "causes": [],
        "treatment": {"organic": [], "chemical": []},
        "prevention": [
            "Regular pruning for air circulation",
            "Balanced fertilization",
            "Monitor for pests and diseases",
        ],
    },

    # ─────────── CORN ───────────
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": {
        "crop": "Corn (Maize)",
        "disease": "Gray Leaf Spot (Cercospora Leaf Spot)",
        "pathogen": "Cercospora zeae-maydis (Fungus)",
        "severity": "High",
        "description": "Gray leaf spot is one of the most yield-limiting corn diseases globally, thriving in warm, humid conditions.",
        "symptoms": [
            "Long, narrow, tan to gray rectangular lesions",
            "Lesions parallel to leaf veins",
            "Premature senescence of leaves",
            "Lesions turning gray with spore masses",
        ],
        "causes": [
            "Fungal spores from infected crop residue",
            "Warm temperatures (25–30°C) + high humidity",
            "Minimum 11+ hours of leaf wetness",
            "Continuous corn cultivation",
        ],
        "treatment": {
            "organic": [
                "Remove and destroy infected crop residue",
                "Crop rotation with non-host crops",
                "Improve field drainage to reduce humidity",
                "Apply Trichoderma-based biocontrol agents",
            ],
            "chemical": [
                "Azoxystrobin (Quadris) — strobilurin fungicide",
                "Propiconazole (Tilt) — DMI fungicide",
                "Pyraclostrobin + Metconazole — dual action",
                "Trifloxystrobin + Prothioconazole — premium option",
            ],
        },
        "prevention": [
            "Plant resistant corn hybrids",
            "Practice crop rotation (2-year)",
            "Till crop residue to accelerate decomposition",
            "Avoid late planting dates",
            "Apply fungicide at VT/R1 stage preventively",
        ],
    },

    "Corn_(maize)___Common_rust_": {
        "crop": "Corn (Maize)",
        "disease": "Common Rust",
        "pathogen": "Puccinia sorghi (Fungus)",
        "severity": "Medium",
        "description": "Common rust is a widespread fungal disease of corn that can significantly reduce yield if infection occurs early.",
        "symptoms": [
            "Small, brick-red to cinnamon-colored pustules on both leaf surfaces",
            "Pustules later turn dark brown to black",
            "Chlorotic (yellow) halos around pustules",
            "Severe infection causes leaf death",
        ],
        "causes": [
            "Wind-blown spores from alternate hosts",
            "Cool temperatures (16–23°C) + high humidity",
            "Susceptible corn varieties",
        ],
        "treatment": {
            "organic": [
                "Apply sulfur-based fungicides at first sign",
                "Use neem oil spray as preventive measure",
                "Remove heavily infected plants to reduce spread",
            ],
            "chemical": [
                "Trifloxystrobin — most effective for rust",
                "Propiconazole — good curative activity",
                "Azoxystrobin + Propiconazole (Quilt Xcel)",
                "Mancozeb — protective, economical option",
            ],
        },
        "prevention": [
            "Plant rust-resistant corn hybrids",
            "Early planting to avoid peak spore periods",
            "Monitor fields regularly from V8 stage",
            "Apply fungicide if >50% plants show rust before silking",
        ],
    },

    "Corn_(maize)___Northern_Leaf_Blight": {
        "crop": "Corn (Maize)",
        "disease": "Northern Corn Leaf Blight",
        "pathogen": "Exserohilum turcicum (Fungus)",
        "severity": "High",
        "description": "Northern corn leaf blight (NCLB) is a major foliar disease that can cause 30–50% yield loss in susceptible hybrids.",
        "symptoms": [
            "Large, cigar-shaped lesions (2.5–15 cm long)",
            "Tan to grayish-green lesions with wavy margins",
            "Dark sporulation visible on lesion surface",
            "Blighting of entire leaves in severe cases",
        ],
        "causes": [
            "Fungal spores from infected residue or wind",
            "Moderate temperatures (18–27°C) + frequent rain",
            "Extended periods of leaf wetness (>6 hours)",
        ],
        "treatment": {
            "organic": [
                "Crop rotation with soybean or wheat",
                "Deep tillage to bury infected residue",
                "Apply Bacillus subtilis biofungicides",
            ],
            "chemical": [
                "Azoxystrobin + Propiconazole — most widely used",
                "Pyraclostrobin (Headline) — excellent protection",
                "Tebuconazole — good curative activity",
                "Picoxystrobin + Cyproconazole — dual protection",
            ],
        },
        "prevention": [
            "Plant NCLB-resistant corn hybrids (Ht gene)",
            "2-year crop rotation with non-host crops",
            "Apply fungicide at silking stage in high-risk areas",
            "Improve field drainage",
        ],
    },

    "Corn_(maize)___healthy": {
        "crop": "Corn (Maize)",
        "disease": "Healthy",
        "pathogen": "None",
        "severity": "None",
        "description": "Your corn plant looks healthy!",
        "symptoms": [],
        "causes": [],
        "treatment": {"organic": [], "chemical": []},
        "prevention": [
            "Balanced fertilization (N-P-K based on soil test)",
            "Adequate plant spacing",
            "Regular scouting for pests",
            "Proper irrigation management",
        ],
    },

    # ─────────── GRAPE ───────────
    "Grape___Black_rot": {
        "crop": "Grape",
        "disease": "Black Rot",
        "pathogen": "Guignardia bidwellii (Fungus)",
        "severity": "High",
        "description": "Black rot is the most destructive grape disease in humid climates, potentially destroying 80% of the crop.",
        "symptoms": [
            "Circular brown spots with dark borders on leaves",
            "Tan lesions containing black pycnidia (fruiting bodies)",
            "Young berries turning brown, then black and shriveled (mummies)",
            "Infected shoots with dark lesions",
        ],
        "causes": [
            "Fungal spores from overwintering mummified berries",
            "Wet, warm weather (20–30°C)",
            "Spore dispersal during rainfall",
        ],
        "treatment": {
            "organic": [
                "Remove and destroy all mummified berries",
                "Apply lime sulfur during dormant season",
                "Use copper-based fungicides",
                "Apply Bacillus subtilis biocontrol",
            ],
            "chemical": [
                "Myclobutanil — excellent for black rot control",
                "Mancozeb — protective fungicide",
                "Tebuconazole — systemic curative action",
                "Captan + Myclobutanil — combined protection",
            ],
        },
        "prevention": [
            "Remove all mummified clusters and infected debris",
            "Prune for good canopy ventilation",
            "Apply first spray at bud break",
            "Continue sprays every 7–10 days through fruit set",
        ],
    },

    "Grape___Esca_(Black_Measles)": {
        "crop": "Grape",
        "disease": "Esca (Black Measles)",
        "pathogen": "Phaeomoniella chlamydospora / Phaeoacremonium (Fungus complex)",
        "severity": "High",
        "description": "Esca is a serious trunk disease complex affecting grapevines worldwide, causing progressive vine decline.",
        "symptoms": [
            "Interveinal chlorosis and necrosis on leaves (tiger stripe pattern)",
            "Berries with dark spotting (measles symptom)",
            "Sudden wilting and collapse of shoots (apoplexy)",
            "Internal wood decay and discoloration",
        ],
        "causes": [
            "Fungal infection through pruning wounds",
            "Stressed vines more susceptible",
            "Secondary infection from wood-boring insects",
        ],
        "treatment": {
            "organic": [
                "Apply wound sealants immediately after pruning",
                "Remove and burn severely infected wood",
                "Delay pruning to reduce infection risk",
                "Apply Trichoderma-based biocontrol to wounds",
            ],
            "chemical": [
                "Thiophanate-methyl — apply to pruning wounds",
                "Flusilazole — trunk injection for severe cases",
                "Tebuconazole — wound protection",
            ],
        },
        "prevention": [
            "Use clean, sharp pruning tools",
            "Seal all pruning wounds immediately",
            "Prune during dry weather",
            "Remove and burn infected canes/trunks",
            "Maintain vine health with proper nutrition",
        ],
    },

    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": {
        "crop": "Grape",
        "disease": "Leaf Blight (Isariopsis Leaf Spot)",
        "pathogen": "Isariopsis clavispora (Fungus)",
        "severity": "Medium",
        "description": "A fungal disease causing leaf spots and premature defoliation in grapevines.",
        "symptoms": [
            "Angular to irregular brown spots on leaves",
            "Yellow halos surrounding lesions",
            "Premature defoliation",
            "Reduced photosynthesis and fruit quality",
        ],
        "causes": ["Fungal infection during wet, warm conditions", "Poor air circulation in canopy"],
        "treatment": {
            "organic": [
                "Remove infected leaves promptly",
                "Apply copper-based fungicides",
                "Improve canopy management",
            ],
            "chemical": [
                "Mancozeb — broad-spectrum protection",
                "Carbendazim — systemic fungicide",
                "Propiconazole — curative action",
            ],
        },
        "prevention": [
            "Canopy management for air circulation",
            "Avoid overhead irrigation",
            "Apply preventive copper sprays",
        ],
    },

    "Grape___healthy": {
        "crop": "Grape",
        "disease": "Healthy",
        "pathogen": "None",
        "severity": "None",
        "description": "Your grapevine is healthy!",
        "symptoms": [],
        "causes": [],
        "treatment": {"organic": [], "chemical": []},
        "prevention": [
            "Annual pruning for canopy management",
            "Balanced fertilization",
            "Regular disease scouting",
        ],
    },

    # ─────────── ORANGE ───────────
    "Orange___Haunglongbing_(Citrus_greening)": {
        "crop": "Orange",
        "disease": "Huanglongbing (Citrus Greening)",
        "pathogen": "Candidatus Liberibacter asiaticus (Bacteria)",
        "severity": "Critical",
        "description": "Citrus greening (HLB) is the most destructive citrus disease worldwide with no cure. It is transmitted by the Asian citrus psyllid.",
        "symptoms": [
            "Asymmetrical yellowing (blotchy mottle) on leaves",
            "Small, misshapen, bitter fruit",
            "Fruit remains green at the stylar (bottom) end",
            "Premature fruit drop",
            "Twig dieback and overall tree decline",
        ],
        "causes": [
            "Bacterial infection spread by Asian citrus psyllid (Diaphorina citri)",
            "Infected grafting material",
            "No known cure once infected",
        ],
        "treatment": {
            "organic": [
                "Remove and destroy infected trees immediately",
                "Control psyllid populations with kaolin clay",
                "Apply reflective mulch to deter psyllids",
                "Trunk injection with micronutrients to extend tree life",
            ],
            "chemical": [
                "Imidacloprid — systemic insecticide for psyllid control",
                "Thiamethoxam — alternative psyllid control",
                "Trunk injection with antibiotics (tetracycline) — slows progress",
                "Drenching with Spirotetramat — psyllid suppression",
            ],
        },
        "prevention": [
            "Use certified disease-free planting material",
            "Control Asian citrus psyllid populations",
            "Quarantine new plant material",
            "Remove and destroy infected trees immediately",
            "Establish windbreaks to reduce psyllid movement",
        ],
    },

    # ─────────── PEACH ───────────
    "Peach___Bacterial_spot": {
        "crop": "Peach",
        "disease": "Bacterial Spot",
        "pathogen": "Xanthomonas arboricola pv. pruni (Bacteria)",
        "severity": "High",
        "description": "Bacterial spot is one of the most common and damaging diseases of peach and nectarine, affecting leaves, fruit, and twigs.",
        "symptoms": [
            "Small, water-soaked spots on leaves turning purplish",
            "Shot-hole appearance as lesions fall out",
            "Dark, sunken spots on fruit with cracking",
            "Twig cankers with gumming",
            "Premature defoliation",
        ],
        "causes": [
            "Bacterial infection through stomata and wounds",
            "Warm (24–29°C), wet weather",
            "Wind-driven rain spreading bacteria",
        ],
        "treatment": {
            "organic": [
                "Apply copper hydroxide sprays starting at bud swell",
                "Remove infected twigs with cankers",
                "Apply fixed copper + mancozeb combination",
            ],
            "chemical": [
                "Copper hydroxide (Kocide) — primary treatment",
                "Oxytetracycline (Mycoshield) — antibiotic spray",
                "Kasugamycin — bacterial control",
                "Copper + Mancozeb — combined protection",
            ],
        },
        "prevention": [
            "Plant resistant peach varieties",
            "Avoid overhead irrigation",
            "Apply copper sprays during dormant season",
            "Prune for air circulation",
            "Avoid sites with frost damage (creates entry points)",
        ],
    },

    "Peach___healthy": {
        "crop": "Peach",
        "disease": "Healthy",
        "pathogen": "None",
        "severity": "None",
        "description": "Your peach tree is healthy!",
        "symptoms": [],
        "causes": [],
        "treatment": {"organic": [], "chemical": []},
        "prevention": [
            "Annual dormant copper sprays",
            "Proper pruning for air circulation",
            "Balanced fertilization",
        ],
    },

    # ─────────── PEPPER ───────────
    "Pepper,_bell___Bacterial_spot": {
        "crop": "Bell Pepper",
        "disease": "Bacterial Spot",
        "pathogen": "Xanthomonas euvesicatoria (Bacteria)",
        "severity": "High",
        "description": "Bacterial spot is a major disease of pepper, causing significant yield loss through defoliation and fruit blemishes.",
        "symptoms": [
            "Small, water-soaked spots on leaves turning brown",
            "Yellow halos around lesions",
            "Shot-hole appearance on leaves",
            "Raised, scabby lesions on fruit",
            "Defoliation exposing fruit to sunscald",
        ],
        "causes": [
            "Bacterial infection from infected seed or transplants",
            "Warm (24–30°C), wet, windy conditions",
            "Splashing water spreads bacteria",
        ],
        "treatment": {
            "organic": [
                "Apply copper-based bactericides",
                "Use disease-free certified seed",
                "Avoid overhead irrigation",
                "Crop rotation with non-solanaceous crops",
            ],
            "chemical": [
                "Copper hydroxide + Mancozeb — standard treatment",
                "Kasugamycin — effective antibiotic bactericide",
                "Acibenzolar-S-methyl (Actigard) — systemic acquired resistance",
                "Copper octanoate — alternative copper source",
            ],
        },
        "prevention": [
            "Use certified pathogen-free seed",
            "Hot water seed treatment (50°C for 25 minutes)",
            "3–4 year crop rotation",
            "Drip irrigation instead of overhead",
            "Avoid working in fields when wet",
        ],
    },

    "Pepper,_bell___healthy": {
        "crop": "Bell Pepper",
        "disease": "Healthy",
        "pathogen": "None",
        "severity": "None",
        "description": "Your bell pepper plant is healthy!",
        "symptoms": [],
        "causes": [],
        "treatment": {"organic": [], "chemical": []},
        "prevention": [
            "Crop rotation every 3–4 years",
            "Drip irrigation",
            "Regular scouting",
        ],
    },

    # ─────────── POTATO ───────────
    "Potato___Early_blight": {
        "crop": "Potato",
        "disease": "Early Blight",
        "pathogen": "Alternaria solani (Fungus)",
        "severity": "Medium",
        "description": "Early blight is a common fungal disease of potato, causing premature defoliation and reduced tuber size.",
        "symptoms": [
            "Dark brown spots with concentric rings (target board pattern)",
            "Yellow chlorotic halo around lesions",
            "Lower leaves affected first, progressing upward",
            "Lesions coalesce causing leaf death",
            "Dark sunken lesions on tubers",
        ],
        "causes": [
            "Fungal infection from infected seed or soil debris",
            "Warm (24–29°C), humid conditions",
            "Plant stress (drought, nutrient deficiency)",
        ],
        "treatment": {
            "organic": [
                "Apply copper-based fungicides at first sign",
                "Remove and destroy infected lower leaves",
                "Ensure proper potassium nutrition (reduces severity)",
                "Neem oil spray as preventive",
            ],
            "chemical": [
                "Mancozeb (75 WP) — 2g/L, apply every 7–10 days",
                "Azoxystrobin — systemic, excellent results",
                "Chlorothalonil — broad-spectrum protection",
                "Iprodione — effective at moderate infections",
            ],
        },
        "prevention": [
            "Use certified disease-free seed potatoes",
            "Crop rotation (3+ years)",
            "Avoid overhead irrigation",
            "Apply balanced fertilizer (adequate potassium)",
            "Hill up soil around plants",
        ],
    },

    "Potato___Late_blight": {
        "crop": "Potato",
        "disease": "Late Blight",
        "pathogen": "Phytophthora infestans (Oomycete)",
        "severity": "Critical",
        "description": "Late blight is the most devastating potato disease, responsible for the Irish Famine (1845). Can destroy crops in days under favorable conditions.",
        "symptoms": [
            "Water-soaked, dark green to brown lesions on leaves",
            "White mold on undersides of leaves in humid conditions",
            "Lesions rapidly expand to kill entire leaves",
            "Dark, firm rot on tubers",
            "Foul smell from infected tubers",
        ],
        "causes": [
            "Phytophthora infestans oomycete in cool (10–20°C), wet conditions",
            "Infected seed tubers",
            "Airborne sporangia during humid weather",
        ],
        "treatment": {
            "organic": [
                "Apply copper-based fungicides immediately at first sight",
                "Remove and destroy infected plants (do not compost)",
                "Bordeaux mixture (copper sulfate + lime) spray",
                "Hill up tubers to prevent infection",
            ],
            "chemical": [
                "Metalaxyl + Mancozeb (Ridomil Gold MZ) — most effective",
                "Cymoxanil + Mancozeb (Curzate M8) — systemic + contact",
                "Dimethomorph (Acrobat) — excellent curative action",
                "Fluopicolide + Propamocarb (Infinito) — premium option",
            ],
        },
        "prevention": [
            "Use certified disease-free seed potatoes",
            "Plant resistant varieties",
            "Apply preventive fungicides based on blight forecast",
            "Destroy volunteer potato plants",
            "Harvest on dry days; cure tubers before storage",
            "Do NOT leave infected crop debris in field",
        ],
    },

    "Potato___healthy": {
        "crop": "Potato",
        "disease": "Healthy",
        "pathogen": "None",
        "severity": "None",
        "description": "Your potato plant is healthy!",
        "symptoms": [],
        "causes": [],
        "treatment": {"organic": [], "chemical": []},
        "prevention": [
            "Use certified seed potatoes",
            "Proper crop rotation",
            "Regular irrigation management",
        ],
    },

    # ─────────── RASPBERRY ───────────
    "Raspberry___healthy": {
        "crop": "Raspberry",
        "disease": "Healthy",
        "pathogen": "None",
        "severity": "None",
        "description": "Your raspberry plant is healthy!",
        "symptoms": [],
        "causes": [],
        "treatment": {"organic": [], "chemical": []},
        "prevention": [
            "Annual pruning of old canes",
            "Proper trellis support",
            "Balanced fertilization",
        ],
    },

    # ─────────── SOYBEAN ───────────
    "Soybean___healthy": {
        "crop": "Soybean",
        "disease": "Healthy",
        "pathogen": "None",
        "severity": "None",
        "description": "Your soybean plant is healthy!",
        "symptoms": [],
        "causes": [],
        "treatment": {"organic": [], "chemical": []},
        "prevention": [
            "Crop rotation with corn or wheat",
            "Use certified disease-free seed",
            "Scout fields regularly",
        ],
    },

    # ─────────── SQUASH ───────────
    "Squash___Powdery_mildew": {
        "crop": "Squash",
        "disease": "Powdery Mildew",
        "pathogen": "Erysiphe cichoracearum / Sphaerotheca fuliginea (Fungus)",
        "severity": "Medium",
        "description": "Powdery mildew is a very common and easily recognizable disease of squash and other cucurbits.",
        "symptoms": [
            "White to grayish powdery spots on leaf surfaces",
            "Spots coalesce to cover entire leaf",
            "Yellowing and browning of infected tissue",
            "Premature leaf death and reduced fruit size",
        ],
        "causes": [
            "Fungal spores in dry, warm (20–27°C) conditions",
            "High humidity with poor air circulation",
            "Unlike many fungi, does NOT require leaf wetness",
        ],
        "treatment": {
            "organic": [
                "Spray 1:9 milk:water solution every 3–4 days",
                "Baking soda spray (1 tsp + 1 tsp dish soap per liter)",
                "Potassium bicarbonate — most effective organic option",
                "Neem oil spray every 7–10 days",
            ],
            "chemical": [
                "Trifloxystrobin — excellent curative action",
                "Myclobutanil — DMI fungicide, systemic",
                "Tebuconazole — effective systemic option",
                "Azoxystrobin — preventive strobilurin",
            ],
        },
        "prevention": [
            "Plant resistant squash varieties",
            "Avoid overhead irrigation",
            "Maintain proper plant spacing for air circulation",
            "Apply preventive sulfur sprays",
            "Remove severely infected leaves",
        ],
    },

    # ─────────── STRAWBERRY ───────────
    "Strawberry___Leaf_scorch": {
        "crop": "Strawberry",
        "disease": "Leaf Scorch",
        "pathogen": "Diplocarpon earlianum (Fungus)",
        "severity": "Medium",
        "description": "Leaf scorch is a common strawberry disease that can cause significant yield reduction through repeated defoliation.",
        "symptoms": [
            "Small, irregular, dark purple spots on leaves",
            "Centers of spots become light brown to grayish",
            "Spots coalesce giving a 'scorched' appearance",
            "Leaf tissue turns reddish-brown and dies",
            "Severely infected plants become weak and unproductive",
        ],
        "causes": [
            "Fungal infection in cool (15–20°C), wet conditions",
            "Overhead irrigation promotes spread",
            "Infected plants or transplants",
        ],
        "treatment": {
            "organic": [
                "Remove and destroy infected leaves",
                "Apply copper-based fungicides",
                "Improve air circulation through proper spacing",
            ],
            "chemical": [
                "Captan — effective protective fungicide",
                "Myclobutanil — systemic, curative action",
                "Thiophanate-methyl — systemic option",
                "Pyraclostrobin — premium broad-spectrum",
            ],
        },
        "prevention": [
            "Use disease-free certified plants",
            "Avoid overhead irrigation — use drip",
            "Renovate beds after harvest by mowing and tilling",
            "Remove old leaves that harbor infection",
            "3-year rotation with non-strawberry crops",
        ],
    },

    "Strawberry___healthy": {
        "crop": "Strawberry",
        "disease": "Healthy",
        "pathogen": "None",
        "severity": "None",
        "description": "Your strawberry plant is healthy!",
        "symptoms": [],
        "causes": [],
        "treatment": {"organic": [], "chemical": []},
        "prevention": [
            "Use certified disease-free runners",
            "Proper bed renovation after fruiting",
            "Drip irrigation",
        ],
    },

    # ─────────── TOMATO ───────────
    "Tomato___Bacterial_spot": {
        "crop": "Tomato",
        "disease": "Bacterial Spot",
        "pathogen": "Xanthomonas vesicatoria (Bacteria)",
        "severity": "High",
        "description": "Bacterial spot is a major foliar and fruit disease of tomato in warm, humid climates, causing significant crop losses.",
        "symptoms": [
            "Small, water-soaked, circular spots on leaves",
            "Spots turn brown with yellow halos",
            "Shot-hole appearance on leaves",
            "Raised, dark, scabby lesions on fruit",
            "Defoliation exposing fruit to sunscald",
        ],
        "causes": [
            "Bacteria from infected seed or transplants",
            "Warm (24–30°C), wet weather",
            "Wind-driven rain and splashing water",
        ],
        "treatment": {
            "organic": [
                "Apply copper hydroxide sprays preventively",
                "Use disease-free certified seed",
                "Crop rotation with non-solanaceous crops",
                "Remove severely infected plants",
            ],
            "chemical": [
                "Copper hydroxide + Mancozeb — standard program",
                "Kasugamycin (Kasumin) — antibiotic bactericide",
                "Acibenzolar-S-methyl (Actigard) — systemic acquired resistance",
                "Oxolinic acid — antibiotic option",
            ],
        },
        "prevention": [
            "Hot water seed treatment (50°C, 25 min)",
            "3–4 year rotation avoiding pepper and eggplant",
            "Use drip irrigation",
            "Stake plants properly for air circulation",
            "Avoid working in fields when wet",
        ],
    },

    "Tomato___Early_blight": {
        "crop": "Tomato",
        "disease": "Early Blight",
        "pathogen": "Alternaria solani (Fungus)",
        "severity": "Medium",
        "description": "Early blight is the most common foliar disease of tomato worldwide, causing premature defoliation and reduced fruit quality.",
        "symptoms": [
            "Dark brown spots with concentric rings (bull's-eye pattern)",
            "Yellow chlorotic halo around lesions",
            "Lesions first on older lower leaves",
            "Defoliation progressing upward",
            "Dark, sunken lesions on stem and fruit",
        ],
        "causes": [
            "Fungal spores surviving in soil and infected debris",
            "Warm (24–29°C), humid conditions",
            "Plant stress triggers outbreak",
        ],
        "treatment": {
            "organic": [
                "Remove infected lower leaves immediately",
                "Apply copper-based fungicide spray",
                "Neem oil + liquid copper combined spray",
                "Ensure adequate calcium and potassium nutrition",
            ],
            "chemical": [
                "Mancozeb (75 WP) at 2g/L — apply every 7 days",
                "Chlorothalonil — broad-spectrum protection",
                "Azoxystrobin — systemic + protective",
                "Difenoconazole — DMI fungicide, excellent results",
            ],
        },
        "prevention": [
            "Use certified disease-free transplants",
            "Mulch around plants to prevent soil splash",
            "Stake/cage plants for air circulation",
            "Crop rotation (3+ years)",
            "Remove and destroy all crop debris after harvest",
        ],
    },

    "Tomato___Late_blight": {
        "crop": "Tomato",
        "disease": "Late Blight",
        "pathogen": "Phytophthora infestans (Oomycete)",
        "severity": "Critical",
        "description": "Late blight is one of the most devastating tomato diseases. Under favorable conditions, it can destroy an entire crop within a week.",
        "symptoms": [
            "Large, irregular, water-soaked, greenish-gray spots on leaves",
            "White mold on underside of leaves in humid conditions",
            "Rapidly expanding lesions killing leaves and stems",
            "Large, firm, dark-brown irregular blotches on fruit",
            "Greasy appearance to infected tissue",
        ],
        "causes": [
            "Phytophthora infestans in cool (10–20°C), wet conditions",
            "Infected transplants or potato plants nearby",
            "Wind-dispersed sporangia",
        ],
        "treatment": {
            "organic": [
                "Apply copper-based fungicides immediately at first sight",
                "Remove and bag infected plants (do NOT compost)",
                "Bordeaux mixture as protective spray",
                "Ensure plants are not overcrowded",
            ],
            "chemical": [
                "Metalaxyl + Mancozeb (Ridomil Gold MZ) — most effective",
                "Cymoxanil + Mancozeb (Curzate) — systemic + contact",
                "Dimethomorph — excellent curative action",
                "Propamocarb — specific anti-oomycete",
            ],
        },
        "prevention": [
            "Avoid planting near potatoes",
            "Use resistant varieties (Ph-3 gene)",
            "Apply preventive sprays before and during rainy weather",
            "Do not irrigate at night",
            "Remove volunteer tomato/potato plants",
        ],
    },

    "Tomato___Leaf_Mold": {
        "crop": "Tomato",
        "disease": "Leaf Mold",
        "pathogen": "Passalora fulva (Fungus)",
        "severity": "Medium",
        "description": "Tomato leaf mold primarily affects greenhouse and high-tunnel tomatoes, thriving in high humidity environments.",
        "symptoms": [
            "Pale green to yellow spots on upper leaf surface",
            "Olive-green to grayish-brown mold on leaf undersides",
            "Leaves curl upward; older leaves die",
            "Rarely affects fruit directly",
        ],
        "causes": [
            "High humidity (>85%) and warm temperatures (22–25°C)",
            "Poor air circulation in greenhouse or tunnel",
            "Spores surviving on plant debris",
        ],
        "treatment": {
            "organic": [
                "Improve ventilation in greenhouse",
                "Remove infected leaves",
                "Reduce humidity below 85%",
                "Apply copper-based fungicides",
            ],
            "chemical": [
                "Chlorothalonil — protective option",
                "Azoxystrobin — systemic protection",
                "Difenoconazole — excellent curative action",
                "Iprodione — effective in high-humidity settings",
            ],
        },
        "prevention": [
            "Maintain humidity below 85%",
            "Use leaf-mold resistant tomato varieties (Cf genes)",
            "Space plants properly for air circulation",
            "Avoid overhead irrigation in greenhouses",
        ],
    },

    "Tomato___Septoria_leaf_spot": {
        "crop": "Tomato",
        "disease": "Septoria Leaf Spot",
        "pathogen": "Septoria lycopersici (Fungus)",
        "severity": "Medium",
        "description": "Septoria leaf spot is one of the most common tomato diseases, causing severe defoliation and reducing photosynthesis.",
        "symptoms": [
            "Numerous small, circular spots with dark brown borders",
            "Spots have white/gray centers with dark edges",
            "Tiny black pycnidia (fruiting bodies) visible in centers",
            "Lower leaves affected first, progressing upward",
            "Severe defoliation weakening the plant",
        ],
        "causes": [
            "Fungal spores in soil and infected debris",
            "Wet, warm (20–25°C) conditions",
            "Splashing rain and overhead irrigation",
        ],
        "treatment": {
            "organic": [
                "Remove infected leaves immediately",
                "Mulch to prevent soil splash",
                "Apply copper hydroxide spray",
                "Neem oil as preventive",
            ],
            "chemical": [
                "Mancozeb — most economical and effective",
                "Chlorothalonil — broad protection",
                "Azoxystrobin + Difenoconazole (Amistar Top)",
                "Boscalid + Pyraclostrobin — premium option",
            ],
        },
        "prevention": [
            "Use pathogen-free transplants",
            "3-year crop rotation",
            "Stake and mulch plants",
            "Remove plant debris after harvest",
            "Avoid overhead irrigation",
        ],
    },

    "Tomato___Spider_mites Two-spotted_spider_mite": {
        "crop": "Tomato",
        "disease": "Two-Spotted Spider Mite",
        "pathogen": "Tetranychus urticae (Pest/Mite)",
        "severity": "High",
        "description": "Two-spotted spider mites are tiny arachnid pests that can rapidly build up in hot, dry conditions and cause severe crop damage.",
        "symptoms": [
            "Fine stippling (tiny yellow dots) on upper leaf surface",
            "Bronze or silvery discoloration of leaves",
            "Fine webbing on leaf undersides and between leaves",
            "Leaves turn yellow, brown, and drop prematurely",
            "Tiny mites visible with hand lens on leaf undersides",
        ],
        "causes": [
            "Hot, dry weather (>28°C, low humidity)",
            "Overuse of broad-spectrum insecticides killing natural enemies",
            "Dusty field conditions",
        ],
        "treatment": {
            "organic": [
                "Strong water spray to knock mites off plants",
                "Apply neem oil or insecticidal soap every 5–7 days",
                "Introduce predatory mites (Phytoseiulus persimilis)",
                "Spray sulfur-based acaricides in cool of day",
            ],
            "chemical": [
                "Abamectin (Agri-Mek) — excellent mite control",
                "Bifenazate (Floramite) — selective miticide",
                "Hexythiazox — ovicidal, good resistance management",
                "Spiromesifen — long residual, excellent results",
            ],
        },
        "prevention": [
            "Monitor plants weekly with hand lens",
            "Avoid excessive nitrogen (promotes mite populations)",
            "Maintain adequate irrigation (mites prefer dry conditions)",
            "Conserve beneficial insects",
            "Rotate miticide classes for resistance management",
        ],
    },

    "Tomato___Target_Spot": {
        "crop": "Tomato",
        "disease": "Target Spot",
        "pathogen": "Corynespora cassiicola (Fungus)",
        "severity": "Medium",
        "description": "Target spot affects tomato leaves, stems, and fruit, causing premature defoliation and fruit blemishes.",
        "symptoms": [
            "Brown spots with concentric rings on leaves",
            "Spots with yellow margin on upper leaf surface",
            "Dark brown spots on green or ripe fruit",
            "Stem lesions causing dieback",
        ],
        "causes": [
            "Fungal infection in warm (20–30°C), humid conditions",
            "Infected crop debris in soil",
        ],
        "treatment": {
            "organic": [
                "Remove infected leaves and debris",
                "Apply copper-based fungicides",
                "Improve air circulation",
            ],
            "chemical": [
                "Azoxystrobin — systemic protection",
                "Chlorothalonil — broad spectrum",
                "Difenoconazole — excellent curative",
                "Boscalid — good for resistant strains",
            ],
        },
        "prevention": [
            "Rotate crops every 2–3 years",
            "Remove crop debris after harvest",
            "Avoid overhead irrigation",
            "Use resistant varieties where available",
        ],
    },

    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": {
        "crop": "Tomato",
        "disease": "Tomato Yellow Leaf Curl Virus (TYLCV)",
        "pathogen": "Begomovirus (Virus, transmitted by whitefly)",
        "severity": "Critical",
        "description": "TYLCV is one of the most devastating tomato viruses worldwide, causing up to 100% yield loss. No cure exists; management focuses on vector control.",
        "symptoms": [
            "Severe upward curling and cupping of leaves",
            "Interveinal yellowing of young leaves",
            "Stunted plant growth",
            "Flower drop and very few or no fruit",
            "Purplish discoloration of leaf veins",
        ],
        "causes": [
            "Virus transmitted by silverleaf whitefly (Bemisia tabaci)",
            "Infected seedlings or transplants",
            "No mechanical or seed transmission",
        ],
        "treatment": {
            "organic": [
                "Remove and destroy infected plants immediately",
                "Apply yellow sticky traps for whitefly monitoring",
                "Use reflective mulches to repel whiteflies",
                "Spray neem oil or insecticidal soap for whitefly control",
            ],
            "chemical": [
                "Imidacloprid — systemic insecticide for whitefly",
                "Thiamethoxam — neonicotinoid whitefly control",
                "Spirotetramat — phloem-mobile for whitefly nymphs",
                "Pymetrozine — selective, whitefly feeding inhibitor",
            ],
        },
        "prevention": [
            "Use TYLCV-resistant tomato varieties",
            "Apply imidacloprid at transplanting for early protection",
            "Use fine mesh netting in nurseries",
            "Remove infected plants before virus spreads",
            "Eliminate weed hosts of whitefly",
        ],
    },

    "Tomato___Tomato_mosaic_virus": {
        "crop": "Tomato",
        "disease": "Tomato Mosaic Virus (ToMV)",
        "pathogen": "Tobamovirus (Virus)",
        "severity": "High",
        "description": "Tomato mosaic virus is a highly stable, easily transmitted virus that causes significant yield and quality losses.",
        "symptoms": [
            "Mosaic pattern of light and dark green on leaves",
            "Leaf distortion, curling, and stunting",
            "Yellow streaking on young leaves",
            "Internal browning of fruit",
            "Uneven fruit ripening and poor quality",
        ],
        "causes": [
            "Highly stable virus, persists in soil/debris for years",
            "Mechanical transmission through hands, tools, and clothing",
            "Infected seed transmission",
            "Contact between plants",
        ],
        "treatment": {
            "organic": [
                "Remove and destroy infected plants",
                "Wash hands and disinfect tools with 10% bleach solution",
                "Do NOT compost infected material",
                "Use milk spray on tools (milk denatures the virus)",
            ],
            "chemical": [
                "No chemical cure — focus on prevention",
                "Disinfect tools with Virkon S solution",
                "Copper-based sprays may reduce spread",
            ],
        },
        "prevention": [
            "Use certified virus-free/resistant seed (Tm genes)",
            "Wash hands before handling plants",
            "Disinfect all tools between plants",
            "Control tobacco use around plants (ToMV infects tobacco)",
            "Avoid handling plants when moving from infected areas",
        ],
    },

    "Tomato___healthy": {
        "crop": "Tomato",
        "disease": "Healthy",
        "pathogen": "None",
        "severity": "None",
        "description": "Your tomato plant is healthy and thriving!",
        "symptoms": [],
        "causes": [],
        "treatment": {"organic": [], "chemical": []},
        "prevention": [
            "Regular watering at soil level (drip preferred)",
            "Stake or cage plants for support",
            "Mulch to retain moisture and prevent soil splash",
            "Monitor weekly for pests and diseases",
            "Apply balanced fertilizer every 2–3 weeks",
        ],
    },

    # ─────────── EXTENDED CROPS: ONION, WHEAT, MUSTARD, MANGO ───────────
    "Onion___Purple_blotch": {
        "crop": "Onion",
        "disease": "Purple Blotch",
        "pathogen": "Alternaria porri (Fungus)",
        "severity": "High",
        "description": "Purple blotch is a major fungal pathogen affecting all allium species, causing purple sunken lesions and foliar collapse.",
        "symptoms": ["Small water-soaked lesions that turn purple to dark brown", "Concentric zonation rings with yellow chlorotic halos", "Girdling of leaf blade causing premature dieback", "Bulb neck rot during storage"],
        "causes": ["High relative humidity (>90%) with warm temperatures (21–30°C)", "Prolonged leaf wetness from overhead watering", "Splashing rain dispersing Alternaria spores"],
        "treatment": {
            "organic": ["Spray copper oxychloride (3g/L) at first symptom onset", "Apply Trichoderma harzianum bio-fungicide to foliar canopy", "Neem oil emulsion (5ml/L) to suppress spore germination"],
            "chemical": ["Mancozeb 75 WP (2.5g/L) or Chlorothalonil 75 WP (2g/L)", "Difenoconazole 25 EC (1ml/L) systemic triazole spray", "Tebuconazole + Trifloxystrobin curative application"],
        },
        "prevention": ["Crop rotation with non-allium crops for 3 years", "Plant certified pathogen-free bulbs and sets", "Adopt drip irrigation to prevent foliar wetness", "Maintain wide plant spacing for enhanced air circulation"],
    },

    "Onion___healthy": {
        "crop": "Onion",
        "disease": "Healthy",
        "pathogen": "None",
        "severity": "None",
        "description": "Certified healthy onion foliage with vibrant tubular leaves, sturdy neck, and zero fungal lesions.",
        "symptoms": [],
        "causes": [],
        "treatment": {"organic": [], "chemical": []},
        "prevention": ["Balanced nitrogen feeding avoiding late-season excess", "Consistent shallow irrigation during bulb enlargement", "Clean field borders free of volunteer alliums"],
    },

    "Wheat___Leaf_rust": {
        "crop": "Wheat",
        "disease": "Leaf Rust (Brown Rust)",
        "pathogen": "Puccinia triticina (Fungus)",
        "severity": "High",
        "description": "Leaf rust is one of the most destructive cereal diseases, producing scattered orange-brown pustules on wheat blades.",
        "symptoms": ["Small round-to-oval orange-red uredinial pustules on upper blade surface", "Yellow halo surrounding rust pustules", "Rapid blade drying, desiccation, and shrivelled grain"],
        "causes": ["Airborne urediniospores carried by wind currents", "Moderate temperatures (15–22°C) combined with dew or moisture", "Dense canopy microclimates"],
        "treatment": {
            "organic": ["Sulfur dust application (25 kg/ha) during early vegetative stages", "Foliar bio-control sprays using Bacillus subtilis"],
            "chemical": ["Propiconazole 25 EC (1ml/L water) at flag leaf emergence", "Tebuconazole 250 EC (1ml/L) or Azoxystrobin + Difenoconazole", "Pyraclostrobin strobilurin systemic curative spray"],
        },
        "prevention": ["Sow rust-resistant wheat cultivars (Lr genes)", "Timely autumn/winter planting to avoid late-season rust peak", "Balanced nitrogen nutrition to avoid overly lush foliage", "Eradicate alternative host grasses and weeds"],
    },

    "Wheat___healthy": {
        "crop": "Wheat",
        "disease": "Healthy",
        "pathogen": "None",
        "severity": "None",
        "description": "Robust, deep-green wheat foliage with continuous clean venation, firm turgor, and zero fungal pustules.",
        "symptoms": [],
        "causes": [],
        "treatment": {"organic": [], "chemical": []},
        "prevention": ["Adequate potash application to strengthen stalk cell walls", "Optimal seed spacing and balanced NPK fertility", "Routine scouting at tillering and boot stages"],
    },

    "Mustard___White_rust": {
        "crop": "Mustard",
        "disease": "White Rust & Downy Mildew Complex",
        "pathogen": "Albugo candida (Oomycete)",
        "severity": "High",
        "description": "White rust causes prominent white-to-cream pustules and floral staghead malformations in brassica crops.",
        "symptoms": ["Raised chalky-white or porcelain-colored blisters on lower leaf surface", "Hypertrophy and floral deformation known as 'staghead'", "Chlorotic yellow mottling on corresponding upper blade surface"],
        "causes": ["Cool, moist weather (12–18°C) with persistent morning dew", "Oospores surviving in soil and crop debris for multiple seasons", "High planting density reducing sunlight penetration"],
        "treatment": {
            "organic": ["Spray garlic extract (5%) or cow urine concoction for bio-inhibition", "Copper hydroxide (2g/L) foliar protective sprays", "Immediate eradication of staghead infected inflorescences"],
            "chemical": ["Metalaxyl 8% + Mancozeb 64% WP (Ridomil MZ, 2g/L)", "Cymoxanil + Mancozeb translaminar combination", "Mefenoxam systemic seed dressing and early vegetative spray"],
        },
        "prevention": ["Adopt 3-year brassica crop rotation", "Seed treatment with Apron 35 SD (6g/kg seed)", "Timely October planting before cool rust peaks", "Field sanitation and burning of stubble"],
    },

    "Mustard___healthy": {
        "crop": "Mustard",
        "disease": "Healthy",
        "pathogen": "None",
        "severity": "None",
        "description": "Healthy brassica leaf showing smooth lobed foliage, vivid green pigment, and complete absence of white blisters.",
        "symptoms": [],
        "causes": [],
        "treatment": {"organic": [], "chemical": []},
        "prevention": ["Optimum sulfur fertilization (30 kg/ha)", "Proper thinning to maintain 15cm inter-plant spacing", "Avoid excess moisture accumulation around roots"],
    },

    "Mango___Anthracnose": {
        "crop": "Mango",
        "disease": "Anthracnose & Leaf Blight",
        "pathogen": "Colletotrichum gloeosporioides (Fungus)",
        "severity": "High",
        "description": "Anthracnose is the most widespread mango disease, attacking tender leaves, twigs, panicles, and developing fruit.",
        "symptoms": ["Irregular dark-brown to black necrotic spots with concentric halos", "Shot-hole effect as lesion centers dry up and drop out", "Blight of tender shoots and flower blossom wither", "Black tear-stain decay on fruit rind"],
        "causes": ["High humidity (>95%) during flush and blossoming stages", "Fungal inoculum residing in dead twigs and mummified fruit", "Rain splashes carrying conidia to young foliage"],
        "treatment": {
            "organic": ["Pruning dead twigs followed by 1% Bordeaux mixture spray", "Copper oxychloride (3g/L) every 15 days in rainy season", "Spray Pseudomonas fluorescens (20g/L) as bio-antagonist"],
            "chemical": ["Carbendazim 50 WP (1g/L) or Thiophanate-methyl (1g/L)", "Azoxystrobin 23 SC (1ml/L) broad-spectrum strobilurin", "Prochloraz or Difenoconazole post-flush curative treatment"],
        },
        "prevention": ["Annual post-harvest canopy pruning to ensure light penetration", "Inter-tree ventilation and removal of fallen orchard debris", "Pre-monsoon and post-bloom protective copper fungicide sprays"],
    },

    "Mango___healthy": {
        "crop": "Mango",
        "disease": "Healthy",
        "pathogen": "None",
        "severity": "None",
        "description": "Glossy, robust mango leaves with deep emerald color, intact cuticle, and zero necrotic spotting.",
        "symptoms": [],
        "causes": [],
        "treatment": {"organic": [], "chemical": []},
        "prevention": ["Micronutrient zinc and boron sprays at flush stage", "Ring irrigation avoiding water touching tree trunk", "Regular monitoring for hopper and fungal complexes"],
    },
}


def get_disease_info(class_name: str) -> dict:
    """Retrieve disease information for a given class name."""
    return DISEASE_KB.get(class_name, {
        "crop": "Unknown",
        "disease": class_name.replace("_", " ").replace("___", " — "),
        "pathogen": "Unknown",
        "severity": "Unknown",
        "description": "Disease information not found in knowledge base.",
        "symptoms": [],
        "causes": [],
        "treatment": {"organic": [], "chemical": []},
        "prevention": [],
    })


def get_all_classes() -> list:
    """Return all disease class names."""
    return list(DISEASE_KB.keys())
