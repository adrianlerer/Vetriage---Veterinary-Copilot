"""
bioRxiv Database Access for VetrIAge
===================================

Access to pre-prints and early veterinary research via bioRxiv API.
Expands literature access by ~20% with cutting-edge research.

Author: VetrIAge Team
Version: 2.1
License: MIT
"""

import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import time
import logging

logger = logging.getLogger(__name__)


class BioRxivSearch:
    """Search bioRxiv for veterinary pre-prints"""
    
    BASE_URL = "https://api.biorxiv.org/details/biorxiv"
    
    def __init__(self, rate_limit: float = 0.5):
        """
        Initialize bioRxiv searcher.
        
        Args:
            rate_limit: Seconds to wait between requests
        """
        self.rate_limit = rate_limit
        self.last_request_time = 0
    
    def _rate_limit_wait(self):
        """Enforce rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit:
            time.sleep(self.rate_limit - time_since_last)
        self.last_request_time = time.time()
    
    def search_veterinary(self, query: str, max_results: int = 10, days_back: int = 365) -> List[Dict]:
        """
        Search bioRxiv for veterinary-related pre-prints.
        
        Args:
            query: Search terms
            max_results: Maximum results to return
            days_back: How many days back to search
        
        Returns:
            List of paper dictionaries
        """
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            # Format dates for API
            start_str = start_date.strftime('%Y-%m-%d')
            end_str = end_date.strftime('%Y-%m-%d')
            
            # bioRxiv API endpoint
            url = f"{self.BASE_URL}/{start_str}/{end_str}/0"
            
            self._rate_limit_wait()
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'collection' not in data:
                logger.warning("No results from bioRxiv API")
                return []
            
            # Filter for veterinary-relevant papers
            vet_keywords = [
                'veterinary', 'canine', 'feline', 'equine', 'bovine',
                'dog', 'cat', 'horse', 'cow', 'animal', 'livestock',
                'companion animal', 'wildlife', 'zoo', 'avian'
            ]
            
            papers = []
            query_lower = query.lower()
            
            for article in data['collection']:
                title = article.get('title', '').lower()
                abstract = article.get('abstract', '').lower()
                
                # Check if veterinary-related
                is_vet_related = any(keyword in title or keyword in abstract 
                                    for keyword in vet_keywords)
                
                # Check if matches query
                matches_query = query_lower in title or query_lower in abstract
                
                if is_vet_related and matches_query:
                    papers.append({
                        'title': article.get('title', ''),
                        'authors': article.get('authors', '').split('; '),
                        'abstract': article.get('abstract', ''),
                        'doi': article.get('doi', ''),
                        'publication_date': article.get('date', ''),
                        'url': f"https://www.biorxiv.org/content/{article.get('doi', '')}",
                        'journal': 'bioRxiv (pre-print)',
                        'source': 'bioRxiv'
                    })
                
                if len(papers) >= max_results:
                    break
            
            logger.info(f"Found {len(papers)} veterinary pre-prints on bioRxiv")
            return papers
        
        except Exception as e:
            logger.error(f"bioRxiv search error: {e}")
            return []
