# Configuration for Lock-On System

# ===== YOLO PERSON DETECTION =====
YOLO_MODEL = 'yolov8n.pt'  # nano = fastest, small = balanced, medium = accurate
YOLO_CONFIDENCE = 0.5  # 0-1, lower = more detections but more false positives
YOLO_IOU = 0.45  # Intersection over Union threshold
MIN_PERSON_WIDTH = 20  # Minimum person width in pixels
MIN_PERSON_HEIGHT = 50  # Minimum person height in pixels

# Smoothing
MOUSE_SMOOTHING = 0.7  # 0-1, higher = smoother but slower to respond

# Visual settings
SHOW_DEBUG_WINDOW = True
DEBUG_WINDOW_SCALE = 0.5  # Scale down debug window to 50% size

# Performance
FPS_TARGET = 60
SCREEN_REGION = None  # None = full screen, or (left, top, width, height) for region
