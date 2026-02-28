"""
VetrIAge RAG Module v2.1
========================

Enhanced veterinary diagnostic system with:
- RAG with PubMed + bioRxiv
- Clinical decision support
- Professional report generation
- Citation management

NEW in v2.1:
- Clinical reports (SOAP format, PDF/HTML)
- Citation management (APA, Vancouver, Harvard, Chicago)
- Clinical decision support with drug safety alerts
- bioRxiv pre-print access
- Species-specific contraindication database
"""

# Core RAG
from .vetriage_rag import (
    VetriageRAG,
    Paper,
    initialize_rag_system,
    quick_diagnosis
)

# Enhanced system (RECOMMENDED)
from .enhanced_diagnostics import (
    EnhancedVetriageSystem,
    create_enhanced_system
)

# Clinical decision support
from .clinical_decision_support import (
    ClinicalDecisionSupport,
    ClinicalAlert,
    AlertSeverity,
    DrugSafetyDatabase
)

# Clinical reports
from .clinical_reports import (
    ClinicalReportGenerator,
    SOAPReport,
    VeterinaryCase,
    create_report_from_diagnosis
)

# Citation management
from .citation_management import (
    BibliographyGenerator,
    CitationFormatter,
    Citation,
    create_citations_from_papers
)

# bioRxiv search
from .biorxiv_search import BioRxivSearch

__all__ = [
    # Core RAG
    'VetriageRAG',
    'Paper',
    'initialize_rag_system',
    'quick_diagnosis',
    
    # Enhanced system (⭐ RECOMMENDED)
    'EnhancedVetriageSystem',
    'create_enhanced_system',
    
    # Clinical decision support
    'ClinicalDecisionSupport',
    'ClinicalAlert',
    'AlertSeverity',
    'DrugSafetyDatabase',
    
    # Clinical reports
    'ClinicalReportGenerator',
    'SOAPReport',
    'VeterinaryCase',
    'create_report_from_diagnosis',
    
    # Citation management
    'BibliographyGenerator',
    'CitationFormatter',
    'Citation',
    'create_citations_from_papers',
    
    # bioRxiv
    'BioRxivSearch'
]

__version__ = '2.1.0'
__author__ = 'VetrIAge Team'
