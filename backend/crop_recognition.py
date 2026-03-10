import numpy as np
from PIL import Image, ImageFilter
import io
from sklearn.ensemble import RandomForestClassifier
from backend.ai_disease import analyze_image

def _generate_plant_training_data(n_samples=600):
    np.random.seed(42)
    features = []
    labels = []

    for _ in range(n_samples):
        r_mean = np.random.uniform(30, 140)
        g_mean = np.random.uniform(80, 210)
        b_mean = np.random.uniform(20, 120)
        r_std = np.random.uniform(5, 55)
        g_std = np.random.uniform(5, 55)
        b_std = np.random.uniform(5, 50)
        total = r_mean + g_mean + b_mean + 1e-6
        green_ratio = g_mean / total
        green_ratio = np.clip(green_ratio + np.random.normal(0, 0.02), 0.34, 0.70)
        hue_mean = np.random.uniform(60, 150)
        hue_std = np.random.uniform(1, 30)
        sat_mean = np.random.uniform(0.20, 0.85)
        sat_std = np.random.uniform(0.02, 0.22)
        edge_density = np.random.uniform(0.03, 0.40)
        contrast = np.random.uniform(5, 90)
        uniformity = np.random.uniform(0.01, 0.35)
        aspect_ratio = np.random.uniform(0.5, 1.8)
        symmetry = np.random.uniform(0.3, 0.98)

        features.append([r_mean, g_mean, b_mean, r_std, g_std, b_std,
                         green_ratio, hue_mean, hue_std, sat_mean, sat_std,
                         edge_density, contrast, uniformity, aspect_ratio, symmetry])
        labels.append(1)

    n_urban = n_samples // 3
    for _ in range(n_urban):
        r_mean = np.random.uniform(100, 200)
        g_mean = np.random.uniform(95, 190)
        b_mean = np.random.uniform(95, 195)
        r_std = np.random.uniform(5, 45)
        g_std = np.random.uniform(5, 45)
        b_std = np.random.uniform(5, 45)
        total = r_mean + g_mean + b_mean + 1e-6
        green_ratio = g_mean / total
        hue_mean = np.random.choice([np.random.uniform(0, 50), np.random.uniform(160, 360)])
        hue_std = np.random.uniform(10, 70)
        sat_mean = np.random.uniform(0.01, 0.20)
        sat_std = np.random.uniform(0.005, 0.10)
        edge_density = np.random.uniform(0.10, 0.50)
        contrast = np.random.uniform(15, 75)
        uniformity = np.random.uniform(0.02, 0.15)
        aspect_ratio = np.random.uniform(0.4, 2.0)
        symmetry = np.random.uniform(0.3, 0.95)

        features.append([r_mean, g_mean, b_mean, r_std, g_std, b_std,
                         green_ratio, hue_mean, hue_std, sat_mean, sat_std,
                         edge_density, contrast, uniformity, aspect_ratio, symmetry])
        labels.append(0)

    n_doc = n_samples // 3
    for _ in range(n_doc):
        r_mean = np.random.uniform(170, 252)
        g_mean = np.random.uniform(170, 252)
        b_mean = np.random.uniform(170, 252)
        r_std = np.random.uniform(2, 25)
        g_std = np.random.uniform(2, 25)
        b_std = np.random.uniform(2, 25)
        total = r_mean + g_mean + b_mean + 1e-6
        green_ratio = g_mean / total
        hue_mean = np.random.uniform(0, 80)
        hue_std = np.random.uniform(0.5, 25)
        sat_mean = np.random.uniform(0.0, 0.12)
        sat_std = np.random.uniform(0.0, 0.06)
        edge_density = np.random.uniform(0.01, 0.18)
        contrast = np.random.uniform(2, 30)
        uniformity = np.random.uniform(0.05, 0.35)
        aspect_ratio = np.random.uniform(0.6, 1.6)
        symmetry = np.random.uniform(0.5, 0.99)

        features.append([r_mean, g_mean, b_mean, r_std, g_std, b_std,
                         green_ratio, hue_mean, hue_std, sat_mean, sat_std,
                         edge_density, contrast, uniformity, aspect_ratio, symmetry])
        labels.append(0)

    n_people = n_samples - n_urban - n_doc
    for _ in range(n_people):
        r_mean = np.random.uniform(120, 220)
        g_mean = np.random.uniform(80, 175)
        b_mean = np.random.uniform(60, 155)
        r_std = np.random.uniform(8, 50)
        g_std = np.random.uniform(8, 45)
        b_std = np.random.uniform(8, 45)
        total = r_mean + g_mean + b_mean + 1e-6
        green_ratio = g_mean / total
        hue_mean = np.random.uniform(5, 45)
        hue_std = np.random.uniform(2, 30)
        sat_mean = np.random.uniform(0.15, 0.55)
        sat_std = np.random.uniform(0.03, 0.18)
        edge_density = np.random.uniform(0.08, 0.45)
        contrast = np.random.uniform(15, 85)
        uniformity = np.random.uniform(0.01, 0.10)
        aspect_ratio = np.random.uniform(0.3, 1.9)
        symmetry = np.random.uniform(0.25, 0.75)

        features.append([r_mean, g_mean, b_mean, r_std, g_std, b_std,
                         green_ratio, hue_mean, hue_std, sat_mean, sat_std,
                         edge_density, contrast, uniformity, aspect_ratio, symmetry])
        labels.append(0)

    return np.array(features), np.array(labels)


def _generate_crop_training_data(n_per_class=200):
    np.random.seed(123)
    features = []
    labels = []
    crop_profiles = {
        "maize": {
            "r_mean": (35, 120), "g_mean": (100, 210), "b_mean": (20, 90),
            "r_std": (5, 45), "g_std": (5, 50), "b_std": (5, 40),
            "green_ratio": (0.42, 0.65),
            "hue_mean": (80, 140), "hue_std": (1, 25),
            "sat_mean": (0.40, 0.80), "sat_std": (0.02, 0.20),
            "edge_density": (0.05, 0.30), "contrast": (5, 70),
            "uniformity": (0.01, 0.30),
            "aspect_ratio": (0.4, 1.2), "symmetry": (0.30, 0.97)
        },
        "tomatoes": {
            "r_mean": (90, 210), "g_mean": (50, 150), "b_mean": (25, 95),
            "r_std": (10, 60), "g_std": (8, 50), "b_std": (5, 45),
            "green_ratio": (0.20, 0.42),
            "hue_mean": (0, 40), "hue_std": (2, 35),
            "sat_mean": (0.40, 0.90), "sat_std": (0.03, 0.25),
            "edge_density": (0.05, 0.40), "contrast": (8, 90),
            "uniformity": (0.01, 0.25),
            "aspect_ratio": (0.6, 1.5), "symmetry": (0.35, 0.95)
        },
        "potatoes": {
            "r_mean": (70, 160), "g_mean": (90, 180), "b_mean": (40, 120),
            "r_std": (5, 45), "g_std": (5, 48), "b_std": (5, 40),
            "green_ratio": (0.32, 0.52),
            "hue_mean": (55, 110), "hue_std": (2, 28),
            "sat_mean": (0.20, 0.60), "sat_std": (0.02, 0.18),
            "edge_density": (0.04, 0.30), "contrast": (5, 65),
            "uniformity": (0.01, 0.28),
            "aspect_ratio": (0.7, 1.6), "symmetry": (0.35, 0.95)
        },
        "wheat": {
            "r_mean": (110, 220), "g_mean": (110, 210), "b_mean": (40, 130),
            "r_std": (5, 40), "g_std": (5, 42), "b_std": (5, 35),
            "green_ratio": (0.30, 0.48),
            "hue_mean": (50, 95), "hue_std": (1, 20),
            "sat_mean": (0.25, 0.65), "sat_std": (0.02, 0.16),
            "edge_density": (0.08, 0.42), "contrast": (5, 55),
            "uniformity": (0.02, 0.25),
            "aspect_ratio": (0.3, 1.0), "symmetry": (0.40, 0.95)
        }
    }

    crop_names = ["maize", "tomatoes", "potatoes", "wheat"]
    for idx, crop in enumerate(crop_names):
        p = crop_profiles[crop]
        for _ in range(n_per_class):
            row = []
            for key in ["r_mean", "g_mean", "b_mean", "r_std", "g_std", "b_std",
                         "green_ratio", "hue_mean", "hue_std", "sat_mean", "sat_std",
                         "edge_density", "contrast", "uniformity", "aspect_ratio", "symmetry"]:
                lo, hi = p[key]
                row.append(np.random.uniform(lo, hi))
            features.append(row)
            labels.append(idx)

    return np.array(features), np.array(labels), crop_names


FEATURE_NAMES = ["r_mean", "g_mean", "b_mean", "r_std", "g_std", "b_std",
                 "green_ratio", "hue_mean", "hue_std", "sat_mean", "sat_std",
                 "edge_density", "contrast", "uniformity", "aspect_ratio", "symmetry"]

_plant_X, _plant_y = _generate_plant_training_data(600)
plant_classifier = RandomForestClassifier(n_estimators=80, random_state=42, n_jobs=-1)
plant_classifier.fit(_plant_X, _plant_y)

_crop_X, _crop_y, CROP_NAMES = _generate_crop_training_data(200)
crop_classifier = RandomForestClassifier(n_estimators=80, random_state=42, n_jobs=-1)
crop_classifier.fit(_crop_X, _crop_y)


def _sobel_edge_density(gray_arr):
    kx = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float32)
    ky = kx.T
    from scipy.signal import convolve2d
    gx = convolve2d(gray_arr, kx, mode='same', boundary='symm')
    gy = convolve2d(gray_arr, ky, mode='same', boundary='symm')
    magnitude = np.sqrt(gx ** 2 + gy ** 2)
    threshold = np.mean(magnitude) + np.std(magnitude)
    return float(np.mean(magnitude > threshold))


def extract_features(image_bytes):
    try:
        image = Image.open(io.BytesIO(image_bytes))
    except Exception:
        return None

    image = image.convert("RGB").resize((224, 224))
    arr = np.array(image, dtype=np.float32)

    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    r_mean, g_mean, b_mean = float(np.mean(r)), float(np.mean(g)), float(np.mean(b))
    r_std, g_std, b_std = float(np.std(r)), float(np.std(g)), float(np.std(b))

    total = r_mean + g_mean + b_mean + 1e-6
    green_ratio = g_mean / total

    hsv_image = image.convert("HSV")
    hsv_arr = np.array(hsv_image, dtype=np.float32)
    h, s, v = hsv_arr[:, :, 0], hsv_arr[:, :, 1], hsv_arr[:, :, 2]
    hue_mean = float(np.mean(h)) * (360.0 / 255.0)
    hue_std = float(np.std(h)) * (360.0 / 255.0)
    sat_mean = float(np.mean(s)) / 255.0
    sat_std = float(np.std(s)) / 255.0

    gray = np.mean(arr, axis=2)
    edge_density = _sobel_edge_density(gray)

    contrast = float(np.std(gray))

    hist, _ = np.histogram(gray, bins=32, range=(0, 256))
    hist = hist / hist.sum()
    uniformity = float(np.sum(hist ** 2))

    h_img, w_img = arr.shape[:2]
    aspect_ratio = float(w_img) / float(h_img)

    left_half = gray[:, :w_img // 2]
    right_half = np.fliplr(gray[:, (w_img - w_img // 2):])
    min_w = min(left_half.shape[1], right_half.shape[1])
    if min_w > 0:
        diff = np.abs(left_half[:, :min_w] - right_half[:, :min_w])
        symmetry = 1.0 - float(np.mean(diff) / 255.0)
    else:
        symmetry = 0.5

    feature_dict = {
        "r_mean": round(r_mean, 2), "g_mean": round(g_mean, 2), "b_mean": round(b_mean, 2),
        "r_std": round(r_std, 2), "g_std": round(g_std, 2), "b_std": round(b_std, 2),
        "green_ratio": round(green_ratio, 4),
        "hue_mean": round(hue_mean, 2), "hue_std": round(hue_std, 2),
        "sat_mean": round(sat_mean, 4), "sat_std": round(sat_std, 4),
        "edge_density": round(edge_density, 4),
        "contrast": round(contrast, 2),
        "uniformity": round(uniformity, 4),
        "aspect_ratio": round(aspect_ratio, 4),
        "symmetry": round(symmetry, 4)
    }
    return feature_dict


def _features_to_vector(feat_dict):
    return np.array([[feat_dict[k] for k in FEATURE_NAMES]])


def classify_plant(image_bytes):
    feat = extract_features(image_bytes)
    if feat is None:
        return {"is_plant": False, "confidence": 0.0, "features": {},
                "error": "Failed to process image"}

    vec = _features_to_vector(feat)
    proba = plant_classifier.predict_proba(vec)[0]
    class_idx = int(np.argmax(proba))
    is_plant = class_idx == 1
    confidence = float(proba[class_idx])

    return {
        "is_plant": is_plant,
        "confidence": round(confidence, 4),
        "features": feat
    }


def identify_crop(image_bytes):
    feat = extract_features(image_bytes)
    if feat is None:
        return {"crop_type": "unknown", "confidence": 0.0, "all_predictions": [],
                "error": "Failed to process image"}

    vec = _features_to_vector(feat)
    proba = crop_classifier.predict_proba(vec)[0]
    best_idx = int(np.argmax(proba))
    best_crop = CROP_NAMES[best_idx]
    confidence = float(proba[best_idx])

    all_predictions = []
    for i, name in enumerate(CROP_NAMES):
        all_predictions.append({
            "crop_type": name,
            "confidence": round(float(proba[i]), 4)
        })
    all_predictions.sort(key=lambda x: x["confidence"], reverse=True)

    return {
        "crop_type": best_crop,
        "confidence": round(confidence, 4),
        "all_predictions": all_predictions
    }


def full_analysis(image_bytes):
    plant_result = classify_plant(image_bytes)

    if plant_result.get("error"):
        return {
            "success": False,
            "error": plant_result["error"],
            "plant_classification": plant_result,
            "crop_identification": None,
            "disease_analysis": None
        }

    if not plant_result["is_plant"]:
        return {
            "success": True,
            "is_plant": False,
            "plant_classification": plant_result,
            "crop_identification": None,
            "disease_analysis": None
        }

    crop_result = identify_crop(image_bytes)
    disease_result = analyze_image(image_bytes, crop_result["crop_type"])

    return {
        "success": True,
        "is_plant": True,
        "plant_classification": plant_result,
        "crop_identification": crop_result,
        "disease_analysis": disease_result
    }
