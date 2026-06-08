"""Air Traffic Control backend.

Detection + Segmentation : pretrained YOLOv8m-seg (COCO).
Classification           : trained ResNet50 (8 aircraft types) from outputs/.

Endpoints
  GET  /health
  POST /classify          single-aircraft image -> type, confidence, category, top-k
  POST /detect            runway image -> boxes named via the trained classifier
  POST /segment           runway image -> step-by-step segmentation visualization
  POST /analyze           combined detect + segment + classify
  GET  /analytics         trained-model metrics (JSON)
  GET  /analytics/plot/<name>  serves the output PNGs (confusion matrix, etc.)
"""
import json
import os

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from ultralytics import YOLO

from config import Config
from utils import (AircraftClassifier, build_segmentation_stages,
                   draw_detections, image_to_base64, load_image_from_base64,
                   resize_image)

app = Flask(__name__)
CORS(app, origins=Config.CORS_ORIGINS)

print('Loading models...')
yolo = YOLO(Config.DETECTION_MODEL)
COCO_NAMES = yolo.names  # {id: name}
classifier = AircraftClassifier(Config.CLASSIFICATION_CHECKPOINT)
print(f'Models loaded. Classifier classes: {classifier.class_names}')


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------
def _read_image_from_request():
    """Return (image, error_response). image is None on failure."""
    data = request.get_json(silent=True) or {}
    image = load_image_from_base64(data.get('image'))
    if image is None:
        return None, (jsonify({'error': 'Invalid or missing image'}), 400)
    return resize_image(image, Config.MAX_IMAGE_SIZE), None


def _run_detection(image):
    """Run YOLO detection, classify each airplane crop, return detection dicts."""
    results = yolo(image, conf=Config.DETECTION_CONFIDENCE, verbose=False)
    detections = []
    boxes = results[0].boxes
    if boxes is None:
        return detections, results

    h, w = image.shape[:2]
    for i, box in enumerate(boxes):
        cls_id = int(box.cls[0])
        if Config.DETECT_AIRPLANES_ONLY and cls_id != Config.COCO_AIRPLANE_CLASS:
            continue
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)
        bw, bh = x2 - x1, y2 - y1
        det = {
            'id': len(detections),
            'box': [x1, y1, bw, bh],
            'center': [x1 + bw // 2, y1 + bh // 2],
            'area_px': bw * bh,
            'detection_confidence': float(box.conf[0]),
            'coco_class': COCO_NAMES.get(cls_id, str(cls_id)),
        }

        # Hybrid step: name the plane using the trained classifier.
        if bw >= Config.MIN_CROP_SIZE and bh >= Config.MIN_CROP_SIZE:
            crop = image[y1:y2, x1:x2]
            pred = classifier.predict(crop, topk=3)
            if pred:
                det.update({
                    'label': pred['class_name'],
                    'classification_confidence': pred['confidence'],
                    'category': pred['category'],
                    'top_k': pred['top_k'],
                })
        det.setdefault('label', 'Aircraft')
        detections.append(det)
    return detections, results


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'running',
        'detector': 'yolov8m-seg',
        'classifier': 'resnet50 (trained)',
        'classes': classifier.class_names,
    })


@app.route('/classify', methods=['POST'])
def classify():
    image, err = _read_image_from_request()
    if err:
        return err
    pred = classifier.predict(image, topk=len(classifier.class_names))
    if pred is None:
        return jsonify({'error': 'Could not classify image'}), 400
    return jsonify({
        'prediction': pred,
        'classes': classifier.class_names,
        'category_map': classifier.category_map,
    })


@app.route('/detect', methods=['POST'])
def detect():
    image, err = _read_image_from_request()
    if err:
        return err
    detections, _ = _run_detection(image)
    annotated = draw_detections(image, detections)
    confs = [d['detection_confidence'] for d in detections]
    return jsonify({
        'detections': detections,
        'image': image_to_base64(annotated),
        'summary': {
            'total': len(detections),
            'avg_confidence': round(sum(confs) / len(confs), 4) if confs else 0,
        },
    })


@app.route('/segment', methods=['POST'])
def segment():
    image, err = _read_image_from_request()
    if err:
        return err
    results = yolo(image, conf=Config.SEGMENTATION_CONFIDENCE, verbose=False)
    stages, stats = build_segmentation_stages(image, results, class_names=COCO_NAMES)
    return jsonify({
        'stages': [
            {'title': s['title'], 'description': s['description'],
             'image': image_to_base64(s['image'])}
            for s in stages
        ],
        'stats': stats,
    })


@app.route('/analyze', methods=['POST'])
def analyze():
    image, err = _read_image_from_request()
    if err:
        return err
    detections, results = _run_detection(image)
    annotated = draw_detections(image, detections)
    stages, seg_stats = build_segmentation_stages(image, results,
                                                  class_names=COCO_NAMES)
    return jsonify({
        'detections': detections,
        'image': image_to_base64(annotated),
        'segmentation': {
            'stats': seg_stats,
            'stages': [
                {'title': s['title'], 'description': s['description'],
                 'image': image_to_base64(s['image'])}
                for s in stages
            ],
        },
        'summary': {
            'total_aircraft': len(detections),
            'classified': sum(1 for d in detections if 'classification_confidence' in d),
            'segmented_instances': seg_stats['instances'],
        },
    })


@app.route('/analytics', methods=['GET'])
def analytics():
    metrics_path = os.path.join(Config.OUTPUTS_DIR, 'resnet50_metrics.json')
    comparison_path = os.path.join(Config.OUTPUTS_DIR, 'model_comparison.json')
    payload = {'class_names': classifier.class_names,
               'category_map': classifier.category_map}

    if os.path.exists(metrics_path):
        with open(metrics_path) as f:
            payload['metrics'] = json.load(f)
    if os.path.exists(comparison_path):
        with open(comparison_path) as f:
            payload['comparison'] = json.load(f)

    # Which plot PNGs exist (served via /analytics/plot/<name>).
    plots = {}
    for key, fname in {
        'confusion_matrix': 'resnet50_confusion_matrix.png',
        'class_distribution': 'class_distribution.png',
        'sample_images': 'sample_images.png',
    }.items():
        if os.path.exists(os.path.join(Config.OUTPUTS_DIR, fname)):
            plots[key] = f'/analytics/plot/{fname}'
    payload['plots'] = plots
    return jsonify(payload)


@app.route('/analytics/plot/<path:name>', methods=['GET'])
def analytics_plot(name):
    return send_from_directory(Config.OUTPUTS_DIR, name)


if __name__ == '__main__':
    app.run(debug=Config.DEBUG, port=Config.PORT, host='0.0.0.0')
