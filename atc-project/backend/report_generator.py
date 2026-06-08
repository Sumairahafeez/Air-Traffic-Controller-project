import base64
import io
import datetime
from PIL import Image as PILImage
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle, PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def base64_to_rl_image(b64_str, max_width=450, max_height=280):
    if not b64_str:
        return None
    try:
        if ',' in b64_str:
            b64_str = b64_str.split(',', 1)[1]
        img_data = base64.b64decode(b64_str)
        pil_img = PILImage.open(io.BytesIO(img_data))
        
        width, height = pil_img.size
        aspect = width / height
        if width > max_width:
            width = max_width
            height = width / aspect
        if height > max_height:
            height = max_height
            width = height * aspect
            
        img_byte_arr = io.BytesIO()
        if pil_img.mode in ('RGBA', 'P'):
            pil_img = pil_img.convert('RGB')
        pil_img.save(img_byte_arr, format='JPEG', quality=85)
        img_byte_arr.seek(0)
        return RLImage(img_byte_arr, width=width, height=height)
    except Exception as e:
        print(f"Error decoding base64 image: {e}")
        return None

def make_pdf_report(data):
    """Generates a professional, comprehensive PDF report from the analysis data.
    
    Supports report types:
    - 'full': Combined pipeline report (Classification, Detection, Segmentation)
    - 'classification': Dedicated classification details
    - 'detection': Dedicated detection details
    - 'segmentation': Dedicated segmentation details
    """
    report_type = data.get('report_type', 'full')
    
    # Extract data parts at top so they are always in scope
    detections = data.get('detections', [])
    summary = data.get('summary', {})
    
    seg_data = data.get('segmentation', {})
    if not seg_data and 'stages' in data:
        seg_data = data
        
    seg_stats = seg_data.get('stats', {}) if isinstance(seg_data, dict) else {}
    if not seg_stats and 'instances' in data:
        seg_stats = data
        
    seg_stages = seg_data.get('stages', []) if isinstance(seg_data, dict) else []
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    
    # Colors
    PRIMARY = colors.HexColor('#0F172A')   # Slate 900
    SECONDARY = colors.HexColor('#475569') # Slate 600
    BORDER = colors.HexColor('#E2E8F0')    # Slate 200
    BG_LIGHT = colors.HexColor('#F8FAFC')  # Slate 50
    
    # Typography
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=PRIMARY,
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=SECONDARY,
        spaceAfter=15
    )
    
    section_h1 = ParagraphStyle(
        'SectionH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=PRIMARY,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    section_h2 = ParagraphStyle(
        'SectionH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=SECONDARY,
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=SECONDARY,
        spaceAfter=6
    )
    
    card_label_style = ParagraphStyle(
        'CardLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=SECONDARY,
        alignment=1
    )
    
    card_val_style = ParagraphStyle(
        'CardVal',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=PRIMARY,
        alignment=1
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.white
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=SECONDARY
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=table_cell_style,
        fontName='Helvetica-Bold',
        textColor=PRIMARY
    )
    
    story = []
    
    # 1. Header Banner
    title_text = "AIR TRAFFIC CONTROL ANALYSIS REPORT"
    if report_type == 'classification':
        title_text = "ATC·VISION CLASSIFICATION REPORT"
    elif report_type == 'detection':
        title_text = "ATC·VISION DETECTION REPORT"
    elif report_type == 'segmentation':
        title_text = "ATC·VISION SEGMENTATION REPORT"
        
    story.append(Paragraph(title_text, title_style))
    date_str = datetime.datetime.now().strftime("%B %d, %Y - %H:%M:%S")
    story.append(Paragraph(f"Generated on {date_str} | Air Traffic Control Vision System", subtitle_style))
    story.append(Spacer(1, 8))
    
    # Resolve images
    input_b64 = data.get('input_image')
    output_b64 = data.get('image')
    
    # =========================================================================
    # CLASSIFICATION REPORT MODE
    # =========================================================================
    if report_type == 'classification':
        prediction = data.get('prediction', {})
        class_name = prediction.get('class_name', 'Unknown')
        confidence = prediction.get('confidence', 0.0)
        category = prediction.get('category', 'Unknown')
        all_probs = prediction.get('all_probabilities', {})
        
        # Classification overview card
        class_overview = [
            [
                Paragraph("CLASSIFIED TYPE", card_label_style),
                Paragraph("CONFIDENCE", card_label_style),
                Paragraph("CATEGORY", card_label_style)
            ],
            [
                Paragraph(class_name, card_val_style),
                Paragraph(f"{confidence * 100:.2f}%", card_val_style),
                Paragraph(category, card_val_style)
            ]
        ]
        class_overview_table = Table(class_overview, colWidths=[173, 173, 173])
        class_overview_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), BG_LIGHT),
            ('BOX', (0, 0), (-1, -1), 1, BORDER),
            ('INNERGRID', (0, 0), (-1, -1), 1, BORDER),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ]))
        story.append(class_overview_table)
        story.append(Spacer(1, 15))
        
        # Image view
        input_img_flowable = base64_to_rl_image(input_b64, max_width=300, max_height=220)
        if input_img_flowable:
            vis_table_data = [[input_img_flowable], [Paragraph("<b>Classified Aircraft Crop</b>", body_style)]]
            vis_table = Table(vis_table_data, colWidths=[520])
            vis_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 4),
                ('BOTTOMPADDING', (0, 1), (-1, 1), 10),
            ]))
            story.append(vis_table)
            
        story.append(Paragraph("Class Probability Distribution", section_h1))
        
        if all_probs:
            prob_table_data = [[
                Paragraph("Class Name", table_header_style),
                Paragraph("Probability", table_header_style)
            ]]
            sorted_probs = sorted(all_probs.items(), key=lambda x: x[1], reverse=True)
            for name, p in sorted_probs:
                prob_table_data.append([
                    Paragraph(name, table_cell_bold if name == class_name else table_cell_style),
                    Paragraph(f"{p * 100:.2f}%", table_cell_bold if name == class_name else table_cell_style)
                ])
            prob_table = Table(prob_table_data, colWidths=[260, 260])
            prob_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BG_LIGHT]),
                ('BOX', (0, 0), (-1, -1), 1, BORDER),
                ('INNERGRID', (0, 0), (-1, -1), 1, BORDER),
            ]))
            story.append(KeepTogether([prob_table]))
            
    # =========================================================================
    # DETECTION REPORT MODE
    # =========================================================================
    elif report_type == 'detection':
        detections = data.get('detections', [])
        summary = data.get('summary', {})
        total_det = len(detections)
        avg_det_conf = sum(d['detection_confidence'] for d in detections) / total_det if total_det > 0 else 0.0
        
        box_areas = [d.get('area_px', 0) for d in detections]
        min_box_area = min(box_areas) if box_areas else 0
        max_box_area = max(box_areas) if box_areas else 0
        avg_box_area = sum(box_areas) / len(box_areas) if box_areas else 0
        
        det_overview = [
            [
                Paragraph("TOTAL DETECTED", card_label_style),
                Paragraph("AVG DET. CONFIDENCE", card_label_style)
            ],
            [
                Paragraph(str(total_det), card_val_style),
                Paragraph(f"{avg_det_conf * 100:.2f}%", card_val_style)
            ]
        ]
        det_overview_table = Table(det_overview, colWidths=[260, 260])
        det_overview_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), BG_LIGHT),
            ('BOX', (0, 0), (-1, -1), 1, BORDER),
            ('INNERGRID', (0, 0), (-1, -1), 1, BORDER),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ]))
        story.append(det_overview_table)
        story.append(Spacer(1, 15))
        
        # Detection Image view
        input_img_flowable = base64_to_rl_image(input_b64, max_width=240, max_height=180)
        output_img_flowable = base64_to_rl_image(output_b64, max_width=240, max_height=180)
        
        if input_img_flowable or output_img_flowable:
            vis_row = []
            vis_row_labels = []
            if input_img_flowable:
                vis_row.append(input_img_flowable)
                vis_row_labels.append(Paragraph("<b>Input Image</b>", body_style))
            if output_img_flowable:
                vis_row.append(output_img_flowable)
                vis_row_labels.append(Paragraph("<b>Annotated Output</b>", body_style))
                
            vis_table_data = [vis_row, vis_row_labels]
            vis_table = Table(vis_table_data, colWidths=[260, 260])
            vis_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 4),
                ('BOTTOMPADDING', (0, 1), (-1, 1), 10),
            ]))
            story.append(vis_table)
            
        story.append(Paragraph("Detection Statistics & List", section_h1))
        
        det_stats_data = [
            [
                Paragraph("<b>Smallest Bounding Box Size:</b>", body_style),
                Paragraph(f"{min_box_area:,} px²", body_style),
                Paragraph("<b>Largest Bounding Box Size:</b>", body_style),
                Paragraph(f"{max_box_area:,} px²", body_style),
            ],
            [
                Paragraph("<b>Average Bounding Box Size:</b>", body_style),
                Paragraph(f"{avg_box_area:,.1f} px²", body_style),
                Paragraph("", body_style),
                Paragraph("", body_style),
            ]
        ]
        det_stats_table = Table(det_stats_data, colWidths=[150, 110, 160, 100])
        det_stats_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(det_stats_table)
        story.append(Spacer(1, 8))
        
        if detections:
            det_table_data = [[
                Paragraph("ID", table_header_style),
                Paragraph("Class Label", table_header_style),
                Paragraph("Det. Confidence", table_header_style),
                Paragraph("Position (Center X, Y)", table_header_style),
                Paragraph("Bounding Box (x, y, w, h)", table_header_style),
                Paragraph("Box Area", table_header_style)
            ]]
            for idx, det in enumerate(detections):
                bbox = det.get('box', [0, 0, 0, 0])
                center = det.get('center', [0, 0])
                det_table_data.append([
                    Paragraph(f"#{det['id'] + 1}", table_cell_bold),
                    Paragraph(det.get('label', 'Aircraft'), table_cell_bold),
                    Paragraph(f"{det.get('detection_confidence', 0)*100:.2f}%", table_cell_style),
                    Paragraph(f"{center[0]}, {center[1]}", table_cell_style),
                    Paragraph(f"{bbox[0]}, {bbox[1]}, {bbox[2]}, {bbox[3]}", table_cell_style),
                    Paragraph(f"{det.get('area_px', 0):,} px²", table_cell_style)
                ])
                
            det_table = Table(det_table_data, colWidths=[35, 110, 85, 100, 120, 70])
            det_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BG_LIGHT]),
                ('BOX', (0, 0), (-1, -1), 1, BORDER),
                ('INNERGRID', (0, 0), (-1, -1), 1, BORDER),
            ]))
            story.append(KeepTogether([det_table]))
            
    # =========================================================================
    # SEGMENTATION REPORT MODE
    # =========================================================================
    elif report_type == 'segmentation':
        seg_stages = data.get('stages', [])
        seg_stats = data.get('stats', {})
        total_segmented = seg_stats.get('instances', 0)
        total_coverage = seg_stats.get('total_coverage_pct', 0.0)
        per_instance = seg_stats.get('per_instance', [])
        
        avg_seg_area = sum(r.get('area_px', 0) for r in per_instance) / len(per_instance) if per_instance else 0
        avg_seg_coverage = sum(r.get('coverage_pct', 0.0) for r in per_instance) / len(per_instance) if per_instance else 0.0
        
        seg_overview = [
            [
                Paragraph("SEGMENTED INSTANCES", card_label_style),
                Paragraph("TOTAL MASK COVERAGE", card_label_style)
            ],
            [
                Paragraph(str(total_segmented), card_val_style),
                Paragraph(f"{total_coverage}% of image", card_val_style)
            ]
        ]
        seg_overview_table = Table(seg_overview, colWidths=[260, 260])
        seg_overview_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), BG_LIGHT),
            ('BOX', (0, 0), (-1, -1), 1, BORDER),
            ('INNERGRID', (0, 0), (-1, -1), 1, BORDER),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ]))
        story.append(seg_overview_table)
        story.append(Spacer(1, 15))
        
        # Pipeline Stages
        pipeline_stages = [s for s in seg_stages if not s.get('title', '').startswith('1.')]
        
        if pipeline_stages:
            story.append(Paragraph("Step-by-Step Mask Processing Pipeline", section_h1))
            story.append(Spacer(1, 4))
            
            stages_data = []
            for s in pipeline_stages:
                stage_title = s.get('title', '')
                if '.' in stage_title:
                    parts = stage_title.split('.', 1)
                    if parts[0].strip().isdigit():
                        stage_title = parts[1].strip()
                
                stage_desc = s.get('description', '')
                stage_b64 = s.get('image')
                stage_img = base64_to_rl_image(stage_b64, max_width=100, max_height=80)
                
                if stage_img:
                    stages_data.append([
                        stage_img,
                        [
                            Paragraph(f"<b>{stage_title}</b>", section_h2),
                            Spacer(1, 2),
                            Paragraph(stage_desc, body_style)
                        ]
                    ])
                    
            stages_table = Table(stages_data, colWidths=[120, 400])
            stages_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('LINEBELOW', (0, 0), (-1, -1), 0.5, BORDER),
            ]))
            story.append(KeepTogether([stages_table]))
            story.append(Spacer(1, 10))
            
        if per_instance:
            story.append(Paragraph("Segmented Regions Details", section_h1))
            story.append(Spacer(1, 4))
            
            region_table_data = [[
                Paragraph("Region ID", table_header_style),
                Paragraph("Detected Class / Label", table_header_style),
                Paragraph("Mask Area (Pixels)", table_header_style),
                Paragraph("Relative Image Coverage", table_header_style)
            ]]
            
            for r in per_instance:
                region_table_data.append([
                    Paragraph(f"Instance #{r.get('id', 0) + 1}", table_cell_bold),
                    Paragraph(r.get('label') or 'Aircraft / Object', table_cell_bold),
                    Paragraph(f"{r.get('area_px', 0):,}", table_cell_style),
                    Paragraph(f"{r.get('coverage_pct', 0)}%", table_cell_style)
                ])
                
            region_table = Table(region_table_data, colWidths=[100, 140, 140, 140])
            region_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BG_LIGHT]),
                ('BOX', (0, 0), (-1, -1), 1, BORDER),
                ('INNERGRID', (0, 0), (-1, -1), 1, BORDER),
            ]))
            story.append(KeepTogether([region_table]))

    # =========================================================================
    # FULL PIPELINE REPORT MODE (DASHBOARD)
    # =========================================================================
    else:
        # Combined full statistics
        total_det = len(detections)
        classified_dets = [d for d in detections if 'classification_confidence' in d]
        total_classified = len(classified_dets)
        avg_class_conf = sum(d['classification_confidence'] for d in classified_dets) / total_classified if total_classified > 0 else 0.0
        
        categories = {}
        for d in classified_dets:
            cat = d.get('category', 'Unknown')
            categories[cat] = categories.get(cat, 0) + 1
        category_summary = ", ".join(f"{k}: {v}" for k, v in categories.items()) if categories else "None"
        
        avg_det_conf = sum(d['detection_confidence'] for d in detections) / total_det if total_det > 0 else 0.0
        
        box_areas = [d.get('area_px', 0) for d in detections]
        min_box_area = min(box_areas) if box_areas else 0
        max_box_area = max(box_areas) if box_areas else 0
        avg_box_area = sum(box_areas) / len(box_areas) if box_areas else 0
        
        total_segmented = seg_stats.get('instances', 0)
        total_coverage = seg_stats.get('total_coverage_pct', 0.0)
        per_instance = seg_stats.get('per_instance', [])
        
        avg_seg_area = sum(r.get('area_px', 0) for r in per_instance) / len(per_instance) if per_instance else 0
        avg_seg_coverage = sum(r.get('coverage_pct', 0.0) for r in per_instance) / len(per_instance) if per_instance else 0.0

        overview_data = [
            [
                Paragraph("TOTAL DETECTED", card_label_style),
                Paragraph("TOTAL CLASSIFIED", card_label_style),
                Paragraph("SEGMENTED INSTANCES", card_label_style),
                Paragraph("TOTAL MASK COVERAGE", card_label_style)
            ],
            [
                Paragraph(str(total_det), card_val_style),
                Paragraph(str(total_classified), card_val_style),
                Paragraph(str(total_segmented), card_val_style),
                Paragraph(f"{total_coverage}%", card_val_style)
            ]
        ]
        overview_table = Table(overview_data, colWidths=[130, 130, 130, 130])
        overview_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), BG_LIGHT),
            ('BOX', (0, 0), (-1, -1), 1, BORDER),
            ('INNERGRID', (0, 0), (-1, -1), 1, BORDER),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ]))
        story.append(overview_table)
        story.append(Spacer(1, 15))
        
        # 1. Classification
        story.append(Paragraph("1. Aircraft Classification Details", section_h1))
        class_stats_data = [
            [
                Paragraph("<b>Total Classified:</b>", body_style),
                Paragraph(str(total_classified), body_style),
                Paragraph("<b>Avg Classification Confidence:</b>", body_style),
                Paragraph(f"{avg_class_conf * 100:.2f}%", body_style),
            ],
            [
                Paragraph("<b>Categories Detected:</b>", body_style),
                Paragraph(category_summary, body_style),
                Paragraph("", body_style),
                Paragraph("", body_style),
            ]
        ]
        class_stats_table = Table(class_stats_data, colWidths=[110, 150, 160, 100])
        class_stats_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(class_stats_table)
        story.append(Spacer(1, 8))
        
        if classified_dets:
            class_table_data = [[
                Paragraph("ID", table_header_style),
                Paragraph("Primary Label", table_header_style),
                Paragraph("Confidence", table_header_style),
                Paragraph("Category", table_header_style),
                Paragraph("Alternative Predictions (Class / Confidence)", table_header_style)
            ]]
            for idx, det in enumerate(classified_dets):
                alt_preds = det.get('top_k', [])
                alt_str = "—"
                if len(alt_preds) > 1:
                    alt_str = ", ".join(f"{x['class_name']} ({x['confidence']*100:.0f}%)" for x in alt_preds[1:3])
                
                class_table_data.append([
                    Paragraph(f"#{det['id'] + 1}", table_cell_bold),
                    Paragraph(det.get('label', 'Aircraft'), table_cell_bold),
                    Paragraph(f"{det.get('classification_confidence', 0)*100:.2f}%", table_cell_style),
                    Paragraph(det.get('category', 'Unknown'), table_cell_style),
                    Paragraph(alt_str, table_cell_style)
                ])
                
            class_table = Table(class_table_data, colWidths=[35, 110, 70, 75, 230])
            class_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BG_LIGHT]),
                ('BOX', (0, 0), (-1, -1), 1, BORDER),
                ('INNERGRID', (0, 0), (-1, -1), 1, BORDER),
            ]))
            story.append(KeepTogether([class_table]))
            
        story.append(Spacer(1, 15))
        
        # 2. Detection
        story.append(Paragraph("2. Object Detection Details", section_h1))
        det_stats_data = [
            [
                Paragraph("<b>Total Bounding Boxes:</b>", body_style),
                Paragraph(str(total_det), body_style),
                Paragraph("<b>Avg Detection Confidence:</b>", body_style),
                Paragraph(f"{avg_det_conf * 100:.2f}%", body_style),
            ],
            [
                Paragraph("<b>Min Box Area:</b>", body_style),
                Paragraph(f"{min_box_area:,} px²", body_style),
                Paragraph("<b>Max Box Area:</b>", body_style),
                Paragraph(f"{max_box_area:,} px²", body_style),
            ]
        ]
        det_stats_table = Table(det_stats_data, colWidths=[120, 140, 140, 120])
        det_stats_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(det_stats_table)
        story.append(Spacer(1, 8))
        
        if detections:
            det_table_data = [[
                Paragraph("ID", table_header_style),
                Paragraph("Class Label", table_header_style),
                Paragraph("Det. Confidence", table_header_style),
                Paragraph("Position (Center X, Y)", table_header_style),
                Paragraph("Bounding Box (x, y, w, h)", table_header_style),
                Paragraph("Box Area", table_header_style)
            ]]
            for idx, det in enumerate(detections):
                bbox = det.get('box', [0, 0, 0, 0])
                center = det.get('center', [0, 0])
                det_table_data.append([
                    Paragraph(f"#{det['id'] + 1}", table_cell_bold),
                    Paragraph(det.get('label', 'Aircraft'), table_cell_bold),
                    Paragraph(f"{det.get('detection_confidence', 0)*100:.2f}%", table_cell_style),
                    Paragraph(f"{center[0]}, {center[1]}", table_cell_style),
                    Paragraph(f"{bbox[0]}, {bbox[1]}, {bbox[2]}, {bbox[3]}", table_cell_style),
                    Paragraph(f"{det.get('area_px', 0):,} px²", table_cell_style)
                ])
                
            det_table = Table(det_table_data, colWidths=[35, 110, 85, 100, 120, 70])
            det_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BG_LIGHT]),
                ('BOX', (0, 0), (-1, -1), 1, BORDER),
                ('INNERGRID', (0, 0), (-1, -1), 1, BORDER),
            ]))
            story.append(KeepTogether([det_table]))
            
        story.append(PageBreak())
        
        # Pipeline Visuals
        story.append(Paragraph("Input & Annotated Detection Output", section_h1))
        input_img_flowable = base64_to_rl_image(input_b64, max_width=250, max_height=200)
        output_img_flowable = base64_to_rl_image(output_b64, max_width=250, max_height=200)
        
        if input_img_flowable or output_img_flowable:
            vis_row = []
            vis_row_labels = []
            if input_img_flowable:
                vis_row.append(input_img_flowable)
                vis_row_labels.append(Paragraph("<b>Input Runway Scene</b>", body_style))
            if output_img_flowable:
                vis_row.append(output_img_flowable)
                vis_row_labels.append(Paragraph("<b>Annotated Output</b>", body_style))
                
            vis_table_data = [vis_row, vis_row_labels]
            vis_table = Table(vis_table_data, colWidths=[260, 260])
            vis_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 4),
                ('BOTTOMPADDING', (0, 1), (-1, 1), 10),
            ]))
            story.append(vis_table)
            
        story.append(Spacer(1, 10))

        # 3. Segmentation
        story.append(Paragraph("3. Instance Segmentation Details", section_h1))
        seg_stats_data = [
            [
                Paragraph("<b>Total Segmented Regions:</b>", body_style),
                Paragraph(str(total_segmented), body_style),
                Paragraph("<b>Total Mask Coverage:</b>", body_style),
                Paragraph(f"{total_coverage}% of image", body_style),
            ],
            [
                Paragraph("<b>Avg Instance Area:</b>", body_style),
                Paragraph(f"{avg_seg_area:,.1f} px²", body_style),
                Paragraph("<b>Avg Instance Coverage:</b>", body_style),
                Paragraph(f"{avg_seg_coverage:.3f}%", body_style),
            ]
        ]
        seg_stats_table = Table(seg_stats_data, colWidths=[140, 120, 140, 120])
        seg_stats_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(seg_stats_table)
        story.append(Spacer(1, 8))
        
        # Pipeline Stages
        pipeline_stages = [s for s in seg_stages if not s.get('title', '').startswith('1.')]
        if pipeline_stages:
            story.append(Paragraph("<b>Step-by-Step Mask Processing Pipeline:</b>", body_style))
            story.append(Spacer(1, 4))
            
            stages_data = []
            for s in pipeline_stages:
                stage_title = s.get('title', '')
                if '.' in stage_title:
                    parts = stage_title.split('.', 1)
                    if parts[0].strip().isdigit():
                        stage_title = parts[1].strip()
                
                stage_desc = s.get('description', '')
                stage_b64 = s.get('image')
                stage_img = base64_to_rl_image(stage_b64, max_width=100, max_height=80)
                
                if stage_img:
                    stages_data.append([
                        stage_img,
                        [
                            Paragraph(f"<b>{stage_title}</b>", section_h2),
                            Spacer(1, 2),
                            Paragraph(stage_desc, body_style)
                        ]
                    ])
                    
            stages_table = Table(stages_data, colWidths=[120, 400])
            stages_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('LINEBELOW', (0, 0), (-1, -1), 0.5, BORDER),
            ]))
            story.append(KeepTogether([stages_table]))
            
        story.append(Spacer(1, 10))
        
        if per_instance:
            region_table_data = [[
                Paragraph("Region ID", table_header_style),
                Paragraph("Detected Class / Label", table_header_style),
                Paragraph("Mask Area (Pixels)", table_header_style),
                Paragraph("Relative Image Coverage", table_header_style)
            ]]
            
            for r in per_instance:
                region_table_data.append([
                    Paragraph(f"Instance #{r.get('id', 0) + 1}", table_cell_bold),
                    Paragraph(r.get('label') or 'Aircraft / Object', table_cell_bold),
                    Paragraph(f"{r.get('area_px', 0):,}", table_cell_style),
                    Paragraph(f"{r.get('coverage_pct', 0)}%", table_cell_style)
                ])
                
            region_table = Table(region_table_data, colWidths=[100, 140, 140, 140])
            region_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BG_LIGHT]),
                ('BOX', (0, 0), (-1, -1), 1, BORDER),
                ('INNERGRID', (0, 0), (-1, -1), 1, BORDER),
            ]))
            story.append(KeepTogether([region_table]))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
