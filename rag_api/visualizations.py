"""
VetrIAge Interactive Visualizations
====================================

Provides interactive charts and graphs for veterinary diagnostics:
- Confidence scores by diagnosis
- Differential diagnosis comparison
- Timeline of symptoms
- Treatment response tracking
- Literature evidence strength
- Lab value trends

Author: VetrIAge Team
Version: 2.0.0
License: MIT
"""

import logging
from typing import List, Dict, Optional, Tuple
import json
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Import optional visualization libraries
try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.patches import Rectangle
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    logger.warning("matplotlib not installed. Static visualizations unavailable.")


def generate_confidence_chart(
    diagnoses: List[Dict],
    output_path: Optional[str] = None
) -> Optional[str]:
    """
    Generate bar chart of confidence scores by diagnosis
    
    Args:
        diagnoses: List of diagnosis dicts with 'diagnosis' and 'confidence' keys
        output_path: Path to save image (optional)
    
    Returns:
        Path to saved image or None
    """
    if not HAS_MATPLOTLIB:
        logger.error("matplotlib not available")
        return None
    
    if not diagnoses:
        logger.warning("No diagnoses provided for confidence chart")
        return None
    
    # Sort by confidence descending
    sorted_diagnoses = sorted(diagnoses, key=lambda x: x.get('confidence', 0), reverse=True)
    
    # Take top 10
    top_diagnoses = sorted_diagnoses[:10]
    
    labels = [d.get('diagnosis', 'Unknown')[:40] for d in top_diagnoses]
    confidences = [d.get('confidence', 0) for d in top_diagnoses]
    
    # Color coding based on confidence
    colors = []
    for conf in confidences:
        if conf >= 0.8:
            colors.append('#2ecc71')  # Green - high confidence
        elif conf >= 0.6:
            colors.append('#f39c12')  # Orange - moderate
        else:
            colors.append('#e74c3c')  # Red - low
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Horizontal bar chart
    y_pos = range(len(labels))
    bars = ax.barh(y_pos, confidences, color=colors)
    
    # Customize
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels)
    ax.set_xlabel('Confidence Score', fontsize=12)
    ax.set_title('Differential Diagnosis Confidence Scores', fontsize=14, fontweight='bold')
    ax.set_xlim(0, 1.0)
    
    # Add value labels on bars
    for i, (bar, conf) in enumerate(zip(bars, confidences)):
        ax.text(conf + 0.02, bar.get_y() + bar.get_height()/2, 
                f'{conf:.1%}', va='center', fontsize=10)
    
    # Grid
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    
    # Legend
    legend_elements = [
        Rectangle((0, 0), 1, 1, fc='#2ecc71', label='High (≥80%)'),
        Rectangle((0, 0), 1, 1, fc='#f39c12', label='Moderate (60-80%)'),
        Rectangle((0, 0), 1, 1, fc='#e74c3c', label='Low (<60%)')
    ]
    ax.legend(handles=legend_elements, loc='lower right')
    
    plt.tight_layout()
    
    # Save or return
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        logger.info(f"Confidence chart saved to {output_path}")
        plt.close()
        return output_path
    else:
        # Return base64 encoded image
        from io import BytesIO
        import base64
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode()
        plt.close()
        return f"data:image/png;base64,{img_str}"


def generate_ddx_comparison_chart(
    diagnoses: List[Dict],
    output_path: Optional[str] = None
) -> Optional[str]:
    """
    Generate radar/spider chart comparing top differential diagnoses
    
    Args:
        diagnoses: List of diagnosis dicts
        output_path: Path to save image
    
    Returns:
        Path to saved image or None
    """
    if not HAS_MATPLOTLIB:
        return None
    
    if not diagnoses or len(diagnoses) < 2:
        logger.warning("Need at least 2 diagnoses for comparison chart")
        return None
    
    # Take top 5
    top_diagnoses = sorted(diagnoses, key=lambda x: x.get('confidence', 0), reverse=True)[:5]
    
    # Metrics to compare
    metrics = ['Confidence', 'Evidence Quality', 'Specificity', 'Treatability']
    num_metrics = len(metrics)
    
    # Angles for radar chart
    angles = [n / float(num_metrics) * 2 * 3.14159 for n in range(num_metrics)]
    angles += angles[:1]
    
    # Create figure
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
    
    # Plot each diagnosis
    colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6']
    for idx, (diag, color) in enumerate(zip(top_diagnoses, colors)):
        values = [
            diag.get('confidence', 0),
            diag.get('evidence_quality', 0.5),  # Default if not available
            diag.get('specificity', 0.5),
            diag.get('treatability', 0.5)
        ]
        values += values[:1]
        
        ax.plot(angles, values, 'o-', linewidth=2, color=color, 
                label=diag.get('diagnosis', f'Diagnosis {idx+1}')[:30])
        ax.fill(angles, values, alpha=0.1, color=color)
    
    # Customize
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(metrics)
    ax.set_ylim(0, 1)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(['20%', '40%', '60%', '80%', '100%'])
    ax.grid(True)
    
    plt.title('Differential Diagnosis Comparison', size=14, fontweight='bold', pad=20)
    plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        logger.info(f"DDx comparison chart saved to {output_path}")
        plt.close()
        return output_path
    else:
        from io import BytesIO
        import base64
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode()
        plt.close()
        return f"data:image/png;base64,{img_str}"


def generate_symptom_timeline(
    symptom_data: List[Dict],
    output_path: Optional[str] = None
) -> Optional[str]:
    """
    Generate timeline of symptom onset and progression
    
    Args:
        symptom_data: List of dicts with 'symptom', 'onset_date', 'severity' keys
        output_path: Path to save image
    
    Returns:
        Path to saved image or None
    
    Example symptom_data:
        [
            {'symptom': 'Polyuria', 'onset_date': '2024-01-01', 'severity': 'moderate'},
            {'symptom': 'Polydipsia', 'onset_date': '2024-01-03', 'severity': 'severe'},
            ...
        ]
    """
    if not HAS_MATPLOTLIB:
        return None
    
    if not symptom_data:
        logger.warning("No symptom data provided")
        return None
    
    # Parse dates
    parsed_data = []
    for item in symptom_data:
        try:
            if isinstance(item['onset_date'], str):
                date = datetime.strptime(item['onset_date'], '%Y-%m-%d')
            else:
                date = item['onset_date']
            
            parsed_data.append({
                'symptom': item['symptom'],
                'date': date,
                'severity': item.get('severity', 'moderate')
            })
        except Exception as e:
            logger.error(f"Error parsing symptom date: {e}")
            continue
    
    if not parsed_data:
        return None
    
    # Sort by date
    parsed_data.sort(key=lambda x: x['date'])
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Severity colors
    severity_colors = {
        'mild': '#3498db',
        'moderate': '#f39c12',
        'severe': '#e74c3c',
        'critical': '#8e44ad'
    }
    
    # Plot timeline
    for idx, item in enumerate(parsed_data):
        date = item['date']
        severity = item['severity'].lower()
        color = severity_colors.get(severity, '#95a5a6')
        
        # Plot point
        ax.scatter(date, idx, s=200, c=color, zorder=3, edgecolors='black', linewidth=1.5)
        
        # Add label
        ax.text(date, idx + 0.2, item['symptom'], fontsize=10, ha='center')
    
    # Customize
    ax.set_ylim(-1, len(parsed_data))
    ax.set_xlabel('Date', fontsize=12)
    ax.set_title('Symptom Timeline', fontsize=14, fontweight='bold')
    
    # Format x-axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.xticks(rotation=45, ha='right')
    
    # Remove y-axis ticks
    ax.set_yticks([])
    
    # Grid
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    
    # Legend
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', label='Mild',
                   markerfacecolor='#3498db', markersize=10, markeredgecolor='black'),
        plt.Line2D([0], [0], marker='o', color='w', label='Moderate',
                   markerfacecolor='#f39c12', markersize=10, markeredgecolor='black'),
        plt.Line2D([0], [0], marker='o', color='w', label='Severe',
                   markerfacecolor='#e74c3c', markersize=10, markeredgecolor='black'),
        plt.Line2D([0], [0], marker='o', color='w', label='Critical',
                   markerfacecolor='#8e44ad', markersize=10, markeredgecolor='black')
    ]
    ax.legend(handles=legend_elements, loc='upper right')
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        logger.info(f"Symptom timeline saved to {output_path}")
        plt.close()
        return output_path
    else:
        from io import BytesIO
        import base64
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode()
        plt.close()
        return f"data:image/png;base64,{img_str}"


def generate_lab_trends_chart(
    lab_data: Dict[str, List[Tuple[str, float]]],
    reference_ranges: Optional[Dict[str, Tuple[float, float]]] = None,
    output_path: Optional[str] = None
) -> Optional[str]:
    """
    Generate chart showing lab value trends over time
    
    Args:
        lab_data: Dict of parameter name -> list of (date, value) tuples
        reference_ranges: Dict of parameter name -> (min, max) normal range
        output_path: Path to save image
    
    Returns:
        Path to saved image or None
    
    Example:
        lab_data = {
            'Glucose': [('2024-01-01', 524), ('2024-01-05', 380), ('2024-01-10', 250)],
            'BUN': [('2024-01-01', 65), ('2024-01-05', 55), ('2024-01-10', 40)]
        }
        reference_ranges = {
            'Glucose': (70, 150),
            'BUN': (10, 30)
        }
    """
    if not HAS_MATPLOTLIB:
        return None
    
    if not lab_data:
        logger.warning("No lab data provided")
        return None
    
    # Create subplots for each parameter
    num_params = len(lab_data)
    fig, axes = plt.subplots(num_params, 1, figsize=(12, 4 * num_params))
    
    if num_params == 1:
        axes = [axes]
    
    for idx, (param, values) in enumerate(lab_data.items()):
        ax = axes[idx]
        
        # Parse dates and values
        dates = []
        vals = []
        for date_str, val in values:
            try:
                if isinstance(date_str, str):
                    date = datetime.strptime(date_str, '%Y-%m-%d')
                else:
                    date = date_str
                dates.append(date)
                vals.append(val)
            except Exception as e:
                logger.error(f"Error parsing date: {e}")
                continue
        
        if not dates:
            continue
        
        # Plot values
        ax.plot(dates, vals, 'o-', linewidth=2, markersize=8, color='#3498db', label=param)
        
        # Add reference range if provided
        if reference_ranges and param in reference_ranges:
            min_val, max_val = reference_ranges[param]
            ax.axhspan(min_val, max_val, alpha=0.2, color='green', label='Normal Range')
            ax.axhline(min_val, color='green', linestyle='--', alpha=0.5)
            ax.axhline(max_val, color='green', linestyle='--', alpha=0.5)
        
        # Customize
        ax.set_ylabel(param, fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper right')
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # Overall title
    fig.suptitle('Laboratory Value Trends', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        logger.info(f"Lab trends chart saved to {output_path}")
        plt.close()
        return output_path
    else:
        from io import BytesIO
        import base64
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode()
        plt.close()
        return f"data:image/png;base64,{img_str}"


def generate_evidence_strength_chart(
    cited_papers: List[Dict],
    output_path: Optional[str] = None
) -> Optional[str]:
    """
    Generate chart showing evidence strength by paper type
    
    Args:
        cited_papers: List of cited paper dicts
        output_path: Path to save image
    
    Returns:
        Path to saved image or None
    """
    if not HAS_MATPLOTLIB:
        return None
    
    if not cited_papers:
        logger.warning("No cited papers provided")
        return None
    
    # Categorize papers by type (from GRADE or keywords)
    categories = {
        'Systematic Review / Meta-Analysis': 0,
        'Randomized Controlled Trial': 0,
        'Cohort Study': 0,
        'Case-Control Study': 0,
        'Case Series / Report': 0,
        'Expert Opinion': 0
    }
    
    for paper in cited_papers:
        title = paper.get('title', '').lower()
        abstract = paper.get('abstract', '').lower()
        text = title + " " + abstract
        
        if 'systematic review' in text or 'meta-analysis' in text:
            categories['Systematic Review / Meta-Analysis'] += 1
        elif 'randomized' in text or 'rct' in text:
            categories['Randomized Controlled Trial'] += 1
        elif 'cohort' in text:
            categories['Cohort Study'] += 1
        elif 'case-control' in text:
            categories['Case-Control Study'] += 1
        elif 'case series' in text or 'case report' in text:
            categories['Case Series / Report'] += 1
        else:
            categories['Expert Opinion'] += 1
    
    # Filter out empty categories
    categories = {k: v for k, v in categories.items() if v > 0}
    
    if not categories:
        return None
    
    # Create pie chart
    fig, ax = plt.subplots(figsize=(10, 7))
    
    labels = list(categories.keys())
    sizes = list(categories.values())
    
    # GRADE-based color coding (highest to lowest quality)
    colors = ['#2ecc71', '#3498db', '#f39c12', '#e67e22', '#e74c3c', '#95a5a6']
    colors = colors[:len(labels)]
    
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, autopct='%1.1f%%',
        colors=colors, startangle=90,
        textprops={'fontsize': 10}
    )
    
    # Bold percentage text
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    
    ax.set_title('Evidence Strength Distribution (GRADE Hierarchy)', 
                 fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        logger.info(f"Evidence strength chart saved to {output_path}")
        plt.close()
        return output_path
    else:
        from io import BytesIO
        import base64
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode()
        plt.close()
        return f"data:image/png;base64,{img_str}"


def generate_all_visualizations(
    diagnosis_result: Dict,
    output_dir: str
) -> Dict[str, str]:
    """
    Generate all visualizations for a diagnosis result
    
    Args:
        diagnosis_result: Complete diagnosis result from RAG system
        output_dir: Directory to save visualizations
    
    Returns:
        Dict mapping visualization type to file path
    """
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    visualizations = {}
    
    # 1. Confidence chart
    if 'differential_diagnoses' in diagnosis_result:
        conf_path = os.path.join(output_dir, 'confidence_chart.png')
        result = generate_confidence_chart(
            diagnosis_result['differential_diagnoses'],
            conf_path
        )
        if result:
            visualizations['confidence'] = result
    
    # 2. DDx comparison
    if 'differential_diagnoses' in diagnosis_result:
        comp_path = os.path.join(output_dir, 'ddx_comparison.png')
        result = generate_ddx_comparison_chart(
            diagnosis_result['differential_diagnoses'],
            comp_path
        )
        if result:
            visualizations['comparison'] = result
    
    # 3. Evidence strength
    if 'cited_papers' in diagnosis_result:
        evid_path = os.path.join(output_dir, 'evidence_strength.png')
        result = generate_evidence_strength_chart(
            diagnosis_result['cited_papers'],
            evid_path
        )
        if result:
            visualizations['evidence'] = result
    
    logger.info(f"Generated {len(visualizations)} visualizations in {output_dir}")
    
    return visualizations


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Example diagnosis result
    diagnoses = [
        {'diagnosis': 'Diabetes mellitus', 'confidence': 0.92},
        {'diagnosis': 'Chronic kidney disease', 'confidence': 0.75},
        {'diagnosis': 'Hyperthyroidism', 'confidence': 0.68},
        {'diagnosis': 'Hyperadrenocorticism', 'confidence': 0.55},
        {'diagnosis': 'Pancreatitis', 'confidence': 0.42}
    ]
    
    cited_papers = [
        {'title': 'Systematic review of feline diabetes management', 'abstract': '...'},
        {'title': 'Randomized trial of insulin therapy in cats', 'abstract': '...'},
        {'title': 'Case series: diabetes in senior cats', 'abstract': '...'}
    ]
    
    # Generate charts
    print("Generating confidence chart...")
    generate_confidence_chart(diagnoses, 'confidence_chart.png')
    
    print("Generating DDx comparison...")
    generate_ddx_comparison_chart(diagnoses, 'ddx_comparison.png')
    
    print("Generating evidence strength chart...")
    generate_evidence_strength_chart(cited_papers, 'evidence_strength.png')
    
    print("\nVisualizations generated successfully!")
