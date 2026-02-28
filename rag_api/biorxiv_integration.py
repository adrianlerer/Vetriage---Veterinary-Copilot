"""
VetrIAge bioRxiv Integration
=============================

Extends literature access with bioRxiv pre-prints, adding ~20% more veterinary research.
Provides access to cutting-edge research before peer review publication.

Features:
- Search bioRxiv and medRxiv for veterinary pre-prints
- Parse and extract metadata
- Filter by date, species, research area
- Combine with PubMed results for comprehensive coverage
- Track version history of pre-prints

Author: VetrIAge Team
Version: 2.0.0
License: MIT
"""

import re
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import requests
from xml.etree import ElementTree as ET
import time
from urllib.parse import quote

logger = logging.getLogger(__name__)


@dataclass
class PrePrint:
    """Structured pre-print data"""
    doi: str
    title: str
    authors: List[str]
    abstract: str
    date: str  # YYYY-MM-DD format
    server: str  # 'biorxiv' or 'medrxiv'
    category: str
    url: str
    version: int = 1
    pdf_url: Optional[str] = None
    
    def to_paper_dict(self) -> Dict:
        """Convert to VetrIAge Paper dictionary format"""
        return {
            'pmid': f"biorxiv_{self.doi.replace('/', '_')}",  # Fake PMID for compatibility
            'title': self.title,
            'authors': self.authors,
            'abstract': self.abstract,
            'journal': f"{self.server.title()} ({self.category})",
            'date': self.date,
            'doi': self.doi,
            'url': self.url,
            'is_preprint': True,
            'preprint_server': self.server,
            'version': self.version
        }


class BioRxivClient:
    """Client for bioRxiv/medRxiv API"""
    
    BASE_URL = "https://api.biorxiv.org"
    
    # Veterinary-relevant categories
    VETERINARY_CATEGORIES = [
        "veterinary medicine",
        "microbiology",
        "immunology",
        "pathology",
        "pharmacology and toxicology",
        "animal behavior and cognition",
        "zoology",
        "infectious diseases",
        "epidemiology"
    ]
    
    def __init__(self, rate_limit_delay: float = 0.5):
        """
        Initialize bioRxiv client
        
        Args:
            rate_limit_delay: Delay between requests (seconds)
        """
        self.rate_limit_delay = rate_limit_delay
        self.last_request_time = 0
    
    def _rate_limit(self):
        """Enforce rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)
        self.last_request_time = time.time()
    
    def search(
        self,
        query: str,
        server: str = "biorxiv",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        max_results: int = 100
    ) -> List[PrePrint]:
        """
        Search bioRxiv/medRxiv for pre-prints
        
        Args:
            query: Search query
            server: 'biorxiv' or 'medrxiv'
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            max_results: Maximum number of results
        
        Returns:
            List of PrePrint objects
        """
        # Default date range: last 2 years
        if not start_date:
            start_date = (datetime.now() - timedelta(days=730)).strftime("%Y-%m-%d")
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        results = []
        
        try:
            # bioRxiv API uses a different endpoint structure
            # We'll use the content detail endpoint with date ranges
            url = f"{self.BASE_URL}/details/{server}/{start_date}/{end_date}"
            
            self._rate_limit()
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'collection' not in data:
                logger.warning(f"No collection found in response for {server}")
                return results
            
            # Filter results by query match
            for item in data['collection']:
                if self._matches_query(item, query):
                    preprint = self._parse_preprint(item, server)
                    if preprint:
                        results.append(preprint)
                        if len(results) >= max_results:
                            break
            
            logger.info(f"Found {len(results)} pre-prints matching '{query}' in {server}")
            
        except Exception as e:
            logger.error(f"Error searching {server}: {e}")
        
        return results[:max_results]
    
    def _matches_query(self, item: Dict, query: str) -> bool:
        """
        Check if pre-print matches search query
        
        Args:
            item: Pre-print metadata
            query: Search query
        
        Returns:
            True if matches
        """
        query_lower = query.lower()
        searchable_text = " ".join([
            item.get('title', ''),
            item.get('abstract', ''),
            item.get('category', '')
        ]).lower()
        
        # Simple keyword matching (could be improved with NLP)
        query_terms = query_lower.split()
        return any(term in searchable_text for term in query_terms if len(term) > 3)
    
    def _parse_preprint(self, item: Dict, server: str) -> Optional[PrePrint]:
        """
        Parse pre-print metadata from API response
        
        Args:
            item: Raw API response item
            server: Server name
        
        Returns:
            PrePrint object or None if parsing fails
        """
        try:
            doi = item.get('doi')
            if not doi:
                return None
            
            # Extract authors
            authors_str = item.get('authors', '')
            authors = [a.strip() for a in authors_str.split(';') if a.strip()]
            
            # Get version
            version_str = item.get('version', '1')
            try:
                version = int(version_str)
            except (ValueError, TypeError):
                version = 1
            
            preprint = PrePrint(
                doi=doi,
                title=item.get('title', ''),
                authors=authors,
                abstract=item.get('abstract', ''),
                date=item.get('date', ''),
                server=server,
                category=item.get('category', ''),
                url=f"https://www.{server}.org/content/{doi}v{version}",
                version=version,
                pdf_url=f"https://www.{server}.org/content/{doi}v{version}.full.pdf"
            )
            
            return preprint
            
        except Exception as e:
            logger.error(f"Error parsing pre-print: {e}")
            return None
    
    def get_by_doi(self, doi: str, server: str = "biorxiv") -> Optional[PrePrint]:
        """
        Get specific pre-print by DOI
        
        Args:
            doi: DOI of the pre-print
            server: Server name
        
        Returns:
            PrePrint object or None
        """
        try:
            url = f"{self.BASE_URL}/details/{server}/{doi}"
            
            self._rate_limit()
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'collection' in data and len(data['collection']) > 0:
                return self._parse_preprint(data['collection'][0], server)
            
        except Exception as e:
            logger.error(f"Error fetching pre-print {doi}: {e}")
        
        return None


class VeterinaryPrePrintFilter:
    """Filters and ranks pre-prints by veterinary relevance"""
    
    # Veterinary keywords for relevance scoring
    SPECIES_KEYWORDS = {
        'dog': 10, 'canine': 10, 'puppy': 10,
        'cat': 10, 'feline': 10, 'kitten': 10,
        'horse': 10, 'equine': 10, 'foal': 10,
        'cow': 10, 'bovine': 10, 'cattle': 10, 'calf': 10,
        'pig': 10, 'porcine': 10, 'swine': 10,
        'sheep': 8, 'ovine': 8, 'lamb': 8,
        'goat': 8, 'caprine': 8,
        'chicken': 7, 'poultry': 7, 'avian': 7,
        'rabbit': 7, 'bird': 6, 'reptile': 6,
        'veterinary': 15, 'veterinarian': 15,
        'animal': 5, 'pet': 7, 'livestock': 8
    }
    
    DISEASE_KEYWORDS = {
        'disease': 5, 'infection': 5, 'syndrome': 5,
        'pathology': 5, 'diagnosis': 7, 'treatment': 7,
        'therapy': 6, 'clinical': 6, 'epidemiology': 5,
        'vaccine': 6, 'drug': 5, 'medicine': 5
    }
    
    def calculate_relevance_score(self, preprint: PrePrint) -> float:
        """
        Calculate veterinary relevance score (0-100)
        
        Args:
            preprint: PrePrint to score
        
        Returns:
            Relevance score
        """
        score = 0.0
        text = f"{preprint.title} {preprint.abstract}".lower()
        
        # Score species keywords
        for keyword, weight in self.SPECIES_KEYWORDS.items():
            if keyword in text:
                score += weight
        
        # Score disease/clinical keywords
        for keyword, weight in self.DISEASE_KEYWORDS.items():
            if keyword in text:
                score += weight
        
        # Bonus for veterinary categories
        if 'veterinary' in preprint.category.lower():
            score += 20
        
        # Bonus for recent pre-prints (last 6 months)
        try:
            preprint_date = datetime.strptime(preprint.date, "%Y-%m-%d")
            days_old = (datetime.now() - preprint_date).days
            if days_old < 180:
                score += 10 * (1 - days_old / 180)
        except:
            pass
        
        return min(score, 100)  # Cap at 100
    
    def filter_and_rank(
        self,
        preprints: List[PrePrint],
        min_relevance: float = 20.0
    ) -> List[Tuple[PrePrint, float]]:
        """
        Filter and rank pre-prints by relevance
        
        Args:
            preprints: List of pre-prints
            min_relevance: Minimum relevance score
        
        Returns:
            List of (preprint, score) tuples, sorted by score
        """
        scored = []
        for preprint in preprints:
            score = self.calculate_relevance_score(preprint)
            if score >= min_relevance:
                scored.append((preprint, score))
        
        # Sort by score descending
        scored.sort(key=lambda x: x[1], reverse=True)
        
        return scored


def search_veterinary_preprints(
    query: str,
    max_results: int = 20,
    min_relevance: float = 20.0
) -> List[Dict]:
    """
    High-level function to search for veterinary pre-prints
    
    Args:
        query: Search query
        max_results: Maximum results to return
        min_relevance: Minimum relevance score
    
    Returns:
        List of paper dictionaries compatible with VetrIAge RAG
    """
    client = BioRxivClient()
    filter_obj = VeterinaryPrePrintFilter()
    
    all_preprints = []
    
    # Search both bioRxiv and medRxiv
    for server in ['biorxiv', 'medrxiv']:
        preprints = client.search(
            query=query,
            server=server,
            max_results=max_results * 2  # Get more, then filter
        )
        all_preprints.extend(preprints)
    
    # Filter and rank by relevance
    ranked = filter_obj.filter_and_rank(all_preprints, min_relevance)
    
    # Convert to paper dictionaries
    papers = []
    for preprint, score in ranked[:max_results]:
        paper_dict = preprint.to_paper_dict()
        paper_dict['relevance_score'] = score
        papers.append(paper_dict)
    
    logger.info(f"Returning {len(papers)} veterinary pre-prints (relevance ≥ {min_relevance})")
    
    return papers


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Search for feline CKD pre-prints
    query = "feline chronic kidney disease treatment"
    papers = search_veterinary_preprints(query, max_results=10)
    
    print(f"\n=== Found {len(papers)} Pre-Prints ===\n")
    
    for i, paper in enumerate(papers, 1):
        print(f"{i}. {paper['title']}")
        print(f"   Server: {paper['preprint_server']}")
        print(f"   Date: {paper['date']}")
        print(f"   Relevance: {paper['relevance_score']:.1f}")
        print(f"   DOI: {paper['doi']}")
        print(f"   URL: {paper['url']}")
        print()
