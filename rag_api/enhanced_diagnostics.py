"""
Enhanced Veterinary Diagnostics System
======================================

Integrated system combining:
- RAG with PubMed + bioRxiv
- Clinical decision support
- Professional report generation
- Citation management

Author: VetrIAge Team
Version: 2.1
License: MIT
"""

from typing import Dict, List, Optional
import logging

# Import core RAG
from .vetriage_rag import VetriageRAG, Paper, initialize_rag_system

# Import enhancements
from .clinical_decision_support import ClinicalDecisionSupport
from .clinical_reports import (
    ClinicalReportGenerator, SOAPReport, VeterinaryCase,
    create_report_from_diagnosis
)
from .citation_management import (
    BibliographyGenerator, create_citations_from_papers
)
from .biorxiv_search import BioRxivSearch

logger = logging.getLogger(__name__)


class EnhancedVetriageSystem:
    """
    Complete veterinary diagnostic system with all enhancements.
    
    Features:
    - Evidence-based diagnosis (PubMed + bioRxiv)
    - Clinical decision support (drug safety, alerts)
    - Professional SOAP reports (PDF/HTML)
    - Formatted bibliography (multiple styles)
    """
    
    def __init__(self, logo_path: Optional[str] = None):
        """
        Initialize enhanced system.
        
        Args:
            logo_path: Path to clinic logo for reports
        """
        logger.info("Initializing Enhanced VetrIAge System v2.1")
        
        # Core RAG system
        self.rag = initialize_rag_system()
        
        # Clinical decision support
        self.cds = ClinicalDecisionSupport()
        
        # Report generator
        self.report_gen = ClinicalReportGenerator(logo_path=logo_path)
        
        # Citation manager
        self.bib_gen = BibliographyGenerator(style='vancouver')
        
        # bioRxiv access
        self.biorxiv = BioRxivSearch()
        
        logger.info("✅ Enhanced VetrIAge System initialized successfully")
    
    def complete_diagnosis(
        self,
        case_data: Dict,
        veterinarian_name: str = "Dr. [Veterinarian Name]",
        clinic_name: str = "Veterinary Clinic",
        include_biorxiv: bool = True,
        generate_pdf: bool = True,
        citation_style: str = 'vancouver'
    ) -> Dict:
        """
        Complete diagnostic workflow with all enhancements.
        
        Args:
            case_data: Clinical case dictionary
            veterinarian_name: Veterinarian name for report
            clinic_name: Clinic name for report
            include_biorxiv: Search bioRxiv for pre-prints
            generate_pdf: Generate PDF report
            citation_style: Bibliography style (vancouver, apa, harvard, chicago)
        
        Returns:
            Complete diagnosis with reports, alerts, and citations
        """
        logger.info(f"🔬 Starting complete diagnosis for {case_data.get('species', 'unknown')} patient")
        
        # Step 1: Run RAG diagnosis
        logger.info("Step 1/6: Running RAG diagnosis...")
        diagnosis_result = self.rag.rag_diagnose(case_data)
        
        # Step 2: Search bioRxiv if requested
        if include_biorxiv and diagnosis_result.get('differential_diagnoses'):
            logger.info("Step 2/6: Searching bioRxiv for pre-prints...")
            primary_dx = diagnosis_result['differential_diagnoses'][0]['diagnosis']
            biorxiv_papers = self.biorxiv.search_veterinary(
                query=primary_dx,
                max_results=5
            )
            
            if biorxiv_papers:
                logger.info(f"Found {len(biorxiv_papers)} relevant pre-prints")
                # Add to cited papers
                diagnosis_result['cited_papers'].extend(biorxiv_papers)
                diagnosis_result['metadata']['biorxiv_papers_found'] = len(biorxiv_papers)
        
        # Step 3: Clinical decision support
        logger.info("Step 3/6: Running clinical decision support...")
        cds_result = self.cds.analyze_case(case_data, diagnosis_result)
        
        # Add alerts to diagnosis
        diagnosis_result['clinical_alerts'] = cds_result['alerts']
        diagnosis_result['alert_summary'] = cds_result['alert_count']
        diagnosis_result['clinical_pathways'] = cds_result['clinical_pathways']
        diagnosis_result['treatment_protocols'] = cds_result['treatment_protocols']
        
        # Log critical alerts
        if cds_result['alert_count']['critical'] > 0:
            logger.warning(f"⚠️  {cds_result['alert_count']['critical']} CRITICAL alerts detected!")
        
        # Step 4: Create SOAP report
        logger.info("Step 4/6: Generating SOAP clinical report...")
        soap_report = create_report_from_diagnosis(
            diagnosis_result,
            case_data,
            veterinarian_name=veterinarian_name,
            clinic_name=clinic_name
        )
        
        # Step 5: Generate formatted bibliography
        logger.info("Step 5/6: Formatting bibliography...")
        self.bib_gen.style = citation_style
        citations = create_citations_from_papers(diagnosis_result['cited_papers'])
        bibliography_html = self.bib_gen.generate(citations)
        
        # Export options
        bibliography_bibtex = self.bib_gen.export_bibtex(citations)
        bibliography_ris = self.bib_gen.export_ris(citations)
        
        # Step 6: Generate reports
        logger.info("Step 6/6: Generating final reports...")
        reports = {
            'html': self.report_gen.generate_html(soap_report),
            'bibliography_html': bibliography_html,
            'bibliography_bibtex': bibliography_bibtex,
            'bibliography_ris': bibliography_ris
        }
        
        if generate_pdf:
            try:
                pdf_bytes = self.report_gen.generate_pdf(soap_report)
                reports['pdf'] = pdf_bytes
                logger.info("✅ PDF report generated successfully")
            except Exception as e:
                logger.error(f"PDF generation failed: {e}")
                reports['pdf'] = None
        
        logger.info("✅ Complete diagnosis finished successfully")
        
        return {
            # Core diagnosis
            'differential_diagnoses': diagnosis_result['differential_diagnoses'],
            'diagnostic_plan': diagnosis_result['diagnostic_plan'],
            'immediate_actions': diagnosis_result['immediate_actions'],
            'cited_papers': diagnosis_result['cited_papers'],
            'metadata': diagnosis_result.get('metadata', {}),
            
            # Clinical decision support
            'clinical_alerts': diagnosis_result['clinical_alerts'],
            'alert_summary': diagnosis_result['alert_summary'],
            'clinical_pathways': diagnosis_result['clinical_pathways'],
            'treatment_protocols': diagnosis_result['treatment_protocols'],
            
            # Reports and exports
            'reports': reports,
            'soap_report': soap_report.to_dict(),
            
            # Status
            'status': 'success',
            'version': '2.1',
            'timestamp': diagnosis_result.get('metadata', {}).get('timestamp', '')
        }
    
    def quick_diagnosis(self, case_data: Dict) -> Dict:
        """
        Quick diagnosis without full reporting (faster).
        
        Args:
            case_data: Clinical case dictionary
        
        Returns:
            Basic diagnosis with alerts
        """
        # Run RAG diagnosis
        diagnosis_result = self.rag.rag_diagnose(case_data)
        
        # Run clinical decision support
        cds_result = self.cds.analyze_case(case_data, diagnosis_result)
        
        return {
            'differential_diagnoses': diagnosis_result['differential_diagnoses'],
            'diagnostic_plan': diagnosis_result['diagnostic_plan'],
            'immediate_actions': diagnosis_result['immediate_actions'],
            'clinical_alerts': cds_result['alerts'],
            'alert_summary': cds_result['alert_count'],
            'cited_papers_count': len(diagnosis_result['cited_papers']),
            'status': 'success'
        }


def create_enhanced_system(logo_path: Optional[str] = None) -> EnhancedVetriageSystem:
    """
    Factory function to create enhanced system.
    
    Args:
        logo_path: Path to clinic logo
    
    Returns:
        EnhancedVetriageSystem instance
    """
    return EnhancedVetriageSystem(logo_path=logo_path)
