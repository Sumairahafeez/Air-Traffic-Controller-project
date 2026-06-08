# -*- coding: utf-8 -*-
"""Generate an A3 R&D poster (HTML) for the ATC Vision system.

Embeds the real evaluation metrics and the trained-model confusion matrix, then
the companion shell command renders it to PNG / PDF with headless Edge.

Design goals: fits exactly one A3 page (no clipping), large readable text,
black-and-white theme with depth (black bands, light canvas, white cards).
"""
import base64
import json
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'outputs')


def b64(path):
    with open(path, 'rb') as f:
        return 'data:image/png;base64,' + base64.b64encode(f.read()).decode()


with open(os.path.join(OUT, 'resnet50_metrics.json')) as f:
    M = json.load(f)

report = M['classification_report']
per_acc = M['per_class_accuracy']
CLASSES = ['ATR', 'Airbus', 'Boeing', 'C130', 'F16', 'Grob', 'KAI', 'Sukhoi']
CATEGORY = {
    'Airbus': 'Commercial', 'Boeing': 'Commercial', 'ATR': 'Commercial',
    'F16': 'Military', 'Sukhoi': 'Military', 'C130': 'Military',
    'Grob': 'Training', 'KAI': 'Training',
}

cm_img = b64(os.path.join(OUT, 'resnet50_confusion_matrix.png'))
uet_logo = b64(os.path.join(ROOT, 'uet_logo.png'))

total_support = int(report['weighted avg']['support'])

ACC = M['accuracy'] * 100
PREC = M['precision_weighted'] * 100
REC = M['recall_weighted'] * 100
F1 = M['f1_weighted'] * 100
INF = M['inference_time_ms_per_image']

# --- per-class accuracy bars ---
bars = ''
for c in CLASSES:
    p = per_acc[c] * 100
    bars += f'''<div class="bar"><span class="bl">{c}</span>
      <span class="bt"><span class="bf" style="width:{p:.1f}%"></span></span>
      <span class="bp">{p:.1f}%</span></div>'''

# --- per-class metrics table rows ---
rows = ''
for c in CLASSES:
    r = report[c]
    rows += f'''<tr><td><b>{c}</b></td><td class="mut">{CATEGORY[c]}</td>
      <td class="n">{r['precision']:.3f}</td><td class="n">{r['recall']:.3f}</td>
      <td class="n">{r['f1-score']:.3f}</td><td class="n">{int(r['support'])}</td></tr>'''

HTML = f'''<!DOCTYPE html><html><head><meta charset="utf-8"><style>
@page {{ size: A3 portrait; margin: 0; }}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
@media print {{ html, body {{ height: 419.5mm; overflow: hidden; }} }}
:root {{
  --ink:#0b0b0b; --soft:#3f3f3f; --faint:#7c7c7c; --line:#d7d7d7;
  --card:#ffffff; --canvas:#ececed; --accent:#0b0b0b;
}}
html,body {{ background:var(--canvas); }}
body {{
  width:297mm; height:420mm; padding:9mm 10mm; background:var(--canvas); color:var(--ink);
  font-family:"Segoe UI","Inter",Arial,sans-serif; font-size:9.4pt; line-height:1.4;
  display:flex; flex-direction:column; overflow:hidden;
}}
h1,h2,h3,h4 {{ letter-spacing:-.01em; }}
.mono {{ font-family:"Consolas",ui-monospace,monospace; }}
.mut {{ color:var(--faint); }}
b {{ font-weight:700; }}

/* eyebrow label with square bullet */
.eyebrow {{ display:flex; align-items:center; gap:2mm; font-size:8pt; text-transform:uppercase;
  letter-spacing:.14em; color:var(--ink); font-weight:800; margin-bottom:2.5mm; }}
.eyebrow::before {{ content:""; width:2.6mm; height:2.6mm; background:var(--accent); display:block; }}

/* cards */
.card {{ background:var(--card); border:.3mm solid var(--line); border-radius:2.4mm;
  padding:4mm 4.5mm; box-shadow:0 .6mm 1.6mm rgba(0,0,0,.06); }}

/* ---------- header band ---------- */
.head {{ background:var(--ink); color:#fff; padding:6mm 7mm; border-radius:2.6mm; }}
.head-top {{ display:flex; align-items:center; gap:6mm; }}
.head-logo {{ flex:none; width:26mm; height:26mm; background:#fff; border-radius:50%;
  display:flex; align-items:center; justify-content:center; box-shadow:0 0 0 1.2mm rgba(255,255,255,.12); }}
.head-logo img {{ width:22mm; height:22mm; object-fit:contain; }}
.head-mid {{ flex:1; }}
.kicker {{ font-family:"Consolas",monospace; font-weight:700; letter-spacing:.24em; font-size:9.5pt; opacity:.7; }}
.head h1 {{ font-size:27pt; line-height:1.04; margin-top:1.5mm; font-weight:800; }}
.head .sub {{ font-size:10.5pt; opacity:.82; margin-top:2.5mm; max-width:182mm; line-height:1.4; }}
.head .right {{ flex:none; text-align:right; font-size:8.8pt; opacity:.85; line-height:1.55; }}
.head .right b {{ font-size:9.6pt; opacity:1; }}
.head-div {{ height:.3mm; background:rgba(255,255,255,.22); margin:4.5mm 0 3.5mm; }}
.head-credits {{ display:flex; justify-content:space-between; gap:8mm; }}
.cred .lbl {{ font-size:7.6pt; text-transform:uppercase; letter-spacing:.16em; opacity:.55; margin-bottom:1.2mm; }}
.cred .who {{ font-size:10pt; line-height:1.5; }}
.cred .who .id {{ font-family:"Consolas",monospace; opacity:.78; font-size:8.6pt; }}
.head-credits .right-c {{ text-align:right; }}

/* ---------- body grid ---------- */
.body {{ flex:1; min-height:0; display:flex; flex-direction:column; gap:3.4mm; margin-top:3.6mm; }}
.row {{ display:grid; gap:3.4mm; }}
.r-2 {{ grid-template-columns:1fr 1fr; }}
.r-3 {{ grid-template-columns:1fr 1fr 1fr; }}
.r-ab {{ grid-template-columns:1.35fr 1fr; }}
.r-model {{ grid-template-columns:1fr 1.25fr; }}
.results {{ flex:1; min-height:0; grid-template-columns:1.1fr 1fr; }}

h3.title {{ font-size:13.5pt; margin-bottom:1.5mm; font-weight:800; }}
p {{ margin-bottom:1.6mm; }}
ul {{ padding-left:5mm; }}
li {{ margin-bottom:1.4mm; }}

/* ---------- workflow ---------- */
.flow {{ display:flex; align-items:stretch; }}
.node {{ flex:1; border:.4mm solid var(--ink); border-radius:2mm; padding:3.2mm 2.5mm; text-align:center;
  background:var(--card); display:flex; flex-direction:column; align-items:center; justify-content:flex-start; position:relative; }}
.node.dark {{ background:var(--ink); color:#fff; border-color:var(--ink); }}
.node .step {{ position:absolute; top:-3mm; left:50%; transform:translateX(-50%); width:6mm; height:6mm;
  background:var(--ink); color:#fff; border-radius:50%; font-size:8pt; font-weight:700; display:flex;
  align-items:center; justify-content:center; font-family:"Consolas",monospace; }}
.node.dark .step {{ background:#fff; color:var(--ink); }}
.node .ic {{ font-size:16pt; margin-top:1.5mm; }}
.node .t {{ font-weight:800; font-size:10pt; margin-top:1mm; }}
.node .d {{ font-size:8pt; color:var(--soft); margin-top:1mm; line-height:1.3; }}
.node.dark .d {{ color:#d2d2d2; }}
.arrow {{ display:flex; align-items:center; justify-content:center; padding:0 1.6mm; font-size:15pt; font-weight:800; }}
.flow-note {{ font-size:8.4pt; color:var(--soft); margin-top:3mm; text-align:center; }}

/* ---------- metric tiles ---------- */
.tiles {{ display:grid; grid-template-columns:repeat(4,1fr); gap:4mm; }}
.tile {{ background:var(--card); border:.3mm solid var(--line); border-radius:2.4mm; padding:3.5mm 4mm;
  position:relative; overflow:hidden; box-shadow:0 .6mm 1.6mm rgba(0,0,0,.06); }}
.tile::before {{ content:""; position:absolute; top:0; left:0; right:0; height:1.6mm; background:var(--ink); }}
.tile .v {{ font-family:"Consolas",monospace; font-weight:700; font-size:21pt; line-height:1; margin-top:1.5mm; }}
.tile .l {{ font-size:8pt; text-transform:uppercase; letter-spacing:.1em; color:var(--faint); margin-top:2mm; }}

/* ---------- table ---------- */
table {{ width:100%; border-collapse:collapse; font-size:8.7pt; }}
th,td {{ text-align:left; padding:1.25mm 2mm; border-bottom:.25mm solid var(--line); }}
th {{ font-size:7.6pt; text-transform:uppercase; letter-spacing:.06em; color:var(--faint); }}
td.n,th.n {{ text-align:right; font-family:"Consolas",monospace; }}
tbody tr:nth-child(even) {{ background:#f6f6f6; }}
tr:last-child td {{ border-bottom:none; }}
tfoot td {{ border-top:.5mm solid var(--ink); font-weight:700; background:#fff; }}

/* ---------- key-value ---------- */
.model-grid {{ display:grid; grid-template-columns:repeat(3,1fr); column-gap:8mm; }}
.kv {{ display:flex; justify-content:space-between; gap:3mm; font-size:9.4pt; padding:1.5mm 0; border-bottom:.25mm dotted var(--line); }}
.kv b {{ font-family:"Consolas",monospace; text-align:right; }}
.tags {{ margin-top:3mm; display:flex; align-items:center; flex-wrap:wrap; gap:1.4mm; }}
.tag {{ display:inline-block; background:var(--ink); color:#fff; border-radius:6mm; padding:.9mm 3mm; font-size:8.4pt; }}
.tagnote {{ font-size:8.4pt; color:var(--faint); margin-left:2mm; }}

/* ---------- bars ---------- */
.barwrap {{ flex:1; min-height:0; display:flex; flex-direction:column; justify-content:space-between; overflow:hidden; }}
.bar {{ display:grid; grid-template-columns:15mm 1fr 13mm; align-items:center; gap:2.5mm; font-size:8.8pt; }}
.bl {{ font-weight:700; }}
.bt {{ height:3.6mm; background:#e6e6e6; border-radius:2mm; overflow:hidden; }}
.bf {{ display:block; height:100%; background:var(--ink); border-radius:2mm; }}
.bp {{ text-align:right; font-family:"Consolas",monospace; }}

/* ---------- confusion matrix (flexes to fit) ---------- */
.results .plot {{ display:flex; flex-direction:column; min-height:0; }}
.results .plot .imgbox {{ flex:1; min-height:0; display:flex; align-items:center; justify-content:center; }}
.results .plot img {{ max-width:100%; max-height:100%; object-fit:contain; border:.25mm solid var(--line); border-radius:1.4mm; }}
.results .plot .cap {{ font-size:8.2pt; color:var(--faint); margin-top:2mm; }}
.results .right-col {{ display:flex; flex-direction:column; min-height:0; }}

/* ---------- footer band ---------- */
.foot {{ background:var(--ink); color:#fff; border-radius:2.6mm; padding:4.5mm 6mm; display:flex; gap:7mm; align-items:center; }}
.foot .fc {{ flex:1; }}
.foot .eyebrow {{ color:#fff; }}
.foot .eyebrow::before {{ background:#fff; }}
.foot p {{ font-size:9pt; opacity:.9; margin:0; line-height:1.4; }}
.foot .stack {{ flex:none; max-width:78mm; text-align:right; font-size:8.4pt; opacity:.82; line-height:1.5; border-left:.3mm solid rgba(255,255,255,.25); padding-left:6mm; }}
.foot .stack b {{ display:block; font-size:8pt; letter-spacing:.12em; text-transform:uppercase; opacity:.6; margin-bottom:1.5mm; }}
</style></head><body>

  <div class="head">
    <div class="head-top">
      <div class="head-logo"><img src="{uet_logo}" alt="UET Lahore"></div>
      <div class="head-mid">
        <div class="kicker">ATC&middot;VISION</div>
        <h1>Aircraft Detection, Classification &amp; Segmentation<br>for Air Traffic Control</h1>
        <div class="sub">An end-to-end computer-vision pipeline combining pretrained YOLOv8 detection &amp; segmentation
          with a custom-trained ResNet-50 classifier to localise, segment and identify aircraft types from runway imagery.</div>
      </div>
      <div class="right">
        <b>University of Engineering<br>&amp; Technology, Lahore</b><br>Dept. of Computer Science<br>R&amp;D Poster &middot; 2026
      </div>
    </div>
    <div class="head-div"></div>
    <div class="head-credits">
      <div class="cred">
        <div class="lbl">Group Members</div>
        <div class="who"><b>Sumaira Hafeez</b> <span class="id">2023-CS-01</span> &nbsp;&middot;&nbsp; <b>Mustafa Noor</b> <span class="id">2023-CS-17</span></div>
      </div>
      <div class="cred right-c">
        <div class="lbl">Instructors</div>
        <div class="who"><b>Prof. Dr. Usman Ghani</b> &nbsp;&middot;&nbsp; <b>Mr. Muhammad Waseem</b></div>
      </div>
    </div>
  </div>

  <div class="body">

    <!-- abstract + objectives -->
    <div class="row r-ab">
      <div class="card">
        <div class="eyebrow">Abstract</div>
        <p>Modern air-traffic monitoring needs reliable, automated interpretation of visual feeds. <b>ATC&middot;Vision</b>
        performs three vision tasks on one image: <b>detection</b> (locating every aircraft), <b>segmentation</b>
        (pixel-level instance masks) and <b>classification</b> (identifying the exact aircraft type). Detection and
        segmentation reuse a pretrained YOLOv8m-seg backbone, while a ResNet-50 fine-tuned on eight aircraft classes
        reaches <b>{ACC:.2f}%</b> test accuracy. A hybrid stage routes every detected box through the classifier, so
        generic &ldquo;airplane&rdquo; detections become named types with confidence and runway position.</p>
      </div>
      <div class="card">
        <div class="eyebrow">Objectives</div>
        <ul>
          <li>Detect and localise all aircraft in a runway / apron scene.</li>
          <li>Produce instance segmentation masks for situational awareness.</li>
          <li>Classify each aircraft into one of 8 types with confidence.</li>
          <li>Group types into Commercial / Military / Training categories.</li>
          <li>Deliver results through an interactive analysis dashboard.</li>
        </ul>
      </div>
    </div>

    <!-- workflow -->
    <div class="card">
      <div class="eyebrow">System Workflow</div>
      <div class="flow">
        <div class="node"><div class="step">1</div><div class="ic">&#128247;</div><div class="t">Input Image</div><div class="d">Runway / apron photo or single aircraft crop</div></div>
        <div class="arrow">&rarr;</div>
        <div class="node"><div class="step">2</div><div class="ic">&#9881;</div><div class="t">Preprocess</div><div class="d">Resize &amp; normalise (max 1600 px)</div></div>
        <div class="arrow">&rarr;</div>
        <div class="node dark"><div class="step">3</div><div class="ic">&#9707;</div><div class="t">YOLOv8m-seg</div><div class="d">Boxes + instance masks (pretrained, COCO)</div></div>
        <div class="arrow">&rarr;</div>
        <div class="node"><div class="step">4</div><div class="ic">&#9986;</div><div class="t">Crop ROIs</div><div class="d">Extract each detected aircraft region</div></div>
        <div class="arrow">&rarr;</div>
        <div class="node dark"><div class="step">5</div><div class="ic">&#129518;</div><div class="t">ResNet-50</div><div class="d">Trained classifier &rarr; type + confidence</div></div>
        <div class="arrow">&rarr;</div>
        <div class="node"><div class="step">6</div><div class="ic">&#128202;</div><div class="t">Results</div><div class="d">Named boxes, masks &amp; analytics</div></div>
      </div>
      <div class="flow-note">Hybrid design &mdash; YOLOv8 answers <i>where</i> &amp; <i>how many</i>; the fine-tuned ResNet-50 answers <i>which type</i>. A single-aircraft image can skip detection and go straight to the classifier.</div>
    </div>

    <!-- methodology -->
    <div class="row r-3">
      <div class="card"><div class="eyebrow">Detection</div><h3 class="title">YOLOv8m-seg</h3>
        <p>Single-stage detector predicting boxes for the COCO <span class="mono">airplane</span> class at a 0.35
        confidence threshold; boxes are clipped to image bounds and passed downstream for type identification.</p></div>
      <div class="card"><div class="eyebrow">Segmentation</div><h3 class="title">Instance Masks</h3>
        <p>The same network outputs per-instance masks, visualised step-by-step: input &rarr; preprocessing &rarr;
        binary masks &rarr; overlay &rarr; contours, with per-region coverage statistics.</p></div>
      <div class="card"><div class="eyebrow">Classification</div><h3 class="title">ResNet-50 (Fine-tuned)</h3>
        <p>ImageNet-pretrained ResNet-50 with a new 8-way head, 224&times;224 input and ImageNet normalisation; returns
        the top class, confidence and full probability distribution.</p></div>
    </div>

    <!-- model & dataset (compact, full width) -->
    <div class="card">
      <div class="eyebrow">Model &amp; Dataset</div>
      <div class="model-grid">
        <div class="kv"><span>Backbone</span><b>ResNet-50</b></div>
        <div class="kv"><span>Classifier head</span><b>Linear 2048&rarr;8</b></div>
        <div class="kv"><span>Input size</span><b>224 &times; 224</b></div>
        <div class="kv"><span>Detector / Segmenter</span><b>YOLOv8m-seg</b></div>
        <div class="kv"><span>Test images</span><b>{total_support}</b></div>
        <div class="kv"><span>Inference / image</span><b>{INF:.0f} ms</b></div>
      </div>
      <div class="tags">
        <span class="tag">ATR</span><span class="tag">Airbus</span><span class="tag">Boeing</span><span class="tag">C130</span>
        <span class="tag">F16</span><span class="tag">Grob</span><span class="tag">KAI</span><span class="tag">Sukhoi</span>
        <span class="tagnote">8 classes &middot; Commercial / Military / Training</span>
      </div>
    </div>

    <!-- metric tiles -->
    <div class="tiles">
      <div class="tile"><div class="v">{ACC:.1f}%</div><div class="l">Accuracy</div></div>
      <div class="tile"><div class="v">{PREC:.1f}%</div><div class="l">Precision (weighted)</div></div>
      <div class="tile"><div class="v">{REC:.1f}%</div><div class="l">Recall (weighted)</div></div>
      <div class="tile"><div class="v">{F1:.1f}%</div><div class="l">F1-Score (weighted)</div></div>
    </div>

    <!-- results: confusion matrix + per-class accuracy -->
    <div class="row results">
      <div class="card plot">
        <div class="eyebrow">Confusion Matrix</div>
        <div class="imgbox"><img src="{cm_img}" alt="confusion matrix"></div>
        <div class="cap">Strongly diagonal &mdash; errors are rare and confined to visually similar commercial jets.</div>
      </div>
      <div class="card right-col">
        <div class="eyebrow">Per-Class Accuracy</div>
        <div class="barwrap">{bars}</div>
      </div>
    </div>

    <!-- footer band -->
    <div class="foot">
      <div class="fc">
        <div class="eyebrow">Conclusion &amp; Future Work</div>
        <p>The hybrid YOLOv8 + ResNet-50 design delivers accurate, explainable aircraft identification ({ACC:.2f}% test
        accuracy) while reusing strong pretrained detectors, keeping the trainable footprint small. Future work: fine-tune
        the detector on aircraft-specific data, extend to real-time video, and add range / altitude estimation.</p>
      </div>
      <div class="stack">
        <b>Technology Stack</b>
        PyTorch &middot; torchvision &middot; Ultralytics YOLOv8<br>OpenCV &middot; Flask &middot; React + Vite
      </div>
    </div>

  </div>
</body></html>'''

with open(os.path.join(ROOT, 'poster.html'), 'w', encoding='utf-8') as f:
    f.write(HTML)
print('Wrote poster.html ({} KB)'.format(len(HTML) // 1024))
