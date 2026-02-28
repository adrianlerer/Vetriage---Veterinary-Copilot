---
name: vetriage-pubmed-rag
description: Retrieval-Augmented Generation system for veterinary diagnostics. Searches PubMed for relevant veterinary literature, performs semantic search, and integrates evidence into diagnostic recommendations.
license: MIT
metadata:
    skill-author: VetrIAge Team
    skill-version: 2.0
    domain: veterinary-medicine
    capabilities: [rag, pubmed-search, embeddings, semantic-search, evidence-based-diagnostics]
---

# VetrIAge PubMed RAG Integration

## Overview

This skill provides a complete Retrieval-Augmented Generation (RAG) pipeline specifically designed for veterinary diagnostics. It combines PubMed literature search with semantic similarity matching to provide evidence-based diagnostic recommendations with cited scientific literature.

## When to Use This Skill

This skill should be used when:
- Analyzing clinical veterinary cases requiring evidence-based support
- Searching for relevant veterinary research papers from PubMed
- Generating differential diagnoses with scientific citations
- Providing veterinarians with traceable, peer-reviewed evidence
- Implementing RAG architecture for specialized veterinary knowledge
- Performing multi-step diagnostic workflows with literature validation

## Architecture

### RAG Pipeline Flow

```
Clinical Case Input
    ↓
Query Expansion (LLM generates optimal search queries)
    ↓
PubMed Search (3-5 targeted queries via Entrez API)
    ↓
Embedding Generation (OpenAI text-embedding-3-small)
    ↓
Vector Search (FAISS/pgvector similarity matching)
    ↓
Re-ranking (top 5-10 most relevant papers)
    ↓
Context Injection (papers + case → LLM prompt)
    ↓
Diagnostic Response (DDx with GRADE scoring + citations)
    ↓
Response + Top Papers + Metadata
```

## Core Components

### 1. PubMed Search Module

**Purpose**: Search veterinary literature using optimized queries
**API**: NCBI E-utilities (Entrez)
**Rate Limit**: 10 requests/second with API key

**Key Functions**:
- `search_pubmed_veterinary(query: str, max_results: int = 10)` - Search with veterinary filters
- `fetch_abstracts(pmids: List[str])` - Retrieve full abstracts
- `extract_veterinary_keywords(case: dict)` - Generate search terms from clinical case

**Example Usage**:
```python
from vetriage_rag import search_pubmed_veterinary

# Search for feline diabetes papers
papers = search_pubmed_veterinary(
    query="feline diabetes mellitus hyperglycemia treatment",
    max_results=10
)

# Returns: [{"pmid": "...", "title": "...", "abstract": "...", "doi": "..."}]
```

### 2. Embedding & Vector Search

**Purpose**: Semantic similarity matching for relevant paper retrieval
**Model**: OpenAI text-embedding-3-small (1536 dimensions)
**Storage**: FAISS (development) or pgvector (production)

**Key Functions**:
- `generate_embedding(text: str)` - Convert text to vector
- `create_vector_store(papers: List[dict])` - Index papers
- `semantic_search(query: str, top_k: int = 5)` - Find similar papers

**Example Usage**:
```python
from vetriage_rag import generate_embedding, semantic_search

# Generate embedding for clinical case
case_embedding = generate_embedding(
    "Cat, 8 years old, glucose 524 mg/dL, polyuria, polydipsia"
)

# Find similar papers
similar_papers = semantic_search(
    query=case_embedding,
    top_k=5
)
```

### 3. Query Expansion

**Purpose**: Generate optimal PubMed search queries from clinical cases
**Method**: LLM-assisted keyword extraction and Boolean query construction

**Key Functions**:
- `expand_query(case: dict, num_queries: int = 4)` - Generate multiple targeted queries
- `translate_to_english(text: str)` - Translate Spanish/Portuguese to English for PubMed

**Example Usage**:
```python
from vetriage_rag import expand_query

case = {
    "species": "cat",
    "age": 8,
    "symptoms": ["poliuria", "polidipsia", "deshidratación"],
    "labs": {"glucose": 524, "WBC": 24.2}
}

queries = expand_query(case, num_queries=4)
# Returns:
# [
#   "feline diabetes mellitus hyperglycemia ketoacidosis",
#   "cat steroid-induced diabetes prednisolone",
#   "feline diabetic ketoacidosis pancreatitis concurrent",
#   "feline diabetes emergency insulin protocol"
# ]
```

### 4. RAG Integration

**Purpose**: Combine retrieved papers with LLM for evidence-based diagnostics
**LLM**: Claude 3.5 Sonnet (or GPT-4) via OpenRouter

**Key Functions**:
- `rag_diagnose(case: dict, papers: List[dict])` - Full RAG pipeline
- `inject_context(case: dict, papers: List[dict])` - Build augmented prompt
- `format_response(diagnosis: dict, papers: List[dict])` - Structure output

**Example Usage**:
```python
from vetriage_rag import rag_diagnose

case = {
    "species": "cat",
    "age": 8,
    "chief_complaint": "Polyuria, polydipsia",
    "labs": {"glucose": 524}
}

result = rag_diagnose(case)

# Returns:
# {
#   "differential_diagnoses": [
#     {
#       "diagnosis": "Diabetic Ketoacidosis (DKA)",
#       "probability": 0.68,
#       "grade_score": "A",
#       "supporting_evidence": ["PMID:34567890", "PMID:23456789"]
#     }
#   ],
#   "cited_papers": [
#     {
#       "pmid": "34567890",
#       "title": "Feline Diabetic Ketoacidosis: 127 Cases",
#       "doi": "10.1111/jvim.15678",
#       "relevance_score": 0.92
#     }
#   ],
#   "diagnostic_plan": ["Blood gas analysis", "Insulin therapy"],
#   "immediate_actions": ["Hospitalization", "IV fluids"]
# }
```

## Dependencies

### Required Python Packages

```
biopython>=1.83          # PubMed API access
openai>=1.0.0           # Embeddings generation
faiss-cpu>=1.7.4        # Vector search (development)
pgvector>=0.2.0         # Vector search (production, PostgreSQL extension)
numpy>=1.24.0           # Numerical operations
langchain>=0.1.0        # RAG orchestration
anthropic>=0.21.0       # Claude LLM
requests>=2.31.0        # HTTP requests
python-dotenv>=1.0.0    # Environment variables
```

### Environment Variables

```bash
# Required
NCBI_API_KEY=your_pubmed_api_key_here
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_claude_key_here

# Optional
VECTOR_STORE_TYPE=faiss  # or pgvector
POSTGRES_CONNECTION_STRING=postgresql://... # if using pgvector
MAX_PAPERS_PER_QUERY=10
EMBEDDING_MODEL=text-embedding-3-small
LLM_MODEL=claude-3-5-sonnet-20241022
```

## Installation & Setup

### 1. Install Dependencies

```bash
# Using uv (recommended)
uv pip install biopython openai faiss-cpu langchain anthropic

# Or using pip
pip install -r requirements.txt
```

### 2. Get API Keys

**PubMed API Key** (free):
1. Go to https://www.ncbi.nlm.nih.gov/account/
2. Create an account
3. Request API key (instant approval)
4. Add to `.env`: `NCBI_API_KEY=your_key_here`

**OpenAI API Key**:
1. Go to https://platform.openai.com/api-keys
2. Create new secret key
3. Add to `.env`: `OPENAI_API_KEY=sk-...`

**Anthropic API Key**:
1. Go to https://console.anthropic.com/
2. Create API key
3. Add to `.env`: `ANTHROPIC_API_KEY=sk-ant-...`

### 3. Initialize Vector Store

```python
from vetriage_rag import initialize_vector_store

# Index existing veterinary cases (optional)
cases = load_previous_cases()  # Your existing case database
initialize_vector_store(cases)
```

## Usage Examples

### Example 1: Basic RAG Diagnosis

```python
from vetriage_rag import rag_diagnose

# Clinical case
case = {
    "species": "cat",
    "age": 8,
    "sex": "male",
    "chief_complaint": "Poliuria, polidipsia, deshidratación",
    "history": "Prednisolona 6 gotas/día × 3 meses",
    "physical_exam": "Deshidratación 8%, mucosas secas",
    "labs": {
        "glucose": 524,  # mg/dL
        "BUN": 45,
        "creatinine": 1.8,
        "hematocrit": 25,
        "WBC": 24.2
    },
    "region": "Buenos Aires, Argentina"
}

# Run RAG pipeline
result = rag_diagnose(case)

# Access results
print(f"Top Diagnosis: {result['differential_diagnoses'][0]['diagnosis']}")
print(f"Supporting Papers: {len(result['cited_papers'])}")

for paper in result['cited_papers'][:3]:
    print(f"- {paper['title']} (PMID:{paper['pmid']})")
```

### Example 2: Custom Search + Semantic Matching

```python
from vetriage_rag import search_pubmed_veterinary, semantic_search

# Step 1: Search PubMed
papers = search_pubmed_veterinary(
    query="canine ehrlichiosis diagnosis PCR treatment doxycycline",
    max_results=20
)

# Step 2: Semantic filtering
case_text = "Dog with thrombocytopenia, anemia, fever, from Misiones Argentina"
relevant_papers = semantic_search(
    query=case_text,
    papers=papers,
    top_k=5
)

print(f"Found {len(relevant_papers)} highly relevant papers")
```

### Example 3: Batch Processing Multiple Cases

```python
from vetriage_rag import rag_diagnose_batch

cases = [
    {"species": "dog", "symptoms": ["vomiting", "diarrhea"], ...},
    {"species": "cat", "symptoms": ["polyuria", "polydipsia"], ...},
    {"species": "horse", "symptoms": ["colic", "sweating"], ...}
]

# Process all cases with caching
results = rag_diagnose_batch(cases, use_cache=True)

for case, result in zip(cases, results):
    print(f"{case['species']}: {result['differential_diagnoses'][0]['diagnosis']}")
```

## Performance Metrics

### Expected Performance (Target Goals)

- **Latency**: 12-15 seconds per diagnosis (5s PubMed + 2s embeddings + 1s search + 6s LLM)
- **Cost per Query**: $0.12-0.15 (embeddings $0.005 + search $0.01 + LLM $0.10)
- **Precision**: 85-90% (papers relevant to diagnosis)
- **Recall**: 80-85% (captures key literature)
- **Diagnostic Accuracy**: >85% (with RAG) vs ~70% (without RAG)

### Optimization Tips

1. **Cache Embeddings**: Store embeddings for common cases/papers
2. **Batch Requests**: Process multiple PubMed queries in parallel
3. **Use Prompt Caching**: Claude 3.5 prompt caching reduces cost 40%
4. **Filter by Date**: Limit searches to recent papers (last 5 years)
5. **Preload Common Papers**: Index frequently cited veterinary papers

## Troubleshooting

### Issue: PubMed Rate Limit Exceeded

**Solution**: 
```python
import time

# Add delay between requests
time.sleep(0.15)  # ~6 requests/second (safe margin)

# Or use exponential backoff
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def search_with_retry(query):
    return search_pubmed_veterinary(query)
```

### Issue: Papers Not Relevant to Veterinary Medicine

**Solution**:
```python
# Add veterinary-specific filters to query
query = f"({base_query}) AND (veterinary[tiab] OR canine OR feline OR equine)"

# Or filter by journals
VETERINARY_JOURNALS = [
    "J Vet Intern Med",
    "J Am Vet Med Assoc",
    "Vet J",
    "J Feline Med Surg"
]
query += f" AND ({' OR '.join([f'{j}[ta]' for j in VETERINARY_JOURNALS])})"
```

### Issue: Vector Search Returns Irrelevant Results

**Solution**:
```python
# Increase similarity threshold
relevant_papers = semantic_search(
    query=case_embedding,
    top_k=10,
    min_similarity=0.75  # Only papers >75% similar
)

# Or use hybrid search (keyword + semantic)
from vetriage_rag import hybrid_search

papers = hybrid_search(
    query=case_text,
    keyword_weight=0.3,
    semantic_weight=0.7
)
```

## Advanced Features

### 1. Regional Epidemiology Integration

Combine PubMed papers with regional disease prevalence data.

```python
from vetriage_rag import rag_diagnose_with_epidemiology

result = rag_diagnose_with_epidemiology(
    case=case,
    region="Misiones, Argentina"
)

# Adds regional prevalence to diagnosis
# e.g., "Ehrlichiosis (25-35% prevalence in Misiones)"
```

### 2. Multi-Language Support

Automatically translate queries and results.

```python
from vetriage_rag import rag_diagnose

# Spanish input
case = {
    "especie": "gato",
    "síntomas": ["poliuria", "polidipsia"],
    ...
}

result = rag_diagnose(case, input_language="es", output_language="es")
# Searches PubMed in English, returns diagnosis in Spanish
```

### 3. Custom Re-ranking

Implement domain-specific paper re-ranking.

```python
from vetriage_rag import custom_rerank

def veterinary_reranker(papers, case):
    """Prioritize papers by species match, recency, journal impact"""
    scored = []
    for paper in papers:
        score = paper['similarity_score']
        
        # Boost species match
        if case['species'] in paper['abstract'].lower():
            score *= 1.3
        
        # Boost recent papers
        year = int(paper['publication_date'][:4])
        if year >= 2020:
            score *= 1.2
        
        # Boost high-impact journals
        if paper['journal'] in TIER_1_VET_JOURNALS:
            score *= 1.1
        
        scored.append((paper, score))
    
    return sorted(scored, key=lambda x: x[1], reverse=True)

# Use custom ranker
result = rag_diagnose(case, reranker=veterinary_reranker)
```

## References

- **PubMed E-utilities**: https://www.ncbi.nlm.nih.gov/books/NBK25501/
- **OpenAI Embeddings**: https://platform.openai.com/docs/guides/embeddings
- **FAISS Vector Search**: https://github.com/facebookresearch/faiss
- **LangChain RAG**: https://python.langchain.com/docs/use_cases/question_answering/
- **Claude API**: https://docs.anthropic.com/claude/reference/getting-started-with-the-api

## Related Skills

- `pubmed-database` - Direct PubMed REST API access
- `biopython` - Comprehensive bioinformatics toolkit (includes Entrez)
- `clinical-decision-support` - Clinical decision-making frameworks
- `scientific-visualization` - Visualize diagnostic workflows and evidence networks

## Citation

If you use this skill in research or clinical practice, please cite:

```
VetrIAge PubMed RAG Integration (2026)
VetrIAge Team
Available at: https://github.com/[your-repo]/vetriage-rag
```

---

**Version**: 2.0 (February 2026)
**Maintainer**: VetrIAge Development Team
**License**: MIT
**Status**: Production-ready for alpha testing
