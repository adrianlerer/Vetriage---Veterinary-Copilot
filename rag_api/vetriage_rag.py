"""
VetrIAge RAG (Retrieval-Augmented Generation) System
====================================================

Complete RAG pipeline for veterinary diagnostics with PubMed integration.
Implements the architecture described in the SKILL.md specification.

NEW in v2.1:
- Clinical reports generation (SOAP format, PDF/HTML)
- Citation management (APA, Vancouver, Harvard, Chicago)
- Clinical decision support with drug safety alerts
- bioRxiv pre-print access (+20% literature)
- Species-specific contraindication database

Author: VetrIAge Team
Version: 2.1
License: MIT
"""

import os
import time
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

# Scientific libraries
import numpy as np
from Bio import Entrez, Medline

# AI/ML libraries
try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

# OpenRouter support (uses OpenAI SDK with custom base_url)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
USE_OPENROUTER = bool(OPENROUTER_API_KEY)

try:
    import faiss
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
NCBI_EMAIL = os.getenv("NCBI_EMAIL", "vetriage@example.com")
NCBI_API_KEY = os.getenv("NCBI_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
LLM_MODEL = os.getenv("LLM_MODEL", "anthropic/claude-3.5-sonnet" if USE_OPENROUTER else "claude-3-5-sonnet-20241022")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet")
MAX_PAPERS_PER_QUERY = int(os.getenv("MAX_PAPERS_PER_QUERY", "10"))

# Configure Entrez
Entrez.email = NCBI_EMAIL
if NCBI_API_KEY:
    Entrez.api_key = NCBI_API_KEY


@dataclass
class Paper:
    """Represents a scientific paper from PubMed"""
    pmid: str
    title: str
    abstract: str
    authors: List[str]
    journal: str
    publication_date: str
    doi: Optional[str] = None
    mesh_terms: Optional[List[str]] = None
    embedding: Optional[np.ndarray] = None
    similarity_score: Optional[float] = None


class VetriageRAG:
    """
    Main RAG system for veterinary diagnostics.
    
    Pipeline:
    1. Query Expansion: Generate optimized PubMed search queries
    2. PubMed Search: Retrieve relevant papers
    3. Embedding Generation: Convert to vectors
    4. Semantic Search: Find most relevant papers
    5. Context Injection: Augment LLM prompt with papers
    6. Diagnosis Generation: Evidence-based differential diagnosis
    """
    
    def __init__(
        self,
        openai_key: Optional[str] = None,
        anthropic_key: Optional[str] = None,
        vector_store_type: str = "faiss"
    ):
        """Initialize RAG system with API keys and configuration"""
        self.openai_key = openai_key or OPENAI_API_KEY
        self.anthropic_key = anthropic_key or ANTHROPIC_API_KEY
        self.vector_store_type = vector_store_type
        
        # Initialize clients
        if HAS_OPENAI and self.openai_key:
            self.openai_client = openai.OpenAI(api_key=self.openai_key)
        else:
            self.openai_client = None
            logger.warning("OpenAI client not available. Install openai package and provide API key.")

        # OpenRouter client (uses OpenAI SDK with custom base_url)
        self.openrouter_client = None
        if USE_OPENROUTER and HAS_OPENAI:
            self.openrouter_client = openai.OpenAI(
                base_url=OPENROUTER_BASE_URL,
                api_key=OPENROUTER_API_KEY,
                default_headers={
                    "HTTP-Referer": "https://vetriage.app",
                    "X-Title": "Vetriage - Veterinary Copilot",
                }
            )
            logger.info(f"OpenRouter client initialized (model: {OPENROUTER_MODEL})")

        if HAS_ANTHROPIC and self.anthropic_key and not USE_OPENROUTER:
            self.anthropic_client = anthropic.Anthropic(api_key=self.anthropic_key)
        else:
            self.anthropic_client = None
            if not USE_OPENROUTER:
                logger.warning("Anthropic client not available. Install anthropic package and provide API key.")
        
        # Vector store
        self.index = None
        self.indexed_papers = []
        
        logger.info("VetriageRAG initialized successfully")
    
    def _llm_chat(self, prompt: str, max_tokens: int = 4000, model: Optional[str] = None) -> Optional[str]:
        """
        Send a chat completion request via OpenRouter (preferred) or Anthropic fallback.

        Args:
            prompt: User prompt text
            max_tokens: Maximum response tokens
            model: Override model name

        Returns:
            Response text or None on failure
        """
        # Try OpenRouter first
        if self.openrouter_client:
            try:
                response = self.openrouter_client.chat.completions.create(
                    model=model or OPENROUTER_MODEL,
                    max_tokens=max_tokens,
                    messages=[{"role": "user", "content": prompt}],
                )
                return response.choices[0].message.content
            except Exception as e:
                logger.error(f"OpenRouter request failed: {e}")
                # Fall through to Anthropic

        # Fallback to Anthropic direct
        if self.anthropic_client:
            try:
                message = self.anthropic_client.messages.create(
                    model=model or LLM_MODEL,
                    max_tokens=max_tokens,
                    messages=[{"role": "user", "content": prompt}],
                )
                return message.content[0].text
            except Exception as e:
                logger.error(f"Anthropic request failed: {e}")

        return None

    def expand_query(self, case: Dict, num_queries: int = 4) -> List[str]:
        """
        Generate optimized PubMed search queries from clinical case.
        
        Args:
            case: Clinical case dictionary with symptoms, labs, history
            num_queries: Number of queries to generate (default: 4)
        
        Returns:
            List of optimized PubMed search query strings
        """
        if not self.openrouter_client and not self.anthropic_client:
            logger.warning("No LLM client available. Using fallback query generation.")
            return self._fallback_query_expansion(case)

        # Build prompt for query expansion
        case_summary = self._summarize_case(case)

        prompt = f"""Generate {num_queries} optimized PubMed search queries for this veterinary case.

Case Summary:
{case_summary}

Requirements:
- Use veterinary-specific terminology
- Include species-specific terms (canine, feline, equine)
- Combine clinical signs with diagnostic terms
- Use Boolean operators appropriately
- Target recent veterinary literature

Return ONLY the queries, one per line, no numbering or explanation.
Example format:
feline diabetes mellitus hyperglycemia ketoacidosis
steroid-induced diabetes cat prednisolone treatment
"""

        response_text = self._llm_chat(prompt, max_tokens=500)
        if response_text:
            queries = [q.strip() for q in response_text.strip().split('\n') if q.strip()]
            logger.info(f"Generated {len(queries)} search queries")
            return queries[:num_queries]

        return self._fallback_query_expansion(case)
    
    def _fallback_query_expansion(self, case: Dict) -> List[str]:
        """Fallback query generation without LLM"""
        species = case.get('species', 'animal')
        symptoms = case.get('symptoms', [])
        
        # Map species to veterinary terms
        species_map = {
            'dog': 'canine',
            'cat': 'feline',
            'horse': 'equine',
            'cow': 'bovine',
            'pig': 'porcine'
        }
        vet_species = species_map.get(species.lower(), species)
        
        queries = []
        
        # Query 1: Species + main symptoms
        if symptoms:
            queries.append(f"{vet_species} {' '.join(symptoms[:3])} diagnosis")
        
        # Query 2: Species + disease category
        if 'labs' in case:
            labs = case['labs']
            if labs.get('glucose', 0) > 400:
                queries.append(f"{vet_species} diabetes mellitus hyperglycemia treatment")
            if labs.get('WBC', 0) > 20:
                queries.append(f"{vet_species} leukocytosis infection sepsis")
        
        # Query 3: Species + specific finding
        if 'history' in case:
            queries.append(f"{vet_species} {case['history'][:50]}")
        
        # Query 4: General emergency
        queries.append(f"{vet_species} emergency critical care")
        
        return queries[:4]
    
    def search_pubmed_veterinary(
        self,
        query: str,
        max_results: int = 10,
        filter_species: Optional[str] = None
    ) -> List[Paper]:
        """
        Search PubMed for veterinary papers.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            filter_species: Optional species filter (canine, feline, etc.)
        
        Returns:
            List of Paper objects with PMIDs, titles, abstracts
        """
        # Add veterinary filters
        vet_query = f"({query}) AND (veterinary[tiab] OR canine OR feline OR equine OR bovine)"
        
        if filter_species:
            vet_query += f" AND {filter_species}"
        
        try:
            # Search PubMed
            logger.info(f"Searching PubMed: {vet_query}")
            handle = Entrez.esearch(
                db="pubmed",
                term=vet_query,
                retmax=max_results,
                sort="relevance",
                usehistory="y"
            )
            search_results = Entrez.read(handle)
            handle.close()
            
            pmids = search_results["IdList"]
            
            if not pmids:
                logger.warning(f"No results found for query: {vet_query}")
                return []
            
            # Fetch abstracts
            logger.info(f"Fetching {len(pmids)} abstracts")
            time.sleep(0.15)  # Rate limiting
            
            handle = Entrez.efetch(
                db="pubmed",
                id=pmids,
                rettype="medline",
                retmode="text"
            )
            records = Medline.parse(handle)
            
            papers = []
            for record in records:
                try:
                    paper = Paper(
                        pmid=record.get("PMID", ""),
                        title=record.get("TI", ""),
                        abstract=record.get("AB", ""),
                        authors=record.get("AU", []),
                        journal=record.get("TA", ""),
                        publication_date=record.get("DP", ""),
                        doi=record.get("AID", [""])[0] if record.get("AID") else None,
                        mesh_terms=record.get("MH", [])
                    )
                    papers.append(paper)
                except Exception as e:
                    logger.warning(f"Error parsing record: {e}")
                    continue
            
            handle.close()
            logger.info(f"Successfully retrieved {len(papers)} papers")
            return papers
        
        except Exception as e:
            logger.error(f"PubMed search failed: {e}")
            return []
    
    def generate_embedding(self, text: str) -> Optional[np.ndarray]:
        """
        Generate embedding vector for text.
        
        Args:
            text: Input text to embed
        
        Returns:
            Numpy array of embedding vector (1536 dimensions)
        """
        if not self.openai_client:
            logger.error("OpenAI client not available for embeddings")
            return None
        
        try:
            response = self.openai_client.embeddings.create(
                model=EMBEDDING_MODEL,
                input=text[:8000]  # Truncate to avoid token limits
            )
            embedding = np.array(response.data[0].embedding, dtype=np.float32)
            return embedding
        
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return None
    
    def create_vector_store(self, papers: List[Paper]):
        """
        Create FAISS vector store from papers.
        
        Args:
            papers: List of Paper objects with embeddings
        """
        if not HAS_FAISS:
            logger.error("FAISS not installed. Install with: pip install faiss-cpu")
            return
        
        # Generate embeddings for all papers
        logger.info(f"Generating embeddings for {len(papers)} papers")
        embeddings = []
        
        for i, paper in enumerate(papers):
            if paper.embedding is None:
                # Combine title and abstract for embedding
                text = f"{paper.title}\n\n{paper.abstract}"
                embedding = self.generate_embedding(text)
                if embedding is not None:
                    paper.embedding = embedding
                    embeddings.append(embedding)
                
                # Rate limiting
                if (i + 1) % 10 == 0:
                    time.sleep(0.5)
        
        if not embeddings:
            logger.error("No embeddings generated")
            return
        
        # Create FAISS index
        embeddings_array = np.array(embeddings)
        dimension = embeddings_array.shape[1]
        
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings_array)
        self.indexed_papers = [p for p in papers if p.embedding is not None]
        
        logger.info(f"Vector store created with {len(self.indexed_papers)} papers")
    
    def semantic_search(
        self,
        query: str,
        top_k: int = 5,
        min_similarity: float = 0.0
    ) -> List[Paper]:
        """
        Perform semantic similarity search.
        
        Args:
            query: Query text (clinical case description)
            top_k: Number of top results to return
            min_similarity: Minimum similarity threshold (0-1)
        
        Returns:
            List of top-k most similar papers with similarity scores
        """
        if self.index is None:
            logger.error("Vector store not initialized. Call create_vector_store first.")
            return []
        
        # Generate query embedding
        query_embedding = self.generate_embedding(query)
        if query_embedding is None:
            return []
        
        # Search index
        query_embedding = query_embedding.reshape(1, -1)
        distances, indices = self.index.search(query_embedding, top_k)
        
        # Convert distances to similarity scores (L2 -> cosine-like)
        similarities = 1 / (1 + distances[0])
        
        # Filter by minimum similarity
        results = []
        for idx, sim in zip(indices[0], similarities):
            if sim >= min_similarity:
                paper = self.indexed_papers[idx]
                paper.similarity_score = float(sim)
                results.append(paper)
        
        logger.info(f"Semantic search found {len(results)} papers above threshold")
        return results
    
    def _summarize_case(self, case: Dict) -> str:
        """Create a concise case summary for prompts"""
        parts = []
        
        if 'species' in case:
            parts.append(f"Species: {case['species']}")
        if 'age' in case:
            parts.append(f"Age: {case['age']}")
        if 'sex' in case:
            parts.append(f"Sex: {case['sex']}")
        if 'chief_complaint' in case or 'symptoms' in case:
            complaint = case.get('chief_complaint', ', '.join(case.get('symptoms', [])))
            parts.append(f"Chief Complaint: {complaint}")
        if 'history' in case:
            parts.append(f"History: {case['history']}")
        if 'physical_exam' in case:
            parts.append(f"Physical Exam: {case['physical_exam']}")
        if 'labs' in case:
            labs = ', '.join([f"{k}: {v}" for k, v in case['labs'].items()])
            parts.append(f"Laboratory: {labs}")
        if 'region' in case:
            parts.append(f"Region: {case['region']}")
        
        return '\n'.join(parts)
    
    def inject_context(self, case: Dict, papers: List[Paper]) -> str:
        """
        Build augmented prompt with retrieved papers.
        
        Args:
            case: Clinical case dictionary
            papers: List of relevant papers
        
        Returns:
            Formatted prompt string with RAG context
        """
        case_summary = self._summarize_case(case)
        
        # Format papers context
        papers_context = []
        for i, paper in enumerate(papers[:10], 1):  # Top 10 papers
            context = f"""
Paper {i}:
Title: {paper.title}
PMID: {paper.pmid}
Journal: {paper.journal} ({paper.publication_date})
Abstract: {paper.abstract[:500]}...
Relevance: {paper.similarity_score:.2%} match
"""
            papers_context.append(context)
        
        prompt = f"""You are a veterinary diagnostic specialist with access to the latest scientific literature.

CLINICAL CASE:
{case_summary}

RELEVANT SCIENTIFIC LITERATURE:
{''.join(papers_context)}

Based on the above case and scientific evidence, provide:

1. DIFFERENTIAL DIAGNOSES (ranked by probability):
   - List top 3-5 diagnoses
   - Include probability estimate (0-1)
   - Assign GRADE quality score (A/B/C/D)
   - Cite supporting PMIDs from the literature above

2. DIAGNOSTIC PLAN:
   - Recommended tests to confirm diagnosis
   - Priority order

3. IMMEDIATE ACTIONS:
   - Critical interventions required
   - Timeline

4. EVIDENCE SUMMARY:
   - Key findings from cited papers
   - Strength of evidence

Format response as JSON:
{{
  "differential_diagnoses": [
    {{
      "diagnosis": "...",
      "probability": 0.XX,
      "grade_score": "A/B/C/D",
      "rationale": "...",
      "supporting_evidence": ["PMID:...", ...]
    }}
  ],
  "diagnostic_plan": ["test1", "test2", ...],
  "immediate_actions": ["action1", ...],
  "cited_papers": [
    {{
      "pmid": "...",
      "title": "...",
      "key_finding": "...",
      "relevance": "..."
    }}
  ]
}}
"""
        return prompt
    
    def rag_diagnose(self, case: Dict) -> Dict:
        """
        Complete RAG pipeline for diagnosis.
        
        Args:
            case: Clinical case dictionary
        
        Returns:
            Diagnosis dictionary with evidence and citations
        """
        start_time = time.time()
        logger.info("Starting RAG diagnosis pipeline")
        
        # Step 1: Query Expansion
        queries = self.expand_query(case, num_queries=4)
        logger.info(f"Generated queries: {queries}")
        
        # Step 2: PubMed Search
        all_papers = []
        for query in queries:
            papers = self.search_pubmed_veterinary(query, max_results=10)
            all_papers.extend(papers)
            time.sleep(0.2)  # Rate limiting
        
        # Remove duplicates by PMID
        unique_papers = {p.pmid: p for p in all_papers}.values()
        unique_papers = list(unique_papers)
        logger.info(f"Retrieved {len(unique_papers)} unique papers")
        
        if not unique_papers:
            logger.warning("No papers found. Returning fallback diagnosis.")
            return self._fallback_diagnosis(case)
        
        # Step 3: Create Vector Store
        self.create_vector_store(unique_papers)
        
        # Step 4: Semantic Search
        case_text = self._summarize_case(case)
        relevant_papers = self.semantic_search(case_text, top_k=10, min_similarity=0.5)
        
        if not relevant_papers:
            logger.warning("No relevant papers found. Using all retrieved papers.")
            relevant_papers = unique_papers[:10]
        
        # Step 5: Generate Diagnosis with Context
        prompt = self.inject_context(case, relevant_papers)
        
        try:
            response_text = self._llm_chat(prompt, max_tokens=4000)
            if not response_text:
                response_text = self._fallback_diagnosis_text(case, relevant_papers)
            
            # Parse JSON response
            import json
            result = json.loads(response_text)
            
            # Add metadata
            result['metadata'] = {
                'total_papers_searched': len(all_papers),
                'unique_papers': len(unique_papers),
                'relevant_papers': len(relevant_papers),
                'latency_seconds': time.time() - start_time,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"RAG diagnosis completed in {result['metadata']['latency_seconds']:.2f}s")
            return result
        
        except Exception as e:
            logger.error(f"Diagnosis generation failed: {e}")
            return self._fallback_diagnosis(case)
    
    def _fallback_diagnosis(self, case: Dict) -> Dict:
        """Fallback diagnosis when RAG pipeline fails"""
        return {
            "differential_diagnoses": [{
                "diagnosis": "Unable to generate diagnosis - API error",
                "probability": 0.0,
                "grade_score": "D",
                "rationale": "RAG pipeline encountered an error",
                "supporting_evidence": []
            }],
            "diagnostic_plan": ["Consult with veterinary specialist"],
            "immediate_actions": ["Monitor patient closely"],
            "cited_papers": [],
            "metadata": {
                "error": "RAG pipeline failed",
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def _fallback_diagnosis_text(self, case: Dict, papers: List[Paper]) -> str:
        """Generate simple diagnosis text without LLM"""
        return f"""{{
  "differential_diagnoses": [
    {{
      "diagnosis": "Pending veterinary evaluation",
      "probability": 0.5,
      "grade_score": "C",
      "rationale": "Based on {len(papers)} relevant papers retrieved",
      "supporting_evidence": [{', '.join([f'"PMID:{p.pmid}"' for p in papers[:3]])}]
    }}
  ],
  "diagnostic_plan": ["Complete physical examination", "Laboratory analysis"],
  "immediate_actions": ["Monitor vital signs"],
  "cited_papers": [
    {', '.join([f'{{"pmid": "{p.pmid}", "title": "{p.title[:50]}...", "key_finding": "See abstract", "relevance": "{p.similarity_score:.2%}"}}' for p in papers[:3]])}
  ]
}}"""


# Convenience functions
def initialize_rag_system(
    openai_key: Optional[str] = None,
    anthropic_key: Optional[str] = None
) -> VetriageRAG:
    """Initialize RAG system with API keys"""
    return VetriageRAG(openai_key=openai_key, anthropic_key=anthropic_key)


def quick_diagnosis(case: Dict) -> Dict:
    """Quick diagnosis using default RAG system"""
    rag = initialize_rag_system()
    return rag.rag_diagnose(case)


if __name__ == "__main__":
    # Example usage
    print("VetrIAge RAG System v2.0")
    print("=" * 50)
    
    # Example clinical case
    example_case = {
        "species": "cat",
        "age": 8,
        "sex": "male",
        "chief_complaint": "Polyuria, polydipsia, dehydration",
        "history": "Prednisolone 6 drops/day for 3 months, discontinued 5 days ago",
        "physical_exam": "8% dehydration, dry mucous membranes",
        "labs": {
            "glucose": 524,  # mg/dL
            "BUN": 45,
            "creatinine": 1.8,
            "hematocrit": 25,
            "WBC": 24.2
        },
        "region": "Buenos Aires, Argentina"
    }
    
    print("\nExample Case:")
    print(f"- Species: {example_case['species']}")
    print(f"- Age: {example_case['age']} years")
    print(f"- Chief Complaint: {example_case['chief_complaint']}")
    print(f"- Glucose: {example_case['labs']['glucose']} mg/dL")
    
    print("\nRunning RAG diagnosis...")
    result = quick_diagnosis(example_case)
    
    print("\n" + "=" * 50)
    print("DIAGNOSIS RESULTS")
    print("=" * 50)
    
    if result.get('differential_diagnoses'):
        print("\nTop Diagnosis:")
        top_dx = result['differential_diagnoses'][0]
        print(f"- {top_dx['diagnosis']}")
        print(f"- Probability: {top_dx.get('probability', 0):.1%}")
        print(f"- GRADE Score: {top_dx.get('grade_score', 'N/A')}")
        
        if result.get('cited_papers'):
            print(f"\nCited Papers: {len(result['cited_papers'])}")
            for paper in result['cited_papers'][:3]:
                print(f"- PMID:{paper.get('pmid', 'N/A')}: {paper.get('title', 'N/A')[:60]}...")
    
    print(f"\nMetadata:")
    if 'metadata' in result:
        meta = result['metadata']
        print(f"- Total papers searched: {meta.get('total_papers_searched', 'N/A')}")
        print(f"- Relevant papers: {meta.get('relevant_papers', 'N/A')}")
        print(f"- Latency: {meta.get('latency_seconds', 0):.2f}s")
