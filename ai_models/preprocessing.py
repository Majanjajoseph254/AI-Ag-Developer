from PIL import Image
import io


def load_image(image_bytes):
    try:
        return Image.open(io.BytesIO(image_bytes))
    except Exception:
        return None


def resize_image(image, target_size=(224, 224)):
    return image.resize(target_size, Image.LANCZOS)


def convert_to_rgb(image):
    if image.mode != "RGB":
        return image.convert("RGB")
    return image


def normalize_pixels(image):
    import numpy as np
    arr = np.array(image, dtype=np.float32) / 255.0
    return arr


def preprocess_for_model(image_bytes, target_size=(224, 224)):
    image = load_image(image_bytes)
    if image is None:
        return None
    image = convert_to_rgb(image)
    image = resize_image(image, target_size)
    return normalize_pixels(image)


def image_to_bytes(image, format="JPEG"):
    buffer = io.BytesIO()
    image.save(buffer, format=format)
    return buffer.getvalue()
