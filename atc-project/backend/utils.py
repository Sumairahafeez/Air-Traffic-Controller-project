"""Image helpers, classifier loading, and visualization utilities.

Visualizations use a black & white aesthetic to match the frontend: white
boxes/outlines with black label backgrounds and white text.
"""
import base64

import cv2
import numpy as np
import torch
import torch.nn as nn
from PIL import Image
from torchvision import models, transforms

# ImageNet normalization (the classifier was fine-tuned from ImageNet weights).
_MEAN = [0.485, 0.456, 0.406]
_STD = [0.229, 0.224, 0.225]


# ---------------------------------------------------------------------------
# Image <-> base64 / sizing
# ---------------------------------------------------------------------------
def load_image_from_base64(image_data):
    """Decode a data-URL or raw base64 string into a BGR numpy image."""
    if image_data is None:
        return None
    if ',' in image_data:
        image_data = image_data.split(',', 1)[1]
    try:
        image_bytes = base64.b64decode(image_data)
        image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
    except Exception:
        return None
    return image


def image_to_base64(image):
    """Encode a BGR numpy image as a JPEG data URL."""
    ok, buffer = cv2.imencode('.jpg', image, [cv2.IMWRITE_JPEG_QUALITY, 92])
    if not ok:
        return None
    return 'data:image/jpeg;base64,' + base64.b64encode(buffer).decode()


def resize_image(image, max_size=1600):
    h, w = image.shape[:2]
    if max(h, w) > max_size:
        scale = max_size / max(h, w)
        image = cv2.resize(image, (int(w * scale), int(h * scale)),
                           interpolation=cv2.INTER_AREA)
    return image


# ---------------------------------------------------------------------------
# Classifier
# ---------------------------------------------------------------------------
class AircraftClassifier:
    """Wraps the trained ResNet50 checkpoint and its metadata."""

    def __init__(self, checkpoint_path, device='cpu'):
        self.device = device
        ckpt = torch.load(checkpoint_path, map_location=device, weights_only=False)

        self.class_names = ckpt['class_names']
        self.category_map = ckpt.get('category_map', {})
        self.image_size = int(ckpt.get('image_size', 224))
        num_classes = len(self.class_names)

        model = models.resnet50(weights=None)
        model.fc = nn.Linear(model.fc.in_features, num_classes)
        model.load_state_dict(ckpt['model_state_dict'])
        model.eval().to(device)
        self.model = model

        self.transform = transforms.Compose([
            transforms.Resize((self.image_size, self.image_size)),
            transforms.ToTensor(),
            transforms.Normalize(mean=_MEAN, std=_STD),
        ])

    def category_of(self, class_name):
        return self.category_map.get(class_name, 'Unknown')

    @torch.no_grad()
    def predict(self, bgr_crop, topk=3):
        """Classify a single BGR crop. Returns name/confidence/category/top-k."""
        if bgr_crop is None or bgr_crop.size == 0:
            return None
        pil = Image.fromarray(cv2.cvtColor(bgr_crop, cv2.COLOR_BGR2RGB))
        tensor = self.transform(pil).unsqueeze(0).to(self.device)
        logits = self.model(tensor)
        probs = torch.softmax(logits, dim=1)[0]

        conf, idx = torch.max(probs, 0)
        k = min(topk, len(self.class_names))
        top_conf, top_idx = torch.topk(probs, k)

        name = self.class_names[int(idx)]
        return {
            'class_name': name,
            'class_idx': int(idx),
            'confidence': float(conf),
            'category': self.category_of(name),
            'top_k': [
                {
                    'class_name': self.class_names[int(i)],
                    'confidence': float(c),
                    'category': self.category_of(self.class_names[int(i)]),
                }
                for c, i in zip(top_conf, top_idx)
            ],
            'all_probabilities': {
                self.class_names[i]: float(p) for i, p in enumerate(probs)
            },
        }


# ---------------------------------------------------------------------------
# Drawing (black & white style)
# ---------------------------------------------------------------------------
_WHITE = (255, 255, 255)
_BLACK = (0, 0, 0)
_GREEN = (0, 255, 0)


def _draw_label(image, text, x, y):
    """Draw white text on a solid black box anchored above (x, y)."""
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 0.5
    thickness = 1
    (tw, th), baseline = cv2.getTextSize(text, font, scale, thickness)
    top = max(0, y - th - baseline - 6)
    cv2.rectangle(image, (x, top), (x + tw + 8, top + th + baseline + 6), _BLACK, -1)
    cv2.putText(image, text, (x + 4, top + th + 2), font, scale, _WHITE, thickness,
                cv2.LINE_AA)


def draw_detections(image, detections):
    """Draw boxes + labels (name + confidence) for each detection."""
    out = image.copy()
    for det in detections:
        x, y, w, h = det['box']
        cv2.rectangle(out, (x, y), (x + w, y + h), _GREEN, 3)
        cv2.rectangle(out, (x, y), (x + w, y + h), _BLACK, 1)  # thin inner edge
        label = det.get('label') or det.get('class') or 'Aircraft'
        conf = det.get('classification_confidence') or det.get('detection_confidence', 0)
        _draw_label(out, f'{label} {conf * 100:.0f}%', x, y)
    return out


def build_segmentation_stages(image, results, class_names=None, detections=None):
    """Produce a step-by-step visualization of the segmentation pipeline.

    Returns a list of {'title', 'description', 'image'} stages plus stats.
    """
    h, w = image.shape[:2]
    stages = []

    # Stage 1: original
    stages.append({
        'title': '1. Input Image',
        'description': 'Original image fed into the segmentation model.',
        'image': image.copy(),
    })

    # Stage 2: grayscale (preprocessing intuition)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    stages.append({
        'title': '2. Preprocessing',
        'description': 'Grayscale view — the model normalizes pixels before inference.',
        'image': cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR),
    })

    masks = results[0].masks
    instance_stats = []

    if masks is None or len(masks.data) == 0:
        # No masks: still return the early stages so the UI can explain.
        combined_binary = np.zeros((h, w), dtype=np.uint8)
    else:
        combined_binary = np.zeros((h, w), dtype=np.uint8)
        overlay = image.copy()
        contour_img = image.copy()
        # Distinct grayscale shades for instances (B&W theme).
        shades = np.linspace(80, 255, len(masks.data)).astype(np.uint8)

        boxes = results[0].boxes
        for i, mask in enumerate(masks.data):
            m = mask.cpu().numpy()
            m = cv2.resize(m, (w, h), interpolation=cv2.INTER_LINEAR)
            binary = (m > 0.5).astype(np.uint8)
            combined_binary = np.maximum(combined_binary, binary * 255)

            shade = int(shades[i])
            colored = np.zeros_like(image)
            colored[binary > 0] = (shade, shade, shade)
            overlay = cv2.addWeighted(overlay, 1.0, colored, 0.45, 0)

            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL,
                                           cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(contour_img, contours, -1, _WHITE, 2)

            area_px = int(binary.sum())
            name = None
            if class_names is not None and boxes is not None and i < len(boxes):
                cls_id = int(boxes.cls[i])
                name = class_names.get(cls_id, str(cls_id)) if isinstance(
                    class_names, dict) else None
            instance_stats.append({
                'id': i,
                'area_px': area_px,
                'coverage_pct': round(area_px / (h * w) * 100, 2),
                'label': name,
            })

        stages.append({
            'title': '3. Instance Masks',
            'description': 'Binary masks for every detected object combined into one map.',
            'image': cv2.cvtColor(combined_binary, cv2.COLOR_GRAY2BGR),
        })
        stages.append({
            'title': '4. Mask Overlay',
            'description': 'Masks overlaid on the original image, one shade per instance.',
            'image': overlay,
        })
        stages.append({
            'title': '5. Contours',
            'description': 'Outlines traced around each segmented region.',
            'image': contour_img,
        })

    total_coverage = round(float((combined_binary > 0).sum()) / (h * w) * 100, 2)
    stats = {
        'instances': len(instance_stats),
        'total_coverage_pct': total_coverage,
        'per_instance': instance_stats,
        'image_size': {'width': w, 'height': h},
    }
    return stages, stats
