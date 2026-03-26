"""
Enhanced FastAPI Integration for VetrIAge RAG System v2.1
==========================================================

Complete RESTful API with all advanced features:
- RAG diagnostics with PubMed + bioRxiv
- Safety alerts and contraindications
- Clinical report generation (PDF/HTML)
- Citation management
- Interactive visualizations
- Bibliography export

Author: VetrIAge Team
Version: 2.1.0
License: MIT
"""

import os
import logging
from fastapi import FastAPI, HTTPException, BackgroundTasks, File, UploadFile, Depends, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal
from datetime import datetime
import tempfile

# Import enhanced RAG system
from enhanced_vetriage import EnhancedVetriageRAG, quick_diagnose

# Import monetization layer
from monetization.database import init_db, create_api_key, get_usage_summary, validate_api_key, update_tier, deactivate_key
from monetization.models import Tier, TIER_CONFIG, ENDPOINT_COSTS_USD
from monetization.middleware import APIKeyAuthMiddleware, RateLimitMiddleware, UsageTrackingMiddleware

# Import legal pages (required by Paddle)
from legal_pages import router as legal_router

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="VetrIAge Enhanced RAG API",
    description="Complete Evidence-Based Veterinary Diagnostic System with Safety Alerts",
    version="2.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Legal pages (public, no auth required — needed for Paddle verification)
app.include_router(legal_router)

# Middleware stack (order matters: auth → rate limit → usage tracking)
# Usage tracking wraps the response, so it goes first (outermost)
app.add_middleware(UsageTrackingMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(APIKeyAuthMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global RAG system instance
enhanced_rag: Optional[EnhancedVetriageRAG] = None


@app.on_event("startup")
async def startup_event():
    """Initialize enhanced RAG system and billing database on startup"""
    global enhanced_rag

    # Initialize billing database
    try:
        init_db()
        logger.info("Billing database initialized")
    except Exception as e:
        logger.error(f"Failed to initialize billing DB: {e}")

    try:
        enhanced_rag = EnhancedVetriageRAG(
            enable_biorxiv=True,
            enable_safety_alerts=True,
            enable_visualizations=True,
            citation_style="apa"
        )
        logger.info("Enhanced VetrIAge RAG system initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize RAG system: {e}")
        enhanced_rag = None


# ==================== Pydantic Models ====================

class ClinicalCase(BaseModel):
    """Complete clinical case input"""
    # Patient identification
    patient_name: Optional[str] = Field(None, description="Patient name")
    species: str = Field(..., description="Animal species")
    breed: Optional[str] = Field(None, description="Breed")
    age: Optional[float] = Field(None, description="Age in years")
    sex: Optional[str] = Field(None, description="Sex")
    weight: Optional[float] = Field(None, description="Weight in kg")
    
    # Clinical information
    chief_complaint: str = Field(..., description="Main presenting complaint")
    history: Optional[str] = Field(None, description="Medical history")
    physical_exam: Optional[Dict[str, str]] = Field(None, description="Physical exam findings")
    lab_results: Optional[Dict[str, float]] = Field(None, description="Laboratory results")
    
    # Additional context
    current_medications: Optional[List[str]] = Field(None, description="Current medications")
    region: Optional[str] = Field(None, description="Geographic region")
    
    # Veterinarian info (for reports)
    veterinarian_name: Optional[str] = Field(None, description="Veterinarian name")
    clinic_name: Optional[str] = Field(None, description="Clinic name")
    
    class Config:
        json_schema_extra = {
            "example": {
                "patient_name": "Whiskers",
                "species": "cat",
                "breed": "Domestic Shorthair",
                "age": 12,
                "sex": "Male Castrated",
                "weight": 5.8,
                "chief_complaint": "Polyuria, polydipsia, weight loss for 3 weeks",
                "history": "Indoor cat, recent prednisone use (2mg daily for 3 months)",
                "physical_exam": {
                    "temperature": "38.5 C",
                    "heart_rate": "180 bpm",
                    "respiratory_rate": "32 breaths/min",
                    "hydration": "Mild dehydration (6%)",
                    "body_condition": "Thin (BCS 3/9)"
                },
                "lab_results": {
                    "glucose": 524,
                    "BUN": 38,
                    "creatinine": 1.8,
                    "WBC": 18.2,
                    "hematocrit": 28.5
                },
                "current_medications": ["prednisone"],
                "veterinarian_name": "Dr. Sarah Johnson",
                "clinic_name": "City Veterinary Hospital"
            }
        }


class DiagnosisRequest(BaseModel):
    """Diagnosis request with options"""
    clinical_case: ClinicalCase
    include_preprints: bool = Field(True, description="Include bioRxiv/medRxiv pre-prints")
    generate_report: bool = Field(False, description="Generate clinical report")
    report_format: Literal["pdf", "html", "markdown"] = Field("pdf", description="Report format")
    citation_style: Literal["apa", "vancouver", "nature", "javma"] = Field("apa", description="Citation style")


class SafetyCheckRequest(BaseModel):
    """Drug safety check request"""
    species: str = Field(..., description="Animal species")
    breed: Optional[str] = Field(None, description="Breed (if relevant)")
    age_years: Optional[float] = Field(None, description="Age in years")
    weight_kg: Optional[float] = Field(None, description="Weight in kg")
    current_medications: List[str] = Field(default_factory=list, description="Current medications")
    proposed_treatment: List[str] = Field(..., description="Proposed new medications")
    
    class Config:
        json_schema_extra = {
            "example": {
                "species": "dog",
                "breed": "Collie",
                "age_years": 5.0,
                "weight_kg": 25.0,
                "current_medications": ["prednisone"],
                "proposed_treatment": ["ivermectin", "carprofen"]
            }
        }


class CitationExportRequest(BaseModel):
    """Bibliography export request"""
    pmids: List[str] = Field(..., description="List of PubMed IDs to export")
    format: Literal["bibtex", "ris", "apa", "vancouver"] = Field("bibtex", description="Export format")


# ==================== API Endpoints ====================

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "service": "VetrIAge Enhanced RAG API",
        "version": "2.1.0",
        "status": "operational" if enhanced_rag else "initializing",
        "features": [
            "Evidence-based diagnostics (35M+ papers)",
            "Pre-print integration (bioRxiv/medRxiv)",
            "Safety alerts & contraindications",
            "Clinical report generation (SOAP/PDF)",
            "Citation management (APA/Vancouver/JAVMA/Nature)",
            "Interactive visualizations",
            "Species-specific recommendations"
        ],
        "documentation": "/docs",
        "health_check": "/api/v2/health"
    }


@app.get("/api/v2/health")
async def health_check():
    """Health check endpoint"""
    if not enhanced_rag:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unavailable",
                "message": "RAG system not initialized"
            }
        )
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.1.0",
        "features": {
            "pubmed_access": True,
            "biorxiv_access": enhanced_rag.enable_biorxiv,
            "safety_alerts": enhanced_rag.enable_safety_alerts,
            "visualizations": enhanced_rag.enable_visualizations,
            "citations": enhanced_rag.citation_manager is not None
        }
    }


@app.post("/api/v2/diagnose")
async def diagnose_enhanced(request: DiagnosisRequest):
    """
    Complete enhanced diagnostic endpoint
    
    Returns differential diagnoses with:
    - Evidence from PubMed + bioRxiv
    - Safety alerts and contraindications
    - Professional bibliography
    - Clinical report (optional)
    """
    if not enhanced_rag:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    try:
        logger.info(f"Diagnosis request: {request.clinical_case.species}, {request.clinical_case.age} years")
        
        # Convert Pydantic model to dict
        case_dict = request.clinical_case.model_dump()
        
        # Run enhanced diagnosis
        result = enhanced_rag.diagnose(
            clinical_case=case_dict,
            include_preprints=request.include_preprints,
            generate_report=request.generate_report,
            report_format=request.report_format
        )
        
        logger.info(f"Diagnosis complete: {len(result.get('differential_diagnoses', []))} DDx generated")
        
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Diagnosis error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v2/safety-check")
async def safety_check(request: SafetyCheckRequest):
    """
    Check drug safety and contraindications
    
    Returns:
    - Species-specific contraindications
    - Breed-specific warnings (e.g., MDR1 mutation)
    - Drug-drug interactions
    - Age/weight-based dosing alerts
    """
    try:
        from safety_alerts import generate_safety_report
        
        report = generate_safety_report(
            species=request.species,
            breed=request.breed,
            age_years=request.age_years,
            weight_kg=request.weight_kg,
            current_medications=request.current_medications,
            proposed_treatment=request.proposed_treatment
        )
        
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "safety_report": report
        }
        
    except Exception as e:
        logger.error(f"Safety check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class LiteratureSearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    include_preprints: bool = Field(True, description="Include pre-prints")
    max_results: int = Field(20, description="Maximum results")


@app.post("/api/v2/search-literature")
async def search_literature(request: LiteratureSearchRequest):
    """
    Search veterinary literature (PubMed + bioRxiv)
    
    Returns:
    - Relevant papers with abstracts
    - Pre-prints (if enabled)
    - Sorted by relevance
    """
    if not enhanced_rag:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    try:
        results = {
            "pubmed_papers": [],
            "preprints": []
        }
        
        # Search PubMed
        pubmed_ids = enhanced_rag.rag.search_pubmed_veterinary(request.query, request.max_results)
        if pubmed_ids:
            papers = enhanced_rag.rag.fetch_papers(pubmed_ids)
            results["pubmed_papers"] = [
                {
                    "pmid": p.pmid,
                    "title": p.title,
                    "abstract": p.abstract[:500] + "..." if len(p.abstract) > 500 else p.abstract,
                    "authors": p.authors,
                    "journal": getattr(p, 'journal', 'Unknown'),
                    "date": getattr(p, 'date', 'Unknown')
                }
                for p in papers[:request.max_results]
            ]

        # Search bioRxiv if enabled
        if request.include_preprints and enhanced_rag.enable_biorxiv:
            from biorxiv_integration import search_veterinary_preprints
            preprints = search_veterinary_preprints(request.query, max_results=10)
            results["preprints"] = preprints

        return {
            "status": "success",
            "query": request.query,
            "total_results": len(results["pubmed_papers"]) + len(results["preprints"]),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Literature search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v2/export-bibliography")
async def export_bibliography(request: CitationExportRequest):
    """
    Export bibliography in various formats
    
    Supports:
    - BibTeX (for LaTeX)
    - RIS (for EndNote, Mendeley)
    - APA style
    - Vancouver style
    """
    try:
        from citation_management import CitationManager, Citation
        
        manager = CitationManager()
        
        # Fetch papers and create citations
        if enhanced_rag:
            papers = enhanced_rag.rag.fetch_papers(request.pmids)
            for paper in papers:
                citation = Citation(
                    pmid=paper.pmid,
                    title=paper.title,
                    authors=paper.authors,
                    journal=getattr(paper, 'journal', 'Unknown'),
                    year=int(getattr(paper, 'date', '0000')[:4]) if hasattr(paper, 'date') else 0,
                    abstract=paper.abstract
                )
                manager.add_citation(citation)
        
        # Generate bibliography
        bibliography = manager.generate_bibliography(style=request.format)
        
        return {
            "status": "success",
            "format": request.format,
            "citation_count": len(manager.citations),
            "bibliography": bibliography
        }
        
    except Exception as e:
        logger.error(f"Bibliography export error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v2/visualizations/{diagnosis_id}")
async def get_visualizations(diagnosis_id: str):
    """
    Get diagnostic visualizations
    
    Returns:
    - Confidence score chart
    - DDx comparison radar chart
    - Evidence strength distribution
    """
    # This would typically retrieve from a database or cache
    # For now, return a placeholder
    return {
        "status": "success",
        "diagnosis_id": diagnosis_id,
        "visualizations": {
            "confidence_chart": f"/static/viz/{diagnosis_id}/confidence.png",
            "ddx_comparison": f"/static/viz/{diagnosis_id}/comparison.png",
            "evidence_strength": f"/static/viz/{diagnosis_id}/evidence.png"
        }
    }


@app.get("/api/v2/species-info/{species}")
async def get_species_info(species: str):
    """
    Get species-specific clinical information
    
    Returns:
    - Common diseases
    - Drug contraindications
    - Normal lab ranges
    - Breed-specific issues
    """
    try:
        from safety_alerts import SpeciesContraindicationDatabase
        
        db = SpeciesContraindicationDatabase()
        alerts = db.get_alerts_for_species(species.lower())
        
        return {
            "status": "success",
            "species": species,
            "contraindication_count": len(alerts),
            "major_contraindications": [
                {
                    "title": alert.title,
                    "severity": alert.severity.value,
                    "drugs": alert.contraindicated_drugs
                }
                for alert in alerts
                if alert.severity.value in ['critical', 'high']
            ]
        }
        
    except Exception as e:
        logger.error(f"Species info error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Monetization Endpoints ====================

class RegisterRequest(BaseModel):
    email: str = Field(..., description="Owner email")
    name: Optional[str] = Field(None, description="Owner name or clinic name")
    tier: Tier = Field(Tier.FREE, description="Subscription tier")


@app.get("/api/v2/pricing")
async def get_pricing():
    """Public endpoint: show available tiers and pricing"""
    tiers = {}
    for tier, config in TIER_CONFIG.items():
        tiers[tier.value] = {
            "name": config["name"],
            "price_monthly_usd": config["price_monthly_usd"],
            "requests_per_month": config["requests_per_month"],
            "requests_per_minute": config["requests_per_minute"],
            "features": {
                "report_generation": config["report_generation"],
                "literature_search": config["literature_search"],
                "bibliography_export": config["bibliography_export"],
                "priority_support": config["priority_support"],
            },
        }
    return {
        "service": "VetrIAge API",
        "tiers": tiers,
        "cost_per_endpoint": ENDPOINT_COSTS_USD,
        "signup": "POST /api/v2/register",
    }


@app.post("/api/v2/register")
async def register_api_key(request: RegisterRequest):
    """
    Register for an API key.
    Returns the raw API key — store it securely, it's shown only once.
    """
    admin_secret = os.getenv("VETRIAGE_ADMIN_SECRET")

    # For paid tiers, could integrate Stripe here; for now, admin-gated
    if request.tier != Tier.FREE and not admin_secret:
        raise HTTPException(
            status_code=400,
            detail="Paid tier registration requires contacting sales. Use tier='free' to get started.",
        )

    try:
        key_id, raw_key = create_api_key(
            owner_email=request.email,
            owner_name=request.name,
            tier=request.tier,
        )
        tier_config = TIER_CONFIG[request.tier]
        return {
            "status": "success",
            "message": "API key created. Store it securely — it won't be shown again.",
            "key_id": key_id,
            "api_key": raw_key,
            "tier": request.tier.value,
            "limits": {
                "requests_per_month": tier_config["requests_per_month"],
                "requests_per_minute": tier_config["requests_per_minute"],
            },
            "usage": "Pass your key via X-API-Key header or ?api_key= query param.",
        }
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create API key.")


@app.get("/api/v2/usage")
async def get_usage(request: Request):
    """Get usage dashboard for current API key. Requires auth."""
    key_record = getattr(request.state, "api_key", None)
    if not key_record:
        raise HTTPException(status_code=401, detail="API key required")

    summary = get_usage_summary(key_record.key_id)
    tier_config = TIER_CONFIG[key_record.tier]

    return {
        "key_id": key_record.key_id,
        "tier": key_record.tier.value,
        "limits": {
            "requests_per_month": tier_config["requests_per_month"],
            "requests_per_minute": tier_config["requests_per_minute"],
        },
        "usage": summary,
    }


# ==================== Admin Endpoints ====================

def _verify_admin(request: Request):
    """Check for admin secret in X-Admin-Secret header."""
    admin_secret = os.getenv("VETRIAGE_ADMIN_SECRET")
    if not admin_secret:
        raise HTTPException(status_code=503, detail="Admin not configured")
    provided = request.headers.get("X-Admin-Secret")
    if provided != admin_secret:
        raise HTTPException(status_code=403, detail="Invalid admin secret")


@app.post("/api/v2/admin/upgrade")
async def admin_upgrade_tier(request: Request, key_id: str = Query(...), new_tier: Tier = Query(...)):
    """Admin: upgrade a user's tier (after payment confirmation)."""
    _verify_admin(request)
    update_tier(key_id, new_tier)
    return {"status": "success", "key_id": key_id, "new_tier": new_tier.value}


@app.post("/api/v2/admin/deactivate")
async def admin_deactivate(request: Request, key_id: str = Query(...)):
    """Admin: deactivate an API key."""
    _verify_admin(request)
    deactivate_key(key_id)
    return {"status": "success", "key_id": key_id, "active": False}


# ==================== Run Server ====================

if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment or use default
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"Starting VetrIAge Enhanced RAG API on {host}:{port}")
    
    uvicorn.run(
        "fastapi_enhanced:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
