# ATC·Vision — Air Traffic Control Vision System

A unified web app for aircraft **detection**, **classification**, and **segmentation**.

| Capability      | Model                              | Notes |
|-----------------|------------------------------------|-------|
| Detection       | YOLOv8m-seg (pretrained, COCO)     | Finds aircraft, then names each box via the trained classifier (hybrid). |
| Segmentation    | YOLOv8m-seg (pretrained, COCO)     | Step-by-step pipeline: input → preprocess → masks → overlay → contours. |
| Classification  | **ResNet-50 (trained, 8 classes)** | `outputs/resnet50_best.pth` — ATR, Airbus, Boeing, C130, F16, Grob, KAI, Sukhoi (98.97% test accuracy). |

## Project layout
```
atc-project/
  backend/        Flask API (app.py, utils.py, config.py)
  frontend/       React + Vite single-page app (B&W theme, tabbed sections)
../outputs/       Trained checkpoint + metrics + plots (read by the backend)
```

## Run

**1. Backend** (from `backend/`):
```powershell
pip install -r requirements.txt   # first time only
python app.py                     # serves http://localhost:5000
```

**2. Frontend** (from `frontend/`, in a second terminal):
```powershell
npm install                       # first time only
npm run dev                       # serves http://localhost:5173
```

Open http://localhost:5173. The Dashboard shows backend status; if it reads
"backend offline", make sure step 1 is running.

## API
| Method | Route                         | Purpose |
|--------|-------------------------------|---------|
| GET    | `/health`                     | Status + class list |
| POST   | `/classify`                   | Single aircraft → type, confidence, category, full probabilities |
| POST   | `/detect`                     | Runway image → boxes named by the classifier (position, size, top-k) |
| POST   | `/segment`                    | Image → ordered segmentation stages + per-instance stats |
| POST   | `/analyze`                    | Combined detect + classify + segment |
| GET    | `/analytics`                  | Trained-model metrics (accuracy, per-class report) |
| GET    | `/analytics/plot/<file>`      | Serves confusion matrix / class distribution PNGs |

POST bodies are `{ "image": "<data-url base64>" }`.
