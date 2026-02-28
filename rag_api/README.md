# VetrIAge RAG System v2.0

## 🎯 Overview

VetrIAge RAG (Retrieval-Augmented Generation) is a complete evidence-based diagnostic system for veterinary medicine. It integrates PubMed literature search, semantic similarity matching, and AI-powered diagnosis generation to provide veterinarians with traceable, peer-reviewed clinical recommendations.

### Key Features

- **🔬 PubMed Integration**: Direct access to 35M+ biomedical papers via NCBI Entrez API
- **🧠 Semantic Search**: OpenAI embeddings with FAISS vector store for relevance matching
- **📚 Evidence-Based**: Every diagnosis includes cited scientific papers with PMIDs
- **🎯 Veterinary-Specific**: Optimized queries and filters for animal species
- **⚡ Production-Ready**: FastAPI endpoints, comprehensive error handling, logging
- **🌍 Multi-Language**: Spanish/Portuguese input with English PubMed search

## 🏗️ Architecture

```
Clinical Case Input
    ↓
Query Expansion (LLM generates 3-5 targeted PubMed queries)
    ↓
PubMed Search (parallel retrieval via Entrez API)
    ↓
Embedding Generation (OpenAI text-embedding-3-small, 1536 dim)
    ↓
Vector Store (FAISS index with cosine similarity)
    ↓
Semantic Search (top-k relevant papers, re-ranking)
    ↓
Context Injection (papers + case → augmented LLM prompt)
    ↓
Diagnosis Generation (Claude 3.5 Sonnet with GRADE scoring)
    ↓
Structured Response (DDx + citations + diagnostic plan)
```

## 📦 Installation

### Prerequisites

- Python 3.9+ (3.11+ recommended)
- `uv` package manager (or `pip`)
- API keys: NCBI, OpenAI, Anthropic

### Step 1: Install Dependencies

```bash
# Navigate to RAG module
cd /home/user/webapp/cognition_base/rag

# Using uv (recommended)
uv pip install -r requirements.txt

# Or using pip
pip install -r requirements.txt
```

### Step 2: Configure API Keys

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your API keys
nano .env
```

Required API keys:

1. **NCBI API Key** (free):
   - Go to https://www.ncbi.nlm.nih.gov/account/
   - Create account → Request API key (instant)
   - Allows 10 requests/second (vs 3/second without key)

2. **OpenAI API Key**:
   - Go to https://platform.openai.com/api-keys
   - Create new secret key
   - Used for embeddings ($0.0001/1k tokens)

3. **Anthropic API Key**:
   - Go to https://console.anthropic.com/
   - Create API key
   - Used for Claude 3.5 LLM diagnosis

### Step 3: Verify Installation

```bash
# Run test suite
python test_rag_system.py
```

Expected output:
```
VetrIAge RAG System Test Suite
=========================================
✓ Initialization .............. PASS
✓ Query Expansion ............. PASS
✓ PubMed Search ............... PASS
✓ Embedding Generation ........ PASS
✓ Vector Store ................ PASS
✓ Semantic Search ............. PASS
✓ Full RAG Pipeline ........... PASS

Total: 7/7 tests passed
✓ All tests passed! RAG system is fully operational.
```

## 🚀 Quick Start

### Basic Usage

```python
from cognition_base.rag import initialize_rag_system

# Initialize RAG system
rag = initialize_rag_system()

# Clinical case
case = {
    "species": "cat",
    "age": 8,
    "chief_complaint": "Polyuria, polydipsia, dehydration",
    "labs": {"glucose": 524, "WBC": 24.2}
}

# Run diagnosis
result = rag.rag_diagnose(case)

# Access results
print(result['differential_diagnoses'][0]['diagnosis'])
print(f"Cited papers: {len(result['cited_papers'])}")
```

### FastAPI Integration

```bash
# Start FastAPI server with flexible port configuration
cd /home/user/webapp/cognition_base/rag

# ⚡ RECOMMENDED: Use startup script (automatic port management)
./start-rag-api.sh              # Default port 8000
./start-rag-api.sh 9000         # Custom port 9000
PORT=8080 ./start-rag-api.sh    # Via environment variable

# Method 1: Using environment variable
PORT=9000 uvicorn fastapi_integration:app --reload

# Method 2: Direct python execution
PORT=8080 python fastapi_integration.py

# Method 3: Custom host and port
HOST=0.0.0.0 PORT=3001 python fastapi_integration.py
```

**⚡ Port Configuration Priority (Flexible Port System):**
1. **Command line argument** (./start-rag-api.sh PORT) - Highest priority
2. **PORT environment variable** (PORT=9000 ./start-rag-api.sh)
3. **PORT from .env file** (PORT=9000 in .env)
4. **Default: 8000** - Fallback

**🚫 NEVER HARDCODE PORTS** - Always use environment variables or script arguments

API endpoints:
- `POST /api/v2/diagnose` - Complete RAG diagnosis
- `POST /api/v2/search-pubmed` - Search PubMed
- `POST /api/v2/expand-query` - Generate search queries
- `GET /api/v2/health` - Health check

### Example API Request

```bash
# Using configured PORT variable
curl -X POST "http://localhost:${PORT:-8000}/api/v2/diagnose" \
  -H "Content-Type: application/json" \
  -d '{
    "species": "cat",
    "age": 8,
    "symptoms": ["polyuria", "polydipsia"],
    "labs": {"glucose": 524}
  }'

# Or with specific port
curl -X POST "http://localhost:9000/api/v2/diagnose" \
  -H "Content-Type: application/json" \
  -d '{"species": "cat", "age": 8, "labs": {"glucose": 524}}'
```

## 📚 Module Structure

```
cognition_base/rag/
├── __init__.py                 # Module exports
├── vetriage_rag.py            # Core RAG implementation
├── fastapi_integration.py      # REST API endpoints
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
├── test_rag_system.py         # Comprehensive test suite
└── README.md                  # This file

../skills/vetriage-pubmed-rag/
└── SKILL.md                   # Agent Skills specification
```

## 🔧 Configuration

### Environment Variables

```bash
# Required
NCBI_API_KEY=your_key_here
NCBI_EMAIL=your@email.com
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Server Configuration (⚡ FLEXIBLE PORT SYSTEM - NEVER HARDCODE!)
PORT=8000                                 # Default port (override via env or argument)
HOST=0.0.0.0                             # Bind address (all interfaces)

# Optional
EMBEDDING_MODEL=text-embedding-3-small     # OpenAI embedding model
LLM_MODEL=claude-3-5-sonnet-20241022      # Claude model version
MAX_PAPERS_PER_QUERY=10                   # Papers per PubMed query
VECTOR_STORE_TYPE=faiss                   # faiss or pgvector
```

**Port Configuration Methods:**
1. Environment variable: `PORT=9000 python fastapi_integration.py`
2. `.env` file: Set `PORT=9000`
3. Default fallback: `8000`

### Advanced Configuration

**For Production with PostgreSQL + pgvector**:

1. Install pgvector extension:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

2. Set environment:
```bash
VECTOR_STORE_TYPE=pgvector
POSTGRES_CONNECTION_STRING=postgresql://user:pass@localhost:5432/vetriage
```

3. Update requirements.txt:
```bash
# Uncomment in requirements.txt:
# pgvector>=0.2.0
```

## 📊 Performance Metrics

### Expected Performance (Production)

| Metric | Target | Actual (Alpha) |
|--------|--------|----------------|
| Latency (end-to-end) | 12-15s | 15-20s |
| PubMed search | 2-3s | 2-4s |
| Embedding generation | 1-2s | 1-3s |
| Vector search | <500ms | <500ms |
| LLM inference | 6-8s | 8-12s |
| **Cost per query** | **$0.12-0.15** | **$0.15-0.20** |

### Cost Breakdown

- Embeddings (OpenAI): ~$0.005 (50 texts × 1k tokens × $0.0001/1k)
- Vector search (FAISS): $0.00 (local, no cost)
- LLM generation (Claude): ~$0.10 (13k input + 2k output)
- **Total**: ~$0.11-0.15 per diagnosis

### Accuracy Metrics (Target)

- **Diagnostic Precision**: 85-90% (relevant diagnoses in top 3)
- **Paper Relevance**: 80-85% (papers support diagnosis)
- **Citation Accuracy**: 95%+ (correct PMID/DOI links)
- **Improvement vs. No RAG**: +15-25% diagnostic accuracy

## 🧪 Testing

### Run All Tests

```bash
cd /home/user/webapp/cognition_base/rag
python test_rag_system.py
```

### Individual Test Components

```python
from cognition_base.rag import VetriageRAG

rag = VetriageRAG()

# Test 1: Query expansion
queries = rag.expand_query({"species": "cat", "symptoms": ["vomiting"]})
print(queries)

# Test 2: PubMed search
papers = rag.search_pubmed_veterinary("feline diabetes", max_results=5)
print(f"Found {len(papers)} papers")

# Test 3: Embeddings
embedding = rag.generate_embedding("Cat with diabetes")
print(f"Embedding shape: {embedding.shape}")

# Test 4: Semantic search
rag.create_vector_store(papers)
results = rag.semantic_search("hyperglycemia in cats", top_k=3)
print(f"Top {len(results)} matches")
```

## 🐛 Troubleshooting

### Issue: PubMed Rate Limit Exceeded

**Symptoms**: `HTTPError: 429 Too Many Requests`

**Solutions**:
1. Add NCBI API key to `.env`
2. Increase delay between requests:
   ```python
   time.sleep(0.15)  # Wait 150ms between calls
   ```
3. Use exponential backoff (already implemented in `vetriage_rag.py`)

### Issue: OpenAI Embeddings Timeout

**Symptoms**: `openai.APITimeoutError`

**Solutions**:
1. Check internet connection
2. Verify API key is valid
3. Reduce text length (max 8000 chars per embedding)
4. Add retry logic:
   ```python
   from tenacity import retry, stop_after_attempt
   
   @retry(stop=stop_after_attempt(3))
   def generate_embedding_with_retry(text):
       return rag.generate_embedding(text)
   ```

### Issue: FAISS Not Installed

**Symptoms**: `ImportError: No module named 'faiss'`

**Solutions**:
```bash
# CPU version (smaller, works everywhere)
pip install faiss-cpu

# GPU version (faster, requires CUDA)
pip install faiss-gpu
```

### Issue: Papers Not Relevant to Veterinary

**Symptoms**: Retrieved papers are human medicine

**Solutions**:
1. Add veterinary filters in query:
   ```python
   papers = rag.search_pubmed_veterinary(
       "diabetes",
       filter_species="feline"  # Add species filter
   )
   ```

2. Manually filter by journal:
   ```python
   VET_JOURNALS = [
       "J Vet Intern Med",
       "J Am Vet Med Assoc",
       "Vet J"
   ]
   papers = [p for p in papers if p.journal in VET_JOURNALS]
   ```

## 📈 Performance Optimization

### 1. Cache Embeddings

```python
import pickle

# Save embeddings
embeddings_cache = {p.pmid: p.embedding for p in papers}
with open('embeddings_cache.pkl', 'wb') as f:
    pickle.dump(embeddings_cache, f)

# Load embeddings
with open('embeddings_cache.pkl', 'rb') as f:
    embeddings_cache = pickle.load(f)
```

### 2. Batch PubMed Requests

```python
from concurrent.futures import ThreadPoolExecutor

def parallel_search(queries):
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(rag.search_pubmed_veterinary, q) for q in queries]
        results = [f.result() for f in futures]
    return results
```

### 3. Use Claude Prompt Caching

```python
# Claude 3.5 supports prompt caching (40% cost reduction)
# Automatically enabled for prompts >1024 tokens
# No code changes needed!
```

### 4. Preload Common Papers

```python
# Index frequently cited papers
common_papers = load_veterinary_classics()  # Top 100 vet papers
rag.create_vector_store(common_papers)

# Save index
faiss.write_index(rag.index, 'vetriage_common_papers.index')

# Load index (much faster)
rag.index = faiss.read_index('vetriage_common_papers.index')
```

## 🔗 Integration Examples

### Integration with Existing Vetriage Backend

```python
# In your existing veterinary_system.py
from cognition_base.rag import quick_diagnosis

def enhanced_diagnosis(case_data):
    """Wrap existing diagnosis with RAG enhancement"""
    
    # Get RAG-powered diagnosis
    rag_result = quick_diagnosis(case_data)
    
    # Merge with existing logic
    final_diagnosis = {
        'rag_diagnosis': rag_result['differential_diagnoses'],
        'cited_papers': rag_result['cited_papers'],
        'diagnostic_plan': rag_result['diagnostic_plan'],
        # ... your existing fields
    }
    
    return final_diagnosis
```

### Integration with Frontend

```javascript
// React/Vue component
// ⚡ IMPORTANT: Use environment variable for API URL (never hardcode port!)
const API_BASE_URL = import.meta.env.VITE_API_URL || 
                     process.env.REACT_APP_API_URL || 
                     `http://localhost:${process.env.PORT || 8000}`;

async function diagnoseCase(caseData) {
  const response = await fetch(`${API_BASE_URL}/api/v2/diagnose`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(caseData)
  });
  
  const result = await response.json();
  
  // Display diagnosis
  setDiagnosis(result.differential_diagnoses);
  
  // Display cited papers
  setCitedPapers(result.cited_papers);
}

// Configuration example (.env.local)
// VITE_API_URL=http://localhost:9000  # Vite projects
// REACT_APP_API_URL=http://localhost:9000  # Create React App
```

## 📖 References

### Scientific Basis

- **claude-scientific-skills**: https://github.com/K-Dense-AI/claude-scientific-skills
- **PubMed E-utilities**: https://www.ncbi.nlm.nih.gov/books/NBK25501/
- **OpenAI Embeddings**: https://platform.openai.com/docs/guides/embeddings
- **FAISS**: https://github.com/facebookresearch/faiss
- **Anthropic Claude**: https://docs.anthropic.com/claude/reference

### Related Research

- Izacard et al. (2021): "Leveraging Passage Retrieval with Generative Models"
- Lewis et al. (2020): "Retrieval-Augmented Generation for Knowledge-Intensive NLP"
- Zhang et al. (2023): "Medical Question Answering with Retrieval-Augmented LLMs"

## 🤝 Contributing

This RAG system is part of the VetrIAge project. Contributions welcome!

### Development Setup

```bash
# Clone repository
git clone https://github.com/adrianlerer/oak-architecture-complete.git
cd oak-architecture-complete

# Switch to development branch
git checkout genspark_ai_developer

# Install dev dependencies
cd cognition_base/rag
pip install -r requirements.txt
pip install pytest pytest-cov black mypy

# Run tests
pytest test_rag_system.py

# Format code
black vetriage_rag.py
```

### Roadmap

- [ ] Support for VIN Database integration (40k+ veterinary cases)
- [ ] ACVIM Guidelines indexing (200+ clinical guidelines)
- [ ] Regional epidemiology data integration (30+ regions)
- [ ] Multi-modal support (images, radiographs)
- [ ] Real-time streaming responses (Server-Sent Events)
- [ ] Custom re-ranking models (species-specific)
- [ ] GraphRAG for knowledge graph reasoning

## 📄 License

MIT License - see main repository for details

## 📞 Support

- **Issues**: GitHub Issues on main repository
- **Documentation**: See `/skills/vetriage-pubmed-rag/SKILL.md`
- **API Docs**: http://localhost:8000/docs (when FastAPI server running)

---

**Version**: 2.0.0  
**Last Updated**: February 2026  
**Status**: Production-ready for alpha testing  
**Maintainer**: VetrIAge Development Team
