"""
FastAPI Integration for VetrIAge RAG System
===========================================

RESTful API endpoints for RAG-powered veterinary diagnostics.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
import logging

from .vetriage_rag import VetriageRAG, initialize_rag_system

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="VetrIAge RAG API",
    description="Retrieval-Augmented Generation for Veterinary Diagnostics",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG system (singleton)
rag_system: Optional[VetriageRAG] = None


@app.on_event("startup")
async def startup_event():
    """Initialize RAG system on startup"""
    global rag_system
    try:
        rag_system = initialize_rag_system()
        logger.info("RAG system initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize RAG system: {e}")
        rag_system = None


# Pydantic models for request/response
class ClinicalCase(BaseModel):
    """Clinical case input model"""
    species: str = Field(..., description="Animal species (dog, cat, horse, etc.)")
    age: Optional[int] = Field(None, description="Age in years")
    sex: Optional[str] = Field(None, description="Sex (male, female, castrated, spayed)")
    chief_complaint: Optional[str] = Field(None, description="Main complaint or symptoms")
    symptoms: Optional[List[str]] = Field(None, description="List of symptoms")
    history: Optional[str] = Field(None, description="Medical history")
    physical_exam: Optional[str] = Field(None, description="Physical examination findings")
    labs: Optional[Dict[str, float]] = Field(None, description="Laboratory results")
    region: Optional[str] = Field(None, description="Geographic region")
    
    class Config:
        schema_extra = {
            "example": {
                "species": "cat",
                "age": 8,
                "sex": "male",
                "chief_complaint": "Polyuria, polydipsia, dehydration",
                "history": "Prednisolone 6 drops/day for 3 months",
                "physical_exam": "8% dehydration, dry mucous membranes",
                "labs": {
                    "glucose": 524,
                    "BUN": 45,
                    "creatinine": 1.8,
                    "hematocrit": 25,
                    "WBC": 24.2
                },
                "region": "Buenos Aires, Argentina"
            }
        }


class DifferentialDiagnosis(BaseModel):
    """Differential diagnosis model"""
    diagnosis: str
    probability: float
    grade_score: str
    rationale: str
    supporting_evidence: List[str]


class CitedPaper(BaseModel):
    """Cited paper model"""
    pmid: str
    title: str
    key_finding: Optional[str] = None
    relevance: Optional[str] = None


class DiagnosisResponse(BaseModel):
    """Diagnosis response model"""
    differential_diagnoses: List[DifferentialDiagnosis]
    diagnostic_plan: List[str]
    immediate_actions: List[str]
    cited_papers: List[CitedPaper]
    metadata: Optional[Dict] = None


class PubMedSearchRequest(BaseModel):
    """PubMed search request model"""
    query: str = Field(..., description="Search query string")
    max_results: int = Field(10, ge=1, le=100, description="Maximum results")
    filter_species: Optional[str] = Field(None, description="Species filter")


class PaperResponse(BaseModel):
    """Paper response model"""
    pmid: str
    title: str
    abstract: str
    authors: List[str]
    journal: str
    publication_date: str
    doi: Optional[str] = None
    similarity_score: Optional[float] = None


# API Endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "VetrIAge RAG API",
        "version": "2.0.0",
        "status": "operational" if rag_system else "degraded",
        "endpoints": [
            "/api/v2/diagnose",
            "/api/v2/search-pubmed",
            "/api/v2/expand-query",
            "/api/v2/health"
        ]
    }


@app.get("/api/v2/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy" if rag_system else "unhealthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "rag_system": "operational" if rag_system else "failed",
            "openai": "configured" if rag_system and rag_system.openai_client else "not configured",
            "anthropic": "configured" if rag_system and rag_system.anthropic_client else "not configured"
        }
    }


@app.post("/api/v2/diagnose", response_model=DiagnosisResponse)
async def diagnose(case: ClinicalCase, background_tasks: BackgroundTasks):
    """
    Generate evidence-based diagnosis using RAG pipeline.
    
    This endpoint:
    1. Expands query to optimized PubMed searches
    2. Retrieves relevant veterinary literature
    3. Performs semantic similarity matching
    4. Generates diagnosis with citations
    
    Returns diagnosis with differential diagnoses, diagnostic plan, 
    immediate actions, and cited scientific papers.
    """
    if not rag_system:
        raise HTTPException(
            status_code=503,
            detail="RAG system not initialized. Check API keys and dependencies."
        )
    
    try:
        logger.info(f"Processing diagnosis request for {case.species}")
        
        # Convert Pydantic model to dict
        case_dict = case.dict(exclude_none=True)
        
        # Run RAG diagnosis
        result = rag_system.rag_diagnose(case_dict)
        
        logger.info(f"Diagnosis completed successfully")
        return result
    
    except Exception as e:
        logger.error(f"Diagnosis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Diagnosis failed: {str(e)}")


@app.post("/api/v2/search-pubmed", response_model=List[PaperResponse])
async def search_pubmed(request: PubMedSearchRequest):
    """
    Search PubMed for veterinary literature.
    
    Returns list of papers with PMIDs, titles, abstracts, and metadata.
    """
    if not rag_system:
        raise HTTPException(
            status_code=503,
            detail="RAG system not initialized"
        )
    
    try:
        logger.info(f"PubMed search: {request.query}")
        
        papers = rag_system.search_pubmed_veterinary(
            query=request.query,
            max_results=request.max_results,
            filter_species=request.filter_species
        )
        
        # Convert Paper objects to dicts
        results = []
        for paper in papers:
            results.append({
                "pmid": paper.pmid,
                "title": paper.title,
                "abstract": paper.abstract,
                "authors": paper.authors,
                "journal": paper.journal,
                "publication_date": paper.publication_date,
                "doi": paper.doi,
                "similarity_score": paper.similarity_score
            })
        
        logger.info(f"Found {len(results)} papers")
        return results
    
    except Exception as e:
        logger.error(f"PubMed search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.post("/api/v2/expand-query")
async def expand_query(case: ClinicalCase, num_queries: int = 4):
    """
    Generate optimized PubMed search queries from clinical case.
    
    Returns list of query strings optimized for veterinary literature search.
    """
    if not rag_system:
        raise HTTPException(
            status_code=503,
            detail="RAG system not initialized"
        )
    
    try:
        logger.info(f"Expanding query for {case.species}")
        
        case_dict = case.dict(exclude_none=True)
        queries = rag_system.expand_query(case_dict, num_queries=num_queries)
        
        return {
            "queries": queries,
            "count": len(queries)
        }
    
    except Exception as e:
        logger.error(f"Query expansion failed: {e}")
        raise HTTPException(status_code=500, detail=f"Query expansion failed: {str(e)}")


@app.post("/api/v2/semantic-search", response_model=List[PaperResponse])
async def semantic_search(
    query: str,
    papers_data: List[Dict],
    top_k: int = 5,
    min_similarity: float = 0.5
):
    """
    Perform semantic similarity search on provided papers.
    
    Args:
        query: Query text for similarity matching
        papers_data: List of paper dictionaries to search
        top_k: Number of top results
        min_similarity: Minimum similarity threshold
    
    Returns list of most similar papers with similarity scores.
    """
    if not rag_system:
        raise HTTPException(
            status_code=503,
            detail="RAG system not initialized"
        )
    
    try:
        from .vetriage_rag import Paper
        
        # Convert dicts to Paper objects
        papers = []
        for p_data in papers_data:
            paper = Paper(
                pmid=p_data.get('pmid', ''),
                title=p_data.get('title', ''),
                abstract=p_data.get('abstract', ''),
                authors=p_data.get('authors', []),
                journal=p_data.get('journal', ''),
                publication_date=p_data.get('publication_date', '')
            )
            papers.append(paper)
        
        # Create vector store and search
        rag_system.create_vector_store(papers)
        results = rag_system.semantic_search(query, top_k=top_k, min_similarity=min_similarity)
        
        # Convert back to dicts
        response = []
        for paper in results:
            response.append({
                "pmid": paper.pmid,
                "title": paper.title,
                "abstract": paper.abstract,
                "authors": paper.authors,
                "journal": paper.journal,
                "publication_date": paper.publication_date,
                "doi": paper.doi,
                "similarity_score": paper.similarity_score
            })
        
        return response
    
    except Exception as e:
        logger.error(f"Semantic search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Semantic search failed: {str(e)}")


# Run with: uvicorn fastapi_integration:app --reload --port ${PORT:-8000}
# Or: PORT=9000 python fastapi_integration.py
if __name__ == "__main__":
    import os
    import uvicorn
    
    # Flexible port configuration
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"🚀 VetrIAge RAG API starting on {host}:{port}")
    logger.info(f"💡 Tip: Set PORT and HOST environment variables for custom configuration")
    
    uvicorn.run(app, host=host, port=port, log_level="info")
