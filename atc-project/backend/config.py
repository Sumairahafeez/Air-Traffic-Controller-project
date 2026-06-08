import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Project root is two levels up from backend/ (atc-project/ -> project root)
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..', '..'))


class Config:
    DEBUG = True
    PORT = 7860

    # --- Models ---
    # Pretrained COCO model used for BOTH detection and segmentation.
    DETECTION_MODEL = os.path.join(BASE_DIR, 'yolov8m-seg.pt')
    # Your trained aircraft-type classifier (8 classes).
    CLASSIFICATION_CHECKPOINT = os.path.join(BASE_DIR, 'outputs', 'resnet50_best.pth')

    # Folder that holds metrics + plots produced during training/evaluation.
    OUTPUTS_DIR = os.path.join(BASE_DIR, 'outputs')

    # --- Inference params ---
    DETECTION_CONFIDENCE = 0.35       # YOLO box confidence threshold
    SEGMENTATION_CONFIDENCE = 0.35
    MAX_IMAGE_SIZE = 1600             # downscale huge uploads before inference

    # COCO class id for "airplane". Detection focuses on aircraft on the runway.
    COCO_AIRPLANE_CLASS = 4
    # If True, only airplane detections are kept; other COCO objects are ignored.
    DETECT_AIRPLANES_ONLY = True

    # Minimum crop size (px) before a detection is worth classifying.
    MIN_CROP_SIZE = 16

    CORS_ORIGINS = ['*']
