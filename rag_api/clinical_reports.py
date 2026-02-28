"""
Clinical Reports Generator for VetrIAge
=======================================

Professional veterinary clinical report generation with multiple formats:
- SOAP (Subjective, Objective, Assessment, Plan)
- POMR (Problem-Oriented Medical Record)
- PDF export with branded templates
- Email delivery integration

Author: VetrIAge Team
Version: 2.1
License: MIT
"""

import os
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
from io import BytesIO
import logging

# PDF generation
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        PageBreak, Image, KeepTogether
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False
    logging.warning("reportlab not installed. PDF generation will be unavailable.")

logger = logging.getLogger(__name__)


@dataclass
class VeterinaryCase:
    """Complete veterinary case information"""
    # Patient information
    patient_name: str
    species: str
    breed: Optional[str] = None
    age: Optional[int] = None
    sex: Optional[str] = None
    weight: Optional[float] = None
    
    # Case details
    case_id: str = field(default_factory=lambda: f"VET-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
    date: datetime = field(default_factory=datetime.now)
    
    # Veterinarian
    veterinarian_name: str = "Dr. [Veterinarian Name]"
    clinic_name: str = "Veterinary Clinic"
    clinic_address: Optional[str] = None
    clinic_phone: Optional[str] = None
    
    # Owner information
    owner_name: Optional[str] = None
    owner_contact: Optional[str] = None


@dataclass
class SOAPReport:
    """SOAP format veterinary clinical report"""
    
    # Case information
    case: VeterinaryCase
    
    # Subjective (S)
    chief_complaint: str
    history: str
    owner_observations: Optional[str] = None
    
    # Objective (O)
    physical_exam: Dict[str, str] = field(default_factory=dict)
    vitals: Dict[str, float] = field(default_factory=dict)
    lab_results: Dict[str, float] = field(default_factory=dict)
    diagnostic_imaging: Optional[str] = None
    
    # Assessment (A)
    differential_diagnoses: List[Dict] = field(default_factory=list)
    primary_diagnosis: Optional[str] = None
    secondary_diagnoses: List[str] = field(default_factory=list)
    grade_score: Optional[str] = None
    prognosis: str = "Guarded pending further diagnostics"
    
    # Plan (P)
    diagnostic_plan: List[str] = field(default_factory=list)
    treatment_plan: List[str] = field(default_factory=list)
    monitoring: List[str] = field(default_factory=list)
    follow_up: str = "Re-evaluate in 7-14 days or sooner if condition worsens"
    
    # Evidence
    cited_papers: List[Dict] = field(default_factory=list)
    
    # Alerts
    clinical_alerts: List[Dict] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'case': self.case.__dict__,
            'subjective': {
                'chief_complaint': self.chief_complaint,
                'history': self.history,
                'owner_observations': self.owner_observations
            },
            'objective': {
                'physical_exam': self.physical_exam,
                'vitals': self.vitals,
                'lab_results': self.lab_results,
                'diagnostic_imaging': self.diagnostic_imaging
            },
            'assessment': {
                'differential_diagnoses': self.differential_diagnoses,
                'primary_diagnosis': self.primary_diagnosis,
                'secondary_diagnoses': self.secondary_diagnoses,
                'grade_score': self.grade_score,
                'prognosis': self.prognosis
            },
            'plan': {
                'diagnostic_plan': self.diagnostic_plan,
                'treatment_plan': self.treatment_plan,
                'monitoring': self.monitoring,
                'follow_up': self.follow_up
            },
            'evidence': {'cited_papers': self.cited_papers},
            'alerts': {'clinical_alerts': self.clinical_alerts}
        }


class ClinicalReportGenerator:
    """Generate professional veterinary clinical reports"""
    
    def __init__(self, logo_path: Optional[str] = None):
        """
        Initialize report generator.
        
        Args:
            logo_path: Path to clinic logo image (optional)
        """
        self.logo_path = logo_path
        self.styles = self._create_styles()
    
    def _create_styles(self) -> Dict:
        """Create custom paragraph styles"""
        styles = getSampleStyleSheet()
        
        # Title style
        styles.add(ParagraphStyle(
            name='VetTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2C5F8D'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Section header style
        styles.add(ParagraphStyle(
            name='VetSection',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2C5F8D'),
            spaceAfter=6,
            spaceBefore=12,
            fontName='Helvetica-Bold',
            borderWidth=1,
            borderColor=colors.HexColor('#2C5F8D'),
            borderPadding=4,
            backColor=colors.HexColor('#E8F4F8')
        ))
        
        # Subsection style
        styles.add(ParagraphStyle(
            name='VetSubsection',
            parent=styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#1E3D59'),
            spaceAfter=4,
            spaceBefore=8,
            fontName='Helvetica-Bold'
        ))
        
        # Body text
        styles.add(ParagraphStyle(
            name='VetBody',
            parent=styles['BodyText'],
            fontSize=10,
            textColor=colors.black,
            spaceAfter=6,
            alignment=TA_JUSTIFY,
            fontName='Helvetica'
        ))
        
        # Alert style (red)
        styles.add(ParagraphStyle(
            name='VetAlert',
            parent=styles['BodyText'],
            fontSize=10,
            textColor=colors.red,
            spaceAfter=6,
            fontName='Helvetica-Bold',
            backColor=colors.HexColor('#FFE6E6'),
            borderWidth=1,
            borderColor=colors.red,
            borderPadding=6
        ))
        
        # Citation style
        styles.add(ParagraphStyle(
            name='VetCitation',
            parent=styles['BodyText'],
            fontSize=8,
            textColor=colors.HexColor('#555555'),
            spaceAfter=3,
            fontName='Helvetica',
            leftIndent=20
        ))
        
        return styles
    
    def generate_pdf(self, report: SOAPReport, output_path: Optional[str] = None) -> bytes:
        """
        Generate PDF report from SOAP data.
        
        Args:
            report: SOAPReport object
            output_path: Path to save PDF (optional). If None, returns bytes.
        
        Returns:
            PDF file as bytes
        """
        if not HAS_REPORTLAB:
            raise ImportError("reportlab is required for PDF generation. Install with: pip install reportlab")
        
        # Create PDF buffer
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer if output_path is None else output_path,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        # Build story (content)
        story = []
        
        # Header with logo (if available)
        if self.logo_path and os.path.exists(self.logo_path):
            try:
                logo = Image(self.logo_path, width=2*inch, height=0.5*inch)
                logo.hAlign = 'CENTER'
                story.append(logo)
                story.append(Spacer(1, 0.2*inch))
            except Exception as e:
                logger.warning(f"Could not load logo: {e}")
        
        # Title
        story.append(Paragraph("VetrIAge Clinical Report", self.styles['VetTitle']))
        story.append(Paragraph(f"Evidence-Based Veterinary Diagnostics", self.styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Case Information Box
        case_data = [
            ['Case ID:', report.case.case_id, 'Date:', report.case.date.strftime('%Y-%m-%d %H:%M')],
            ['Patient:', report.case.patient_name, 'Species:', report.case.species.capitalize()],
            ['Breed:', report.case.breed or 'Not specified', 'Age:', f"{report.case.age} years" if report.case.age else 'Unknown'],
            ['Sex:', report.case.sex or 'Unknown', 'Weight:', f"{report.case.weight} kg" if report.case.weight else 'Unknown'],
            ['Veterinarian:', report.case.veterinarian_name, 'Clinic:', report.case.clinic_name]
        ]
        
        case_table = Table(case_data, colWidths=[1.2*inch, 2.3*inch, 1.2*inch, 2.3*inch])
        case_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F5F5F5')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(case_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Clinical Alerts (if any)
        if report.clinical_alerts:
            story.append(Paragraph("⚠️ CLINICAL ALERTS", self.styles['VetSection']))
            for alert in report.clinical_alerts:
                alert_text = f"<b>{alert['severity'].upper()}</b>: {alert['message']}"
                story.append(Paragraph(alert_text, self.styles['VetAlert']))
            story.append(Spacer(1, 0.2*inch))
        
        # SUBJECTIVE
        story.append(Paragraph("SUBJECTIVE", self.styles['VetSection']))
        
        story.append(Paragraph("<b>Chief Complaint:</b>", self.styles['VetSubsection']))
        story.append(Paragraph(report.chief_complaint, self.styles['VetBody']))
        
        story.append(Paragraph("<b>History:</b>", self.styles['VetSubsection']))
        story.append(Paragraph(report.history, self.styles['VetBody']))
        
        if report.owner_observations:
            story.append(Paragraph("<b>Owner Observations:</b>", self.styles['VetSubsection']))
            story.append(Paragraph(report.owner_observations, self.styles['VetBody']))
        
        story.append(Spacer(1, 0.2*inch))
        
        # OBJECTIVE
        story.append(Paragraph("OBJECTIVE", self.styles['VetSection']))
        
        # Vitals
        if report.vitals:
            story.append(Paragraph("<b>Vital Signs:</b>", self.styles['VetSubsection']))
            vitals_text = ", ".join([f"{k}: {v}" for k, v in report.vitals.items()])
            story.append(Paragraph(vitals_text, self.styles['VetBody']))
        
        # Physical Exam
        if report.physical_exam:
            story.append(Paragraph("<b>Physical Examination:</b>", self.styles['VetSubsection']))
            for system, finding in report.physical_exam.items():
                story.append(Paragraph(f"• <b>{system}:</b> {finding}", self.styles['VetBody']))
        
        # Lab Results
        if report.lab_results:
            story.append(Paragraph("<b>Laboratory Results:</b>", self.styles['VetSubsection']))
            lab_data = [[param, f"{value}"] for param, value in report.lab_results.items()]
            lab_table = Table([['Parameter', 'Value']] + lab_data, colWidths=[3*inch, 2*inch])
            lab_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C5F8D')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(lab_table)
        
        # Diagnostic Imaging
        if report.diagnostic_imaging:
            story.append(Paragraph("<b>Diagnostic Imaging:</b>", self.styles['VetSubsection']))
            story.append(Paragraph(report.diagnostic_imaging, self.styles['VetBody']))
        
        story.append(Spacer(1, 0.2*inch))
        
        # ASSESSMENT
        story.append(Paragraph("ASSESSMENT", self.styles['VetSection']))
        
        # Primary Diagnosis
        if report.primary_diagnosis:
            story.append(Paragraph(f"<b>Primary Diagnosis:</b> {report.primary_diagnosis}", self.styles['VetSubsection']))
            if report.grade_score:
                story.append(Paragraph(f"<b>Evidence Grade:</b> {report.grade_score}", self.styles['VetBody']))
        
        # Differential Diagnoses
        if report.differential_diagnoses:
            story.append(Paragraph("<b>Differential Diagnoses:</b>", self.styles['VetSubsection']))
            for i, ddx in enumerate(report.differential_diagnoses[:5], 1):
                ddx_text = f"{i}. <b>{ddx['diagnosis']}</b> (Probability: {ddx.get('probability', 0)*100:.0f}%)"
                story.append(Paragraph(ddx_text, self.styles['VetBody']))
                if ddx.get('rationale'):
                    story.append(Paragraph(f"   Rationale: {ddx['rationale']}", self.styles['VetBody']))
        
        # Prognosis
        story.append(Paragraph(f"<b>Prognosis:</b> {report.prognosis}", self.styles['VetSubsection']))
        
        story.append(Spacer(1, 0.2*inch))
        
        # PLAN
        story.append(Paragraph("PLAN", self.styles['VetSection']))
        
        # Diagnostic Plan
        if report.diagnostic_plan:
            story.append(Paragraph("<b>Diagnostic Plan:</b>", self.styles['VetSubsection']))
            for item in report.diagnostic_plan:
                story.append(Paragraph(f"• {item}", self.styles['VetBody']))
        
        # Treatment Plan
        if report.treatment_plan:
            story.append(Paragraph("<b>Treatment Plan:</b>", self.styles['VetSubsection']))
            for item in report.treatment_plan:
                story.append(Paragraph(f"• {item}", self.styles['VetBody']))
        
        # Monitoring
        if report.monitoring:
            story.append(Paragraph("<b>Monitoring:</b>", self.styles['VetSubsection']))
            for item in report.monitoring:
                story.append(Paragraph(f"• {item}", self.styles['VetBody']))
        
        # Follow-up
        story.append(Paragraph(f"<b>Follow-up:</b> {report.follow_up}", self.styles['VetSubsection']))
        
        story.append(Spacer(1, 0.3*inch))
        
        # EVIDENCE / REFERENCES
        if report.cited_papers:
            story.append(Paragraph("SCIENTIFIC EVIDENCE", self.styles['VetSection']))
            story.append(Paragraph("This diagnosis is supported by the following peer-reviewed literature:", 
                                 self.styles['VetBody']))
            story.append(Spacer(1, 0.1*inch))
            
            for i, paper in enumerate(report.cited_papers, 1):
                citation = f"{i}. {paper.get('title', 'No title')} (PMID: {paper.get('pmid', 'N/A')})"
                story.append(Paragraph(citation, self.styles['VetCitation']))
                if paper.get('key_finding'):
                    story.append(Paragraph(f"   Key finding: {paper['key_finding']}", self.styles['VetCitation']))
        
        # Footer
        story.append(Spacer(1, 0.5*inch))
        footer_text = f"""
        <i>This report was generated by VetrIAge AI-Powered Veterinary Diagnostics System on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}. 
        This is a clinical decision support tool and should be used in conjunction with professional veterinary judgment. 
        For questions or concerns, please consult with a licensed veterinarian.</i>
        """
        story.append(Paragraph(footer_text, self.styles['Normal']))
        
        # Build PDF
        doc.build(story)
        
        # Return bytes if no output path
        if output_path is None:
            pdf_bytes = buffer.getvalue()
            buffer.close()
            return pdf_bytes
        
        return b''
    
    def generate_html(self, report: SOAPReport) -> str:
        """
        Generate HTML report from SOAP data.
        
        Args:
            report: SOAPReport object
        
        Returns:
            HTML string
        """
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VetrIAge Clinical Report - {report.case.case_id}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            text-align: center;
            background: linear-gradient(135deg, #2C5F8D 0%, #1E3D59 100%);
            color: white;
            padding: 30px;
            border-radius: 10px 10px 0 0;
        }}
        .header h1 {{
            margin: 0;
            font-size: 32px;
        }}
        .header p {{
            margin: 10px 0 0 0;
            font-size: 14px;
            opacity: 0.9;
        }}
        .case-info {{
            background: white;
            padding: 20px;
            border: 1px solid #ddd;
        }}
        .case-info table {{
            width: 100%;
            border-collapse: collapse;
        }}
        .case-info td {{
            padding: 8px;
            border: 1px solid #ddd;
        }}
        .case-info td:nth-child(odd) {{
            background: #f9f9f9;
            font-weight: bold;
            width: 25%;
        }}
        .alert {{
            background: #ffe6e6;
            border-left: 4px solid #d32f2f;
            padding: 15px;
            margin: 20px 0;
        }}
        .alert strong {{
            color: #d32f2f;
        }}
        .section {{
            background: white;
            margin: 20px 0;
            padding: 20px;
            border-left: 4px solid #2C5F8D;
        }}
        .section h2 {{
            margin: 0 0 15px 0;
            color: #2C5F8D;
            font-size: 20px;
            border-bottom: 2px solid #E8F4F8;
            padding-bottom: 10px;
        }}
        .subsection {{
            margin: 15px 0 10px 0;
            font-weight: bold;
            color: #1E3D59;
        }}
        .ddx-item {{
            background: #f9f9f9;
            padding: 12px;
            margin: 8px 0;
            border-radius: 5px;
            border-left: 3px solid #2C5F8D;
        }}
        .lab-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
        }}
        .lab-table th {{
            background: #2C5F8D;
            color: white;
            padding: 10px;
            text-align: left;
        }}
        .lab-table td {{
            padding: 8px;
            border: 1px solid #ddd;
        }}
        .lab-table tr:nth-child(even) {{
            background: #f9f9f9;
        }}
        .citation {{
            background: #f5f5f5;
            padding: 10px;
            margin: 5px 0;
            font-size: 12px;
            border-left: 3px solid #999;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 12px;
            font-style: italic;
            background: white;
            border-radius: 0 0 10px 10px;
        }}
        ul {{
            margin: 10px 0;
            padding-left: 20px;
        }}
        li {{
            margin: 5px 0;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🐾 VetrIAge Clinical Report</h1>
        <p>Evidence-Based Veterinary Diagnostics</p>
    </div>
    
    <div class="case-info">
        <table>
            <tr>
                <td>Case ID</td>
                <td>{report.case.case_id}</td>
                <td>Date</td>
                <td>{report.case.date.strftime('%Y-%m-%d %H:%M')}</td>
            </tr>
            <tr>
                <td>Patient</td>
                <td>{report.case.patient_name}</td>
                <td>Species</td>
                <td>{report.case.species.capitalize()}</td>
            </tr>
            <tr>
                <td>Breed</td>
                <td>{report.case.breed or 'Not specified'}</td>
                <td>Age</td>
                <td>{f"{report.case.age} years" if report.case.age else 'Unknown'}</td>
            </tr>
            <tr>
                <td>Sex</td>
                <td>{report.case.sex or 'Unknown'}</td>
                <td>Weight</td>
                <td>{f"{report.case.weight} kg" if report.case.weight else 'Unknown'}</td>
            </tr>
            <tr>
                <td>Veterinarian</td>
                <td>{report.case.veterinarian_name}</td>
                <td>Clinic</td>
                <td>{report.case.clinic_name}</td>
            </tr>
        </table>
    </div>
    
    """
        
        # Clinical Alerts
        if report.clinical_alerts:
            html += '<div class="alert">'
            html += '<h3>⚠️ CLINICAL ALERTS</h3>'
            for alert in report.clinical_alerts:
                html += f'<p><strong>{alert["severity"].upper()}</strong>: {alert["message"]}</p>'
            html += '</div>'
        
        # SUBJECTIVE
        html += f'''
    <div class="section">
        <h2>SUBJECTIVE</h2>
        <div class="subsection">Chief Complaint:</div>
        <p>{report.chief_complaint}</p>
        
        <div class="subsection">History:</div>
        <p>{report.history}</p>
        '''
        
        if report.owner_observations:
            html += f'''
        <div class="subsection">Owner Observations:</div>
        <p>{report.owner_observations}</p>
            '''
        
        html += '</div>'
        
        # OBJECTIVE
        html += '<div class="section"><h2>OBJECTIVE</h2>'
        
        if report.vitals:
            html += '<div class="subsection">Vital Signs:</div><p>'
            html += ', '.join([f"{k}: {v}" for k, v in report.vitals.items()])
            html += '</p>'
        
        if report.physical_exam:
            html += '<div class="subsection">Physical Examination:</div><ul>'
            for system, finding in report.physical_exam.items():
                html += f'<li><strong>{system}:</strong> {finding}</li>'
            html += '</ul>'
        
        if report.lab_results:
            html += '<div class="subsection">Laboratory Results:</div>'
            html += '<table class="lab-table"><tr><th>Parameter</th><th>Value</th></tr>'
            for param, value in report.lab_results.items():
                html += f'<tr><td>{param}</td><td>{value}</td></tr>'
            html += '</table>'
        
        if report.diagnostic_imaging:
            html += f'<div class="subsection">Diagnostic Imaging:</div><p>{report.diagnostic_imaging}</p>'
        
        html += '</div>'
        
        # ASSESSMENT
        html += '<div class="section"><h2>ASSESSMENT</h2>'
        
        if report.primary_diagnosis:
            html += f'<div class="subsection">Primary Diagnosis: {report.primary_diagnosis}</div>'
            if report.grade_score:
                html += f'<p><strong>Evidence Grade:</strong> {report.grade_score}</p>'
        
        if report.differential_diagnoses:
            html += '<div class="subsection">Differential Diagnoses:</div>'
            for i, ddx in enumerate(report.differential_diagnoses[:5], 1):
                html += f'''
                <div class="ddx-item">
                    <strong>{i}. {ddx['diagnosis']}</strong> (Probability: {ddx.get('probability', 0)*100:.0f}%)
                    <br>Rationale: {ddx.get('rationale', 'N/A')}
                </div>
                '''
        
        html += f'<div class="subsection">Prognosis:</div><p>{report.prognosis}</p></div>'
        
        # PLAN
        html += '<div class="section"><h2>PLAN</h2>'
        
        if report.diagnostic_plan:
            html += '<div class="subsection">Diagnostic Plan:</div><ul>'
            for item in report.diagnostic_plan:
                html += f'<li>{item}</li>'
            html += '</ul>'
        
        if report.treatment_plan:
            html += '<div class="subsection">Treatment Plan:</div><ul>'
            for item in report.treatment_plan:
                html += f'<li>{item}</li>'
            html += '</ul>'
        
        if report.monitoring:
            html += '<div class="subsection">Monitoring:</div><ul>'
            for item in report.monitoring:
                html += f'<li>{item}</li>'
            html += '</ul>'
        
        html += f'<div class="subsection">Follow-up:</div><p>{report.follow_up}</p></div>'
        
        # EVIDENCE
        if report.cited_papers:
            html += '<div class="section"><h2>SCIENTIFIC EVIDENCE</h2>'
            html += '<p>This diagnosis is supported by the following peer-reviewed literature:</p>'
            for i, paper in enumerate(report.cited_papers, 1):
                html += f'''
                <div class="citation">
                    {i}. {paper.get('title', 'No title')} (PMID: {paper.get('pmid', 'N/A')})
                    {f"<br><em>Key finding: {paper['key_finding']}</em>" if paper.get('key_finding') else ''}
                </div>
                '''
            html += '</div>'
        
        # Footer
        html += f'''
    <div class="footer">
        This report was generated by VetrIAge AI-Powered Veterinary Diagnostics System on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.<br>
        This is a clinical decision support tool and should be used in conjunction with professional veterinary judgment.<br>
        For questions or concerns, please consult with a licensed veterinarian.
    </div>
</body>
</html>
        '''
        
        return html


def create_report_from_diagnosis(
    diagnosis_result: Dict,
    case_data: Dict,
    veterinarian_name: str = "Dr. [Veterinarian Name]",
    clinic_name: str = "Veterinary Clinic"
) -> SOAPReport:
    """
    Create SOAP report from RAG diagnosis result.
    
    Args:
        diagnosis_result: Output from VetriageRAG.rag_diagnose()
        case_data: Original case input data
        veterinarian_name: Name of veterinarian
        clinic_name: Name of clinic
    
    Returns:
        SOAPReport object ready for PDF/HTML generation
    """
    # Create case object
    case = VeterinaryCase(
        patient_name=case_data.get('patient_name', 'Unknown Patient'),
        species=case_data.get('species', 'unknown'),
        breed=case_data.get('breed'),
        age=case_data.get('age'),
        sex=case_data.get('sex'),
        weight=case_data.get('weight'),
        veterinarian_name=veterinarian_name,
        clinic_name=clinic_name
    )
    
    # Create SOAP report
    report = SOAPReport(
        case=case,
        chief_complaint=case_data.get('chief_complaint', 'Not specified'),
        history=case_data.get('history', 'Not available'),
        owner_observations=case_data.get('owner_observations'),
        physical_exam=case_data.get('physical_exam', {}),
        vitals=case_data.get('vitals', {}),
        lab_results=case_data.get('labs', {}),
        diagnostic_imaging=case_data.get('imaging'),
        differential_diagnoses=diagnosis_result.get('differential_diagnoses', []),
        primary_diagnosis=diagnosis_result.get('differential_diagnoses', [{}])[0].get('diagnosis') if diagnosis_result.get('differential_diagnoses') else None,
        grade_score=diagnosis_result.get('differential_diagnoses', [{}])[0].get('grade_score') if diagnosis_result.get('differential_diagnoses') else None,
        diagnostic_plan=diagnosis_result.get('diagnostic_plan', []),
        treatment_plan=diagnosis_result.get('immediate_actions', []),
        cited_papers=diagnosis_result.get('cited_papers', []),
        clinical_alerts=diagnosis_result.get('clinical_alerts', [])
    )
    
    return report
