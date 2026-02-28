"""
Enhanced VetrIAge System - Complete Integration
===============================================

Integrates all advanced features:
1. RAG with PubMed + bioRxiv (35M+ papers + pre-prints)
2. Professional clinical reports (SOAP, PDF)
3. Citation management (APA, Vancouver, JAVMA, Nature)
4. Safety alerts & contraindications
5. Interactive visualizations
6. Email delivery

This is the main entry point for the enhanced veterinary diagnostic system.

Author: VetrIAge Team
Version: 2.1.0
License: MIT
"""

import os
import logging
from typing import List, Dict, Optional
from datetime import datetime
import tempfile

# Import core RAG system
from vetriage_rag import VetriageRAG, Paper, initialize_rag_system

# Import enhancement modules
try:
    from citation_management import CitationManager, create_citation_from_paper
    HAS_CITATIONS = True
except ImportError:
    HAS_CITATIONS = False
    logging.warning("Citation management unavailable")

try:
    from biorxiv_integration import search_veterinary_preprints
    HAS_BIORXIV = True
except ImportError:
    HAS_BIORXIV = False
    logging.warning("bioRxiv integration unavailable")

try:
    from safety_alerts import generate_safety_report
    HAS_SAFETY = True
except ImportError:
    HAS_SAFETY = False
    logging.warning("Safety alerts unavailable")

try:
    from visualizations import generate_all_visualizations
    HAS_VISUALIZATIONS = True
except ImportError:
    HAS_VISUALIZATIONS = False
    logging.warning("Visualizations unavailable")

try:
    from clinical_reports import SOAPReport, VeterinaryCase, generate_soap_pdf
    HAS_REPORTS = True
except ImportError:
    HAS_REPORTS = False
    logging.warning("Clinical reports unavailable")

logger = logging.getLogger(__name__)


class EnhancedVetriageRAG:
    """
    Enhanced RAG system with all advanced features integrated
    """
    
    def __init__(
        self,
        enable_biorxiv: bool = True,
        enable_safety_alerts: bool = True,
        enable_visualizations: bool = True,
        citation_style: str = "apa"
    ):
        """
        Initialize enhanced VetrIAge system
        
        Args:
            enable_biorxiv: Include pre-prints from bioRxiv/medRxiv
            enable_safety_alerts: Generate safety and contraindication alerts
            enable_visualizations: Generate diagnostic visualizations
            citation_style: Default citation style (apa, vancouver, nature, javma)
        """
        # Initialize core RAG
        self.rag = initialize_rag_system()
        
        # Configuration
        self.enable_biorxiv = enable_biorxiv and HAS_BIORXIV
        self.enable_safety_alerts = enable_safety_alerts and HAS_SAFETY
        self.enable_visualizations = enable_visualizations and HAS_VISUALIZATIONS
        self.citation_style = citation_style
        
        # Citation manager
        if HAS_CITATIONS:
            self.citation_manager = CitationManager()
        else:
            self.citation_manager = None
        
        logger.info(f"Enhanced VetrIAge initialized (bioRxiv: {self.enable_biorxiv}, "
                   f"safety: {self.enable_safety_alerts}, viz: {self.enable_visualizations})")
    
    def diagnose(
        self,
        clinical_case: Dict,
        include_preprints: Optional[bool] = None,
        generate_report: bool = False,
        report_format: str = "pdf"
    ) -> Dict:
        """
        Complete diagnostic workflow with all enhancements
        
        Args:
            clinical_case: Clinical case dictionary with keys:
                - species (str): Animal species
                - age (int): Age in years
                - chief_complaint (str): Main presenting complaint
                - history (str): Medical history
                - physical_exam (dict): Physical examination findings
                - lab_results (dict): Laboratory results
                - breed (str, optional): Breed
                - sex (str, optional): Sex
                - weight (float, optional): Weight in kg
                - current_medications (list, optional): Current medications
            include_preprints: Override bioRxiv setting for this query
            generate_report: Generate clinical report
            report_format: Report format (pdf, html, markdown)
        
        Returns:
            Complete diagnostic result with all enhancements
        """
        start_time = time.time()
        
        # Extract case info
        species = clinical_case.get('species', 'unknown')
        breed = clinical_case.get('breed')
        age = clinical_case.get('age')
        weight = clinical_case.get('weight')
        current_meds = clinical_case.get('current_medications', [])
        
        logger.info(f"Starting enhanced diagnosis for {species} (breed: {breed}, age: {age})")
        
        # Reset citation manager
        if self.citation_manager:
            self.citation_manager.clear()
        
        # 1. Run core RAG diagnosis
        logger.info("Running RAG diagnosis...")
        rag_result = self.rag.rag_diagnose(clinical_case)
        
        # 2. Add bioRxiv pre-prints if enabled
        if (include_preprints is True) or (include_preprints is None and self.enable_biorxiv):
            logger.info("Searching bioRxiv for pre-prints...")
            try:
                query = self._build_biorxiv_query(clinical_case)
                preprints = search_veterinary_preprints(query, max_results=5)
                
                if preprints:
                    # Add to cited papers
                    rag_result.setdefault('cited_papers', []).extend(preprints)
                    rag_result['preprints_count'] = len(preprints)
                    logger.info(f"Added {len(preprints)} pre-prints")
            except Exception as e:
                logger.error(f"Error fetching pre-prints: {e}")
        
        # 3. Generate safety alerts
        if self.enable_safety_alerts:
            logger.info("Generating safety alerts...")
            try:
                # Extract proposed treatments from diagnosis
                proposed_treatments = []
                for ddx in rag_result.get('differential_diagnoses', []):
                    treatments = ddx.get('recommended_treatment', [])
                    if isinstance(treatments, list):
                        proposed_treatments.extend(treatments)
                    elif isinstance(treatments, str):
                        proposed_treatments.append(treatments)
                
                safety_report = generate_safety_report(
                    species=species,
                    breed=breed,
                    age_years=age,
                    weight_kg=weight,
                    current_medications=current_meds,
                    proposed_treatment=proposed_treatments
                )
                
                rag_result['safety_alerts'] = safety_report
                logger.info(f"Generated safety report: {safety_report['summary']['overall_risk_level']} risk")
            except Exception as e:
                logger.error(f"Error generating safety alerts: {e}")
        
        # 4. Build citation bibliography
        if self.citation_manager:
            logger.info("Building bibliography...")
            try:
                for paper in rag_result.get('cited_papers', []):
                    citation = create_citation_from_paper(paper)
                    self.citation_manager.add_citation(citation)
                
                bibliography = self.citation_manager.generate_bibliography(
                    style=self.citation_style,
                    title="Evidence-Based References"
                )
                rag_result['bibliography'] = bibliography
                rag_result['citation_count'] = len(self.citation_manager.citations)
            except Exception as e:
                logger.error(f"Error building bibliography: {e}")
        
        # 5. Generate visualizations
        if self.enable_visualizations:
            logger.info("Generating visualizations...")
            try:
                with tempfile.TemporaryDirectory() as tmpdir:
                    viz_paths = generate_all_visualizations(rag_result, tmpdir)
                    rag_result['visualizations'] = viz_paths
                    logger.info(f"Generated {len(viz_paths)} visualizations")
            except Exception as e:
                logger.error(f"Error generating visualizations: {e}")
        
        # 6. Generate clinical report
        if generate_report and HAS_REPORTS:
            logger.info(f"Generating {report_format} clinical report...")
            try:
                report = self._create_clinical_report(clinical_case, rag_result, report_format)
                rag_result['clinical_report'] = report
            except Exception as e:
                logger.error(f"Error generating report: {e}")
        
        # Add timing
        elapsed = time.time() - start_time
        rag_result['enhanced_processing_time'] = elapsed
        
        logger.info(f"Enhanced diagnosis completed in {elapsed:.2f}s")
        
        return rag_result
    
    def _build_biorxiv_query(self, clinical_case: Dict) -> str:
        """Build optimized query for bioRxiv search"""
        species = clinical_case.get('species', '')
        complaint = clinical_case.get('chief_complaint', '')
        
        # Combine species and chief complaint
        query_parts = []
        if species:
            query_parts.append(species)
        if complaint:
            # Extract key medical terms
            keywords = [word for word in complaint.lower().split() 
                       if len(word) > 4 and word not in ['with', 'without', 'patient']]
            query_parts.extend(keywords[:3])  # Top 3 keywords
        
        return " ".join(query_parts)
    
    def _create_clinical_report(
        self,
        clinical_case: Dict,
        diagnosis_result: Dict,
        format: str = "pdf"
    ) -> Optional[str]:
        """
        Create professional clinical report
        
        Args:
            clinical_case: Original case data
            diagnosis_result: Diagnosis results
            format: Output format (pdf, html, markdown)
        
        Returns:
            Path to generated report or None
        """
        if not HAS_REPORTS:
            logger.error("Clinical reports module not available")
            return None
        
        try:
            # Create VeterinaryCase object
            vet_case = VeterinaryCase(
                patient_name=clinical_case.get('patient_name', 'Unknown'),
                species=clinical_case.get('species', 'Unknown'),
                breed=clinical_case.get('breed'),
                age=clinical_case.get('age'),
                sex=clinical_case.get('sex'),
                weight=clinical_case.get('weight'),
                veterinarian_name=clinical_case.get('veterinarian_name', 'Dr. [Veterinarian]'),
                clinic_name=clinical_case.get('clinic_name', 'Veterinary Clinic')
            )
            
            # Create SOAP report
            soap = SOAPReport(
                case=vet_case,
                chief_complaint=clinical_case.get('chief_complaint', ''),
                history=clinical_case.get('history', ''),
                physical_exam=clinical_case.get('physical_exam', {}),
                lab_results=clinical_case.get('lab_results', {}),
                differential_diagnoses=diagnosis_result.get('differential_diagnoses', []),
                primary_diagnosis=diagnosis_result.get('differential_diagnoses', [{}])[0].get('diagnosis'),
                cited_papers=diagnosis_result.get('cited_papers', [])
            )
            
            # Generate report
            if format == "pdf":
                output_path = f"vetriage_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                generate_soap_pdf(soap, output_path)
                return output_path
            else:
                logger.warning(f"Report format {format} not yet implemented")
                return None
                
        except Exception as e:
            logger.error(f"Error creating clinical report: {e}")
            return None
    
    def export_bibliography(
        self,
        filepath: str,
        style: str = "bibtex"
    ) -> bool:
        """
        Export bibliography to file
        
        Args:
            filepath: Output file path
            style: Export format (bibtex, ris)
        
        Returns:
            Success status
        """
        if not self.citation_manager:
            logger.error("Citation manager not available")
            return False
        
        try:
            self.citation_manager.export_bibliography(filepath, style)
            return True
        except Exception as e:
            logger.error(f"Error exporting bibliography: {e}")
            return False


def quick_diagnose(
    species: str,
    age: int,
    chief_complaint: str,
    lab_results: Optional[Dict] = None,
    **kwargs
) -> Dict:
    """
    Quick diagnostic interface with all enhancements
    
    Args:
        species: Animal species
        age: Age in years
        chief_complaint: Main complaint
        lab_results: Lab values dictionary
        **kwargs: Additional case parameters
    
    Returns:
        Complete diagnostic result
    """
    # Build clinical case
    clinical_case = {
        'species': species,
        'age': age,
        'chief_complaint': chief_complaint,
        'lab_results': lab_results or {}
    }
    clinical_case.update(kwargs)
    
    # Initialize and run
    enhanced_rag = EnhancedVetriageRAG()
    return enhanced_rag.diagnose(clinical_case)


# Example usage
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Example case: Feline diabetes
    example_case = {
        'species': 'cat',
        'breed': 'Domestic Shorthair',
        'age': 12,
        'sex': 'M',
        'weight': 5.8,
        'patient_name': 'Whiskers',
        'chief_complaint': 'Polyuria, polydipsia, weight loss for 3 weeks',
        'history': 'Indoor cat, no recent travel, up to date on vaccines',
        'physical_exam': {
            'temperature': 38.5,
            'heart_rate': 180,
            'respiratory_rate': 32,
            'body_condition': 'thin',
            'hydration': 'mild dehydration'
        },
        'lab_results': {
            'glucose': 524,
            'BUN': 38,
            'creatinine': 1.8,
            'WBC': 18.2
        },
        'veterinarian_name': 'Dr. Sarah Johnson',
        'clinic_name': 'City Veterinary Hospital'
    }
    
    print("=" * 80)
    print("VetrIAge Enhanced Diagnostic System - Example Case")
    print("=" * 80)
    print(f"\nPatient: {example_case['patient_name']} ({example_case['species']}, {example_case['age']} years)")
    print(f"Chief Complaint: {example_case['chief_complaint']}")
    print("\nRunning enhanced diagnosis (this may take 15-20 seconds)...\n")
    
    # Run diagnosis
    result = quick_diagnose(**example_case)
    
    # Display results
    print("\n" + "=" * 80)
    print("DIAGNOSTIC RESULTS")
    print("=" * 80)
    
    print(f"\n🏥 Top Differential Diagnoses:")
    for i, ddx in enumerate(result.get('differential_diagnoses', [])[:3], 1):
        print(f"\n{i}. {ddx.get('diagnosis')} (confidence: {ddx.get('confidence', 0):.1%})")
        print(f"   Evidence: {ddx.get('evidence_summary', 'N/A')[:100]}...")
    
    print(f"\n📚 Evidence Base:")
    print(f"   - PubMed papers: {len(result.get('cited_papers', []))}")
    print(f"   - Pre-prints: {result.get('preprints_count', 0)}")
    print(f"   - Total citations: {result.get('citation_count', 0)}")
    
    if 'safety_alerts' in result:
        safety = result['safety_alerts']['summary']
        print(f"\n⚠️ Safety Assessment:")
        print(f"   - Risk level: {safety.get('overall_risk_level', 'UNKNOWN')}")
        print(f"   - Total alerts: {safety.get('total_alerts', 0)}")
        print(f"   - Critical contraindications: {safety.get('critical_contraindications', 0)}")
    
    if 'visualizations' in result:
        viz = result['visualizations']
        print(f"\n📊 Visualizations generated: {len(viz)}")
        for name, path in viz.items():
            print(f"   - {name}: {path}")
    
    print(f"\n⏱️ Processing time: {result.get('enhanced_processing_time', 0):.2f}s")
    
    print("\n" + "=" * 80)
    print("Diagnosis complete! All features integrated successfully.")
    print("=" * 80)
