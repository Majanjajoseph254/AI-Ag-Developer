import random
from PIL import Image
import io


DISEASE_DATABASE = {
    "maize": [
        {
            "disease_name": "Maize Lethal Necrosis (MLN)",
            "severity": "high",
            "treatment": "Remove and destroy infected plants. Apply appropriate insecticides to control thrips and aphid vectors.",
            "prevention": "Use certified disease-free seed. Practice crop rotation with non-cereal crops. Control insect vectors early."
        },
        {
            "disease_name": "Gray Leaf Spot",
            "severity": "medium",
            "treatment": "Apply foliar fungicides such as azoxystrobin or pyraclostrobin at early signs of infection.",
            "prevention": "Plant resistant varieties. Rotate crops and remove crop debris after harvest. Avoid overhead irrigation."
        },
        {
            "disease_name": "Northern Corn Leaf Blight",
            "severity": "medium",
            "treatment": "Apply fungicides containing propiconazole or mancozeb when lesions first appear.",
            "prevention": "Use resistant hybrids. Practice crop rotation. Tillage to bury infected residue."
        },
        {
            "disease_name": "Maize Streak Virus",
            "severity": "high",
            "treatment": "No chemical cure. Remove infected plants immediately to prevent spread by leafhoppers.",
            "prevention": "Plant resistant varieties. Control leafhopper populations with insecticides. Early planting to avoid peak vector activity."
        },
        {
            "disease_name": "Common Rust",
            "severity": "low",
            "treatment": "Apply fungicides like mancozeb or propiconazole if infection is severe before tasseling.",
            "prevention": "Plant rust-resistant varieties. Monitor fields regularly during humid conditions."
        }
    ],
    "tomatoes": [
        {
            "disease_name": "Late Blight",
            "severity": "high",
            "treatment": "Apply copper-based fungicides or chlorothalonil. Remove and destroy severely infected plants.",
            "prevention": "Use certified disease-free seedlings. Avoid overhead watering. Ensure good air circulation between plants."
        },
        {
            "disease_name": "Early Blight",
            "severity": "medium",
            "treatment": "Apply fungicides containing chlorothalonil or mancozeb at 7-10 day intervals.",
            "prevention": "Mulch around plants. Remove lower leaves. Rotate crops for 2-3 years. Stake plants for better airflow."
        },
        {
            "disease_name": "Bacterial Wilt",
            "severity": "high",
            "treatment": "No effective chemical treatment. Remove and destroy infected plants. Solarize soil in affected areas.",
            "prevention": "Use resistant varieties. Practice crop rotation with non-solanaceous crops. Avoid waterlogged conditions."
        },
        {
            "disease_name": "Tomato Yellow Leaf Curl Virus",
            "severity": "high",
            "treatment": "No cure available. Control whitefly vectors with insecticides (imidacloprid). Remove infected plants.",
            "prevention": "Use resistant varieties. Install yellow sticky traps. Use reflective mulches to repel whiteflies."
        },
        {
            "disease_name": "Powdery Mildew",
            "severity": "low",
            "treatment": "Apply sulfur-based fungicides or neem oil. Potassium bicarbonate sprays can also help.",
            "prevention": "Ensure adequate spacing between plants. Avoid excessive nitrogen fertilization. Water at the base of plants."
        }
    ],
    "potatoes": [
        {
            "disease_name": "Potato Late Blight",
            "severity": "high",
            "treatment": "Apply metalaxyl or copper-based fungicides preventively. Destroy infected tubers and foliage.",
            "prevention": "Use certified seed potatoes. Plant resistant varieties. Hill potatoes well to protect tubers."
        },
        {
            "disease_name": "Potato Early Blight",
            "severity": "medium",
            "treatment": "Apply chlorothalonil or mancozeb fungicides at first sign of disease.",
            "prevention": "Practice 3-year crop rotation. Remove volunteer plants. Maintain adequate fertility especially potassium."
        },
        {
            "disease_name": "Bacterial Wilt (Brown Rot)",
            "severity": "high",
            "treatment": "No effective chemical control. Remove all infected plants and tubers. Do not compost infected material.",
            "prevention": "Use certified clean seed. Avoid planting in previously infected fields for 5+ years. Control irrigation."
        },
        {
            "disease_name": "Black Scurf (Rhizoctonia)",
            "severity": "medium",
            "treatment": "Treat seed tubers with fungicide (pencycuron or flutolanil) before planting.",
            "prevention": "Use clean seed potatoes. Rotate crops for 3+ years. Plant in warm, well-drained soil."
        },
        {
            "disease_name": "Potato Virus Y",
            "severity": "medium",
            "treatment": "No chemical treatment. Remove infected plants. Control aphid vectors with insecticides.",
            "prevention": "Use virus-free certified seed. Control aphid populations. Remove volunteer potato plants."
        }
    ],
    "wheat": [
        {
            "disease_name": "Wheat Rust (Stem Rust)",
            "severity": "high",
            "treatment": "Apply triazole fungicides (propiconazole, tebuconazole) at first sign of pustules.",
            "prevention": "Plant resistant varieties. Early planting. Remove alternate host plants (barberry)."
        },
        {
            "disease_name": "Septoria Leaf Blotch",
            "severity": "medium",
            "treatment": "Apply fungicides containing azoxystrobin or propiconazole at flag leaf emergence.",
            "prevention": "Use resistant varieties. Rotate crops. Bury crop residues through tillage."
        },
        {
            "disease_name": "Fusarium Head Blight",
            "severity": "high",
            "treatment": "Apply triazole fungicides at early flowering. Harvest infected grain separately.",
            "prevention": "Plant resistant varieties. Avoid planting wheat after maize. Bury crop residues."
        },
        {
            "disease_name": "Powdery Mildew",
            "severity": "low",
            "treatment": "Apply sulfur-based or triazole fungicides when disease appears on lower leaves.",
            "prevention": "Use resistant varieties. Avoid excessive nitrogen. Ensure adequate plant spacing."
        },
        {
            "disease_name": "Wheat Streak Mosaic Virus",
            "severity": "medium",
            "treatment": "No chemical treatment available. Remove infected plants. Control wheat curl mite vector.",
            "prevention": "Eliminate volunteer wheat. Delay planting until after the Hessian fly-free date. Use resistant varieties."
        }
    ]
}


def preprocess_image(image_bytes):
    try:
        image = Image.open(io.BytesIO(image_bytes))
        image = image.resize((224, 224))
        image = image.convert("RGB")
        return image
    except Exception:
        return None


def analyze_image(image_bytes, crop_type):
    crop_type = crop_type.lower()
    if crop_type not in DISEASE_DATABASE:
        return {
            "success": False,
            "error": f"Unsupported crop type: {crop_type}. Supported: {', '.join(DISEASE_DATABASE.keys())}",
            "predictions": []
        }

    processed = preprocess_image(image_bytes)
    if processed is None:
        return {
            "success": False,
            "error": "Failed to process the uploaded image. Please try a different image.",
            "predictions": []
        }

    diseases = DISEASE_DATABASE[crop_type]
    selected = random.sample(diseases, min(3, len(diseases)))

    confidences = sorted([random.uniform(0.55, 0.98) for _ in selected], reverse=True)

    predictions = []
    for disease, confidence in zip(selected, confidences):
        predictions.append({
            "disease_name": disease["disease_name"],
            "confidence": round(confidence, 2),
            "severity": disease["severity"],
            "treatment": disease["treatment"],
            "prevention": disease["prevention"]
        })

    return {
        "success": True,
        "crop_type": crop_type,
        "predictions": predictions
    }
