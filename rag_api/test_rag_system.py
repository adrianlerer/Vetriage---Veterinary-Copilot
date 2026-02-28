#!/usr/bin/env python3
"""
Test script for VetrIAge RAG System
===================================

Tests the complete RAG pipeline with example veterinary cases.
"""

import sys
import os
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from cognition_base.rag import VetriageRAG, initialize_rag_system

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text):
    """Print colored header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(70)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}\n")


def print_section(text):
    """Print colored section"""
    print(f"\n{Colors.OKBLUE}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.OKBLUE}{'-' * len(text)}{Colors.ENDC}")


def print_success(text):
    """Print success message"""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_error(text):
    """Print error message"""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def print_warning(text):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")


def test_initialization():
    """Test 1: System Initialization"""
    print_section("Test 1: System Initialization")
    
    try:
        rag = initialize_rag_system()
        
        # Check API clients
        if rag.openai_client:
            print_success("OpenAI client initialized")
        else:
            print_warning("OpenAI client not available (check OPENAI_API_KEY)")
        
        if rag.anthropic_client:
            print_success("Anthropic client initialized")
        else:
            print_warning("Anthropic client not available (check ANTHROPIC_API_KEY)")
        
        # Check NCBI config
        if os.getenv("NCBI_API_KEY"):
            print_success("NCBI API key configured")
        else:
            print_warning("NCBI API key not configured (rate limits will apply)")
        
        return rag
    
    except Exception as e:
        print_error(f"Initialization failed: {e}")
        return None


def test_query_expansion(rag):
    """Test 2: Query Expansion"""
    print_section("Test 2: Query Expansion")
    
    case = {
        "species": "cat",
        "age": 8,
        "symptoms": ["polyuria", "polydipsia", "dehydration"],
        "labs": {"glucose": 524, "WBC": 24.2}
    }
    
    try:
        queries = rag.expand_query(case, num_queries=4)
        print_success(f"Generated {len(queries)} search queries:")
        for i, query in enumerate(queries, 1):
            print(f"  {i}. {query}")
        return True
    
    except Exception as e:
        print_error(f"Query expansion failed: {e}")
        return False


def test_pubmed_search(rag):
    """Test 3: PubMed Search"""
    print_section("Test 3: PubMed Search")
    
    query = "feline diabetes mellitus hyperglycemia ketoacidosis"
    
    try:
        papers = rag.search_pubmed_veterinary(query, max_results=5)
        print_success(f"Retrieved {len(papers)} papers from PubMed")
        
        if papers:
            print("\nSample papers:")
            for i, paper in enumerate(papers[:3], 1):
                print(f"\n  {i}. {paper.title}")
                print(f"     PMID: {paper.pmid}")
                print(f"     Journal: {paper.journal} ({paper.publication_date})")
                print(f"     Abstract: {paper.abstract[:150]}...")
        
        return papers
    
    except Exception as e:
        print_error(f"PubMed search failed: {e}")
        return []


def test_embeddings(rag, papers):
    """Test 4: Embedding Generation"""
    print_section("Test 4: Embedding Generation")
    
    if not papers:
        print_warning("No papers available for embedding test")
        return False
    
    try:
        text = f"{papers[0].title}\n\n{papers[0].abstract}"
        embedding = rag.generate_embedding(text)
        
        if embedding is not None:
            print_success(f"Generated embedding vector: shape={embedding.shape}")
            print(f"  Dimension: {len(embedding)}")
            print(f"  Sample values: {embedding[:5]}")
            return True
        else:
            print_error("Embedding generation returned None")
            return False
    
    except Exception as e:
        print_error(f"Embedding generation failed: {e}")
        return False


def test_vector_store(rag, papers):
    """Test 5: Vector Store Creation"""
    print_section("Test 5: Vector Store Creation")
    
    if not papers:
        print_warning("No papers available for vector store test")
        return False
    
    try:
        rag.create_vector_store(papers)
        
        if rag.index is not None:
            print_success(f"Vector store created successfully")
            print(f"  Indexed papers: {len(rag.indexed_papers)}")
            return True
        else:
            print_error("Vector store creation failed")
            return False
    
    except Exception as e:
        print_error(f"Vector store creation failed: {e}")
        return False


def test_semantic_search(rag):
    """Test 6: Semantic Search"""
    print_section("Test 6: Semantic Search")
    
    if rag.index is None:
        print_warning("Vector store not initialized")
        return False
    
    query = "Cat with high blood glucose, drinking excessive water, dehydrated"
    
    try:
        results = rag.semantic_search(query, top_k=3, min_similarity=0.5)
        print_success(f"Found {len(results)} relevant papers")
        
        if results:
            print("\nTop matches:")
            for i, paper in enumerate(results, 1):
                print(f"\n  {i}. {paper.title}")
                print(f"     Similarity: {paper.similarity_score:.2%}")
                print(f"     PMID: {paper.pmid}")
        
        return True
    
    except Exception as e:
        print_error(f"Semantic search failed: {e}")
        return False


def test_full_rag_pipeline(rag):
    """Test 7: Complete RAG Diagnosis Pipeline"""
    print_section("Test 7: Complete RAG Diagnosis Pipeline")
    
    # Example clinical case (Lío from the chat)
    case = {
        "species": "cat",
        "age": 8,
        "sex": "male",
        "chief_complaint": "Polyuria, polydipsia, dehydration",
        "history": "Prednisolone 6 drops/day for 3 months, discontinued 5 days ago",
        "physical_exam": "8% dehydration, dry mucous membranes, weak pulse",
        "labs": {
            "glucose": 524,  # mg/dL
            "BUN": 45,
            "creatinine": 1.8,
            "hematocrit": 25,
            "WBC": 24.2
        },
        "region": "Buenos Aires, Argentina"
    }
    
    print(f"\n{Colors.OKCYAN}Clinical Case:{Colors.ENDC}")
    print(f"  Species: {case['species']}")
    print(f"  Age: {case['age']} years, {case['sex']}")
    print(f"  Chief Complaint: {case['chief_complaint']}")
    print(f"  Key Lab: Glucose {case['labs']['glucose']} mg/dL (critical)")
    
    print(f"\n{Colors.WARNING}Running full RAG pipeline... (this may take 15-30 seconds){Colors.ENDC}")
    
    try:
        result = rag.rag_diagnose(case)
        
        print_success("RAG diagnosis completed!")
        
        # Display results
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}DIAGNOSIS RESULTS{Colors.ENDC}")
        print(f"{Colors.OKGREEN}{'=' * 70}{Colors.ENDC}")
        
        if result.get('differential_diagnoses'):
            print(f"\n{Colors.BOLD}Differential Diagnoses:{Colors.ENDC}")
            for i, dx in enumerate(result['differential_diagnoses'][:3], 1):
                print(f"\n  {i}. {dx['diagnosis']}")
                print(f"     Probability: {dx.get('probability', 0):.1%}")
                print(f"     GRADE Score: {dx.get('grade_score', 'N/A')}")
                print(f"     Rationale: {dx.get('rationale', '')[:150]}...")
                if dx.get('supporting_evidence'):
                    print(f"     Evidence: {', '.join(dx['supporting_evidence'][:3])}")
        
        if result.get('diagnostic_plan'):
            print(f"\n{Colors.BOLD}Diagnostic Plan:{Colors.ENDC}")
            for i, test in enumerate(result['diagnostic_plan'][:5], 1):
                print(f"  {i}. {test}")
        
        if result.get('immediate_actions'):
            print(f"\n{Colors.BOLD}Immediate Actions:{Colors.ENDC}")
            for i, action in enumerate(result['immediate_actions'][:5], 1):
                print(f"  {i}. {action}")
        
        if result.get('cited_papers'):
            print(f"\n{Colors.BOLD}Cited Scientific Papers: {len(result['cited_papers'])}{Colors.ENDC}")
            for i, paper in enumerate(result['cited_papers'][:5], 1):
                print(f"\n  {i}. {paper.get('title', 'N/A')[:80]}...")
                print(f"     PMID: {paper.get('pmid', 'N/A')}")
                if paper.get('key_finding'):
                    print(f"     Finding: {paper['key_finding'][:100]}...")
        
        if result.get('metadata'):
            meta = result['metadata']
            print(f"\n{Colors.BOLD}Performance Metrics:{Colors.ENDC}")
            print(f"  Total papers searched: {meta.get('total_papers_searched', 'N/A')}")
            print(f"  Relevant papers used: {meta.get('relevant_papers', 'N/A')}")
            print(f"  Latency: {meta.get('latency_seconds', 0):.2f} seconds")
        
        # Save results to file
        output_file = "rag_diagnosis_result.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\n{Colors.OKCYAN}Full results saved to: {output_file}{Colors.ENDC}")
        
        return True
    
    except Exception as e:
        print_error(f"RAG diagnosis failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print_header("VetrIAge RAG System Test Suite")
    
    print(f"{Colors.OKCYAN}Testing complete RAG pipeline for veterinary diagnostics{Colors.ENDC}")
    print(f"{Colors.OKCYAN}Based on NVIDIA SLM research and claude-scientific-skills{Colors.ENDC}\n")
    
    # Check environment
    print_section("Environment Check")
    env_vars = {
        "NCBI_API_KEY": "PubMed API key",
        "OPENAI_API_KEY": "OpenAI embeddings",
        "ANTHROPIC_API_KEY": "Claude LLM"
    }
    
    missing_vars = []
    for var, description in env_vars.items():
        if os.getenv(var):
            print_success(f"{var} configured ({description})")
        else:
            print_warning(f"{var} not configured ({description})")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n{Colors.WARNING}⚠ Some API keys are missing. Tests may fail or use fallback methods.{Colors.ENDC}")
        print(f"{Colors.WARNING}  Set them in cognition_base/rag/.env or as environment variables.{Colors.ENDC}")
    
    # Run tests
    test_results = []
    
    # Test 1: Initialization
    rag = test_initialization()
    test_results.append(("Initialization", rag is not None))
    
    if rag is None:
        print_error("Cannot continue without RAG system. Check API keys and dependencies.")
        return
    
    # Test 2: Query Expansion
    result = test_query_expansion(rag)
    test_results.append(("Query Expansion", result))
    
    # Test 3: PubMed Search
    papers = test_pubmed_search(rag)
    test_results.append(("PubMed Search", len(papers) > 0))
    
    # Test 4: Embeddings
    if papers:
        result = test_embeddings(rag, papers)
        test_results.append(("Embedding Generation", result))
        
        # Test 5: Vector Store
        result = test_vector_store(rag, papers)
        test_results.append(("Vector Store", result))
        
        # Test 6: Semantic Search
        result = test_semantic_search(rag)
        test_results.append(("Semantic Search", result))
    else:
        test_results.append(("Embedding Generation", False))
        test_results.append(("Vector Store", False))
        test_results.append(("Semantic Search", False))
    
    # Test 7: Full Pipeline
    result = test_full_rag_pipeline(rag)
    test_results.append(("Full RAG Pipeline", result))
    
    # Summary
    print_header("Test Summary")
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        if result:
            print_success(f"{test_name:.<40} PASS")
        else:
            print_error(f"{test_name:.<40} FAIL")
    
    print(f"\n{Colors.BOLD}Total: {passed}/{total} tests passed{Colors.ENDC}")
    
    if passed == total:
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}✓ All tests passed! RAG system is fully operational.{Colors.ENDC}")
    elif passed >= total * 0.7:
        print(f"\n{Colors.WARNING}{Colors.BOLD}⚠ Most tests passed. Some features may be limited.{Colors.ENDC}")
    else:
        print(f"\n{Colors.FAIL}{Colors.BOLD}✗ Many tests failed. Check API keys and dependencies.{Colors.ENDC}")


if __name__ == "__main__":
    main()
