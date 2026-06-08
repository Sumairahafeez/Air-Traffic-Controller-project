# 📡 ATC·VISION: Air Traffic Control Pipeline System

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.1+-EE4C2C.svg?style=flat-square&logo=pytorch&logoColor=white)](https://pytorch.org)
[![YOLOv8](https://img.shields.io/badge/YOLO-v8m--seg-00ffff.svg?style=flat-square&logo=ultralytics&logoColor=black)](https://github.com/ultralytics/ultralytics)
[![React](https://img.shields.io/badge/React-19-61DAFB.svg?style=flat-square&logo=react&logoColor=black)](https://react.dev)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED.svg?style=flat-square&logo=docker&logoColor=white)](https://huggingface.co/docs/hub/spaces-sdks-docker)

A unified computer vision pipeline designed for real-time runway monitoring, offering joint aircraft **object detection**, **instance segmentation**, and **fine-grained classifier naming** (ResNet-50 trained on 8 custom aircraft types). Features standard compliance with Hugging Face Spaces Docker deployment and automatic PDF report compilation.

---

## 🚀 Key Features

* **Unified AI Pipeline**: Combines pretrained YOLOv8m-seg (for object localization & masking) with a custom ResNet-50 classifier (for fine-grained aircraft type prediction).
* **Step-by-Step Segmentation Visualizer**: Detailed image stage rendering highlighting original, preprocessed grayscale, raw binary masks, overlay masks, and final contours.
* **On-Demand PDF Report Generator**: Generates comprehensive PDF reports with custom metadata, key metrics cards, data distribution summaries, and tables for both the full pipeline and individual tasks.
* **Hugging Face Spaces Optimized**: Standardized Docker orchestration equipped with Gunicorn serving, OpenCV system dependencies, and custom port configuration (7860).

---

## 📁 Repository Structure

```text
Air-Traffic-Controller-project/
├── atc-project/
│   ├── backend/
│   │   ├── outputs/              # Classifier metrics, training plots, and best weights
│   │   ├── app.py                # Flask main application & endpoints
│   │   ├── config.py             # Inference/deployment configuration parameters
│   │   ├── report_generator.py   # PDF compilation helper (ReportLab flowables)
│   │   ├── utils.py              # Visualizers & deep learning predictors
│   │   ├── requirements.txt      # Backend dependencies (PyTorch, Ultralytics, etc.)
│   │   └── Dockerfile            # Deployment-ready Docker image configuration
│   └── frontend/
│       ├── public/               # Static assets & minimalist airplane favicon
│       ├── src/
│       │   ├── sections/         # Application tabs (Dashboard, Detection, etc.)
│       │   ├── api.js            # Fetch API client pointing to production endpoints
│       │   └── App.jsx           # Tab navigator & state manager
│       └── package.json          # Node dependencies
└── README.md                     # Project documentation
```

---

## 🛠️ Installation & Setup

### 1. Backend Setup

Prerequisites: Python 3.9+ installed.

```bash
# Navigate to the backend directory
cd atc-project/backend

# Create a virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the Flask backend locally (port 7860)
python app.py
```

### 2. Frontend Setup

Prerequisites: Node.js (v18+) installed.

```bash
# Navigate to the frontend directory
cd atc-project/frontend

# Install node modules
npm install

# Start the Vite development server (port 5173)
npm run dev
```

Visit the application at `http://localhost:5173/`.

---

## 🐳 Docker Deployment (Hugging Face Spaces)

The backend is fully optimized for **Hugging Face Spaces** Docker deployment. It automatically handles permissions, system libraries for graphics drivers, and is configured to bind to port `7860`.

To build and run the Docker container locally:
```bash
cd atc-project/backend
docker build -t atc-vision-backend .
docker run -p 7860:7860 atc-vision-backend
```

---

## 📄 Automated PDF Reporting Engine

The PDF compiler (`report_generator.py`) generates tailored report layouts for different pipeline activities:

| Report Type | Included Sections | Key Statistics Provided |
| :--- | :--- | :--- |
| **Full Report** | Classification $\rightarrow$ Detection $\rightarrow$ Segmentation | Combined statistics, crop label alternatives, bbox coordinate matrices, step-by-step segment maps. |
| **Classification Only** | Single Crop + Confidence Bar Chart | Primary predictions, category mapping, full probability breakdown. |
| **Detection Only** | BBox Outlines + Coordinate Listing | Box counts, average confidence, smallest/largest box sizes. |
| **Segmentation Only** | Preprocessing $\rightarrow$ Mask $\rightarrow$ Contour Stages | Instance region sizes, coverage percentage of image space. |

---

## 🎨 Theme & Aesthetics

Following a strict **minimalist black & white theme**, the UI offers:
* **High Contrast Visualization**: Neon green bounding boxes (`thickness=3`) ensure visibility against varying asphalt and apron runways.
* **Micro-interactions**: Hover expansions, smooth transition tables, and active radar sweep overlays.
