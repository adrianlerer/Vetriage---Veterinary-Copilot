# 🐾 VetrIAge - Veterinary Copilot

> Evidence-Based Veterinary Diagnostics powered by Retrieval-Augmented Generation (RAG)

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-Embeddings-412991.svg)](https://openai.com)
[![Anthropic](https://img.shields.io/badge/Anthropic-Claude%203.5-8A2BE2.svg)](https://anthropic.com)

---

## 🎯 What is VetrIAge?

VetrIAge is an **AI-powered veterinary diagnostic copilot** that combines:

- **PubMed Integration**: Access to 35M+ biomedical research papers
- **Semantic Search**: OpenAI embeddings (text-embedding-3-small, 1536-dim) + FAISS vector store
- **Evidence Synthesis**: Claude 3.5 Sonnet with GRADE scoring methodology
- **Veterinary-Specific**: Optimized for animal species (dogs, cats, horses, exotic pets)
- **Citation Tracking**: Every diagnosis includes cited PMIDs and DOIs

### 🔬 How It Works

```
Clinical Case Input
    ↓
Query Expansion (LLM generates 3-5 PubMed queries)
    ↓
Literature Search (parallel PubMed retrieval)
    ↓
Embedding Generation (OpenAI API)
    ↓
Semantic Matching (FAISS cosine similarity)
    ↓
Context Injection (papers → augmented prompt)
    ↓
Diagnosis Generation (Claude 3.5 with citations)
    ↓
Structured Response (DDx + plans + PMIDs)
```

---

## ⚡ Quick Start

### Prerequisites

- Python 3.9+ (3.11+ recommended)
- API Keys:
  - [NCBI/PubMed](https://www.ncbi.nlm.nih.gov/account/) (free)
  - [OpenAI](https://platform.openai.com/api-keys)
  - [Anthropic](https://console.anthropic.com/)

### Installation

```bash
# Clone repository
git clone https://github.com/adrianlerer/Vetriage---Veterinary-Copilot.git
cd Vetriage---Veterinary-Copilot

# Navigate to RAG API
cd rag_api

# Install dependencies
pip install -r requirements.txt

# Configure API keys
cp .env.example .env
nano .env  # Add your API keys
```

### Run API Server

```bash
# Method 1: Using startup script (recommended)
./start-api.sh              # Default port 8000
./start-api.sh 9000         # Custom port 9000
PORT=8080 ./start-api.sh    # Via environment

# Method 2: Direct execution
PORT=9000 uvicorn fastapi_integration:app --reload

# Method 3: Python module
PORT=8080 python fastapi_integration.py
```

### Test the System

```bash
# Run comprehensive test suite
python test_rag_system.py

# Expected output:
# ✓ Initialization .............. PASS
# ✓ Query Expansion ............. PASS
# ✓ PubMed Search ............... PASS
# ✓ Embedding Generation ........ PASS
# ✓ Vector Store ................ PASS
# ✓ Semantic Search ............. PASS
# ✓ Full RAG Pipeline ........... PASS
# Total: 7/7 tests passed ✅
```

---

## 🚀 Usage Examples

### Python API

```python
from rag_api import quick_diagnosis

# Clinical case
case = {
    "species": "cat",
    "age": 8,
    "sex": "male",
    "chief_complaint": "Polyuria, polydipsia, weight loss",
    "history": "Prednisolone 6 drops/day for 3 months",
    "physical_exam": "8% dehydration, dry mucous membranes",
    "labs": {
        "glucose": 524,
        "BUN": 45,
        "creatinine": 1.8,
        "hematocrit": 25
    }
}

# Get diagnosis
result = quick_diagnosis(case)

# Access results
for dx in result['differential_diagnoses']:
    print(f"• {dx['diagnosis']} ({dx['probability']*100:.0f}%)")
    print(f"  GRADE: {dx['grade_score']}")
    print(f"  Rationale: {dx['rationale']}")

print(f"\nCited papers: {len(result['cited_papers'])}")
for paper in result['cited_papers']:
    print(f"  • PMID:{paper['pmid']} - {paper['title']}")
```

### REST API

```bash
# Start server
export PORT=9000
./start-api.sh $PORT

# Make diagnosis request
curl -X POST "http://localhost:${PORT}/api/v2/diagnose" \
  -H "Content-Type: application/json" \
  -d '{
    "species": "cat",
    "age": 8,
    "symptoms": ["polyuria", "polydipsia"],
    "labs": {"glucose": 524}
  }'

# Search PubMed
curl -X POST "http://localhost:${PORT}/api/v2/search-pubmed" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "feline diabetes mellitus",
    "max_results": 5,
    "filter_species": "feline"
  }'

# Health check
curl "http://localhost:${PORT}/api/v2/health"

# Interactive API documentation
open "http://localhost:${PORT}/docs"
```

### Integration Example

```javascript
// Frontend integration (React/Vue)
const API_BASE_URL = process.env.REACT_APP_API_URL || 
                     `http://localhost:${process.env.PORT || 8000}`;

async function diagnoseCase(caseData) {
  const response = await fetch(`${API_BASE_URL}/api/v2/diagnose`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(caseData)
  });
  
  const diagnosis = await response.json();
  
  // Display results
  console.log('Differential Diagnoses:', diagnosis.differential_diagnoses);
  console.log('Cited Papers:', diagnosis.cited_papers);
  console.log('Diagnostic Plan:', diagnosis.diagnostic_plan);
  
  return diagnosis;
}
```

---

## 📊 Performance Metrics

| Metric | Target | Current (Alpha) |
|--------|--------|-----------------|
| **Latency (end-to-end)** | 12-15s | 15-20s |
| PubMed search | 2-3s | 2-4s |
| Embedding generation | 1-2s | 1-3s |
| Vector search | <500ms | <500ms |
| LLM inference | 6-8s | 8-12s |
| **Cost per query** | **$0.12-0.15** | **$0.15-0.20** |

### Cost Breakdown

- **OpenAI Embeddings**: ~$0.005 per diagnosis (50 texts × 1k tokens × $0.0001/1k)
- **FAISS Vector Search**: $0.00 (local, no API cost)
- **Claude 3.5 Generation**: ~$0.10 per diagnosis (13k input + 2k output)
- **Total**: ~$0.11-0.15 per diagnosis

### Accuracy Targets

- **Diagnostic Precision**: 85-90% (relevant diagnoses in top 3)
- **Paper Relevance**: 80-85% (papers support diagnosis)
- **Citation Accuracy**: 95%+ (correct PMID/DOI links)
- **Improvement vs. No RAG**: +15-25% diagnostic accuracy

---

## 🔌 Flexible Port System

VetrIAge follows a **zero hardcoded ports** policy for maximum deployment flexibility.

### Port Configuration Priority

```
1. Command Line Argument    → ./start-api.sh 9000
2. PORT Environment Variable → PORT=8080 python fastapi_integration.py
3. .env File Configuration   → PORT=8000 in .env
4. Default Fallback          → 8000
```

### Benefits

- ✅ **No port conflicts** in multi-instance deployments
- ✅ **CI/CD friendly** with random port allocation
- ✅ **Docker/Kubernetes ready** with dynamic port mapping
- ✅ **Development flexibility** for parallel testing

For complete documentation, see: [docs/FLEXIBLE_PORT_STANDARD.md](docs/FLEXIBLE_PORT_STANDARD.md)

---

## 📁 Project Structure

```
Vetriage---Veterinary-Copilot/
├── README.md                      # This file
├── LICENSE                        # MIT License
├── .gitignore                     # Git ignore rules
│
├── rag_api/                       # Core RAG system
│   ├── __init__.py               # Module exports
│   ├── vetriage_rag.py           # RAG pipeline implementation
│   ├── fastapi_integration.py    # REST API endpoints
│   ├── test_rag_system.py        # Comprehensive test suite
│   ├── requirements.txt          # Python dependencies
│   ├── .env.example              # Environment template
│   ├── start-api.sh              # Automated startup script
│   └── README.md                 # API-specific documentation
│
├── tests/                         # Additional tests
│   └── (future: integration tests)
│
├── docs/                          # Documentation
│   ├── INSTALLATION.md
│   ├── API_REFERENCE.md
│   ├── PORT_CONFIGURATION.md
│   ├── FLEXIBLE_PORT_STANDARD.md
│   ├── IMPLEMENTATION_SUMMARY.md
│   └── DEPLOYMENT.md
│
├── examples/                      # Usage examples
│   └── (future: code examples)
│
├── scripts/                       # Utility scripts
│   └── (future: dev/deploy scripts)
│
└── skills/                        # AgentSkills.io integration
    └── vetriage-pubmed-rag/
        └── SKILL.md
```

---

## 🛠️ Development

### Running Tests

```bash
cd rag_api
python test_rag_system.py

# With pytest
pip install pytest pytest-cov
pytest test_rag_system.py -v --cov=. --cov-report=html
```

### Code Quality

```bash
# Format code
pip install black
black vetriage_rag.py fastapi_integration.py

# Type checking
pip install mypy
mypy vetriage_rag.py

# Linting
pip install pylint
pylint vetriage_rag.py
```

### Environment Setup

```bash
# Development environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r rag_api/requirements.txt
pip install -r requirements-dev.txt  # Future: dev dependencies
```

---

## 🚢 Deployment

### Docker

```dockerfile
# Dockerfile (future)
FROM python:3.11-slim

WORKDIR /app
COPY rag_api/ /app/
RUN pip install -r requirements.txt

ENV PORT=8000
EXPOSE ${PORT}

CMD ["python", "fastapi_integration.py"]
```

```bash
# Build and run
docker build -t vetriage-rag .
docker run -p 9000:9000 -e PORT=9000 --env-file .env vetriage-rag
```

### Docker Compose

```yaml
version: '3.8'

services:
  rag-api:
    build: .
    ports:
      - "${PORT:-8000}:${PORT:-8000}"
    environment:
      - PORT=${PORT:-8000}
      - HOST=0.0.0.0
    env_file:
      - .env
    restart: unless-stopped
```

### Cloud Platforms

- **AWS**: EC2, ECS, or Lambda with API Gateway
- **GCP**: Cloud Run or App Engine
- **Azure**: App Service or Container Instances
- **Railway/Render**: Direct Git deployment

---

## 📚 API Reference

### Endpoints

#### `POST /api/v2/diagnose`

Generate evidence-based diagnosis with citations.

**Request:**
```json
{
  "species": "cat",
  "age": 8,
  "sex": "male",
  "chief_complaint": "Polyuria, polydipsia",
  "symptoms": ["polyuria", "polydipsia", "weight loss"],
  "history": "Previous steroid treatment",
  "physical_exam": "Dehydration, dry mucous membranes",
  "labs": {
    "glucose": 524,
    "BUN": 45,
    "creatinine": 1.8
  },
  "region": "Buenos Aires, Argentina"
}
```

**Response:**
```json
{
  "differential_diagnoses": [
    {
      "diagnosis": "Diabetes Mellitus (Steroid-Induced)",
      "probability": 0.85,
      "grade_score": "High (⊕⊕⊕◯)",
      "rationale": "Hyperglycemia (524 mg/dL), polyuria/polydipsia...",
      "supporting_evidence": ["PMID:12345678", "PMID:87654321"]
    }
  ],
  "diagnostic_plan": [
    "Fructosamine test to assess glycemic control",
    "Urinalysis (glucosuria, ketonuria)",
    "Serum biochemistry panel"
  ],
  "immediate_actions": [
    "Discontinue or taper prednisolone",
    "Initiate insulin therapy if indicated"
  ],
  "cited_papers": [
    {
      "pmid": "12345678",
      "title": "Steroid-induced diabetes in cats...",
      "key_finding": "High correlation between...",
      "relevance": "Direct evidence for diagnosis"
    }
  ],
  "metadata": {
    "query_time_seconds": 14.2,
    "papers_retrieved": 25,
    "papers_cited": 8
  }
}
```

#### `POST /api/v2/search-pubmed`

Search PubMed for veterinary literature.

#### `POST /api/v2/expand-query`

Generate optimized PubMed search queries.

#### `GET /api/v2/health`

System health check.

For complete API documentation, start the server and visit: `http://localhost:8000/docs`

---

## 🔬 Technology Stack

- **Backend**: Python 3.11, FastAPI, Uvicorn
- **Vector Store**: FAISS (CPU) with cosine similarity
- **Embeddings**: OpenAI `text-embedding-3-small` (1536-dim)
- **LLM**: Anthropic Claude 3.5 Sonnet
- **Literature**: NCBI PubMed via Biopython Entrez
- **Testing**: pytest, unittest
- **Deployment**: Docker, Docker Compose

---

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'feat: add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Commit Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `test:` Test additions/changes
- `refactor:` Code refactoring

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🔗 Related Projects

- **claude-scientific-skills**: https://github.com/K-Dense-AI/claude-scientific-skills
- **AgentSkills.io**: https://agentskills.io/

---

## 📞 Support & Contact

- **Issues**: [GitHub Issues](https://github.com/adrianlerer/Vetriage---Veterinary-Copilot/issues)
- **Discussions**: [GitHub Discussions](https://github.com/adrianlerer/Vetriage---Veterinary-Copilot/discussions)
- **Documentation**: [docs/](docs/)

---

## 🎓 Citation

If you use VetrIAge in your research or clinical practice, please cite:

```bibtex
@software{vetriage2026,
  title = {VetrIAge: Evidence-Based Veterinary Diagnostics with RAG},
  author = {Lerer, Adrian and Contributors},
  year = {2026},
  url = {https://github.com/adrianlerer/Vetriage---Veterinary-Copilot}
}
```

---

## 🙏 Acknowledgments

- **NCBI/NLM** for PubMed API access
- **OpenAI** for embedding models
- **Anthropic** for Claude LLM
- **K-Dense-AI** for claude-scientific-skills foundation
- **FAISS** by Facebook Research

---

**Version**: 2.0.0  
**Status**: Alpha (Production-Ready for Testing)  
**Last Updated**: February 2026  
**Maintainer**: Adrian Lerer ([@adrianlerer](https://github.com/adrianlerer))

---

⭐ **Star this repository** if you find VetrIAge useful!

🐾 **Building better veterinary medicine through AI.**
