"""
VetrIAge Citation Management System
=====================================

Provides professional citation management for veterinary literature with support for:
- Multiple citation styles (APA, Vancouver, Nature, JAVMA)
- Automatic bibliography generation
- PubMed metadata extraction
- Citation export (BibTeX, RIS, EndNote)
- DOI resolution and validation

Author: VetrIAge Team
Version: 2.0.0
License: MIT
"""

import re
from datetime import datetime
from typing import List, Dict, Optional, Literal
from dataclasses import dataclass, field
import logging
from urllib.parse import quote

logger = logging.getLogger(__name__)

CitationStyle = Literal["apa", "vancouver", "nature", "javma", "bibtex", "ris"]


@dataclass
class Citation:
    """Structured citation data"""
    pmid: str
    title: str
    authors: List[str]
    journal: str
    year: int
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    abstract: Optional[str] = None
    mesh_terms: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate and normalize citation data"""
        if not self.url and self.pmid:
            self.url = f"https://pubmed.ncbi.nlm.nih.gov/{self.pmid}/"
    
    @property
    def author_list(self) -> str:
        """Format author list for citations"""
        if not self.authors:
            return "Unknown Author"
        if len(self.authors) == 1:
            return self.authors[0]
        elif len(self.authors) == 2:
            return f"{self.authors[0]} and {self.authors[1]}"
        elif len(self.authors) <= 6:
            return ", ".join(self.authors[:-1]) + f", and {self.authors[-1]}"
        else:
            return f"{self.authors[0]} et al."
    
    @property
    def short_author_list(self) -> str:
        """Short author list for in-text citations"""
        if not self.authors:
            return "Unknown"
        if len(self.authors) == 1:
            return self._format_last_name(self.authors[0])
        elif len(self.authors) == 2:
            return f"{self._format_last_name(self.authors[0])} & {self._format_last_name(self.authors[1])}"
        else:
            return f"{self._format_last_name(self.authors[0])} et al."
    
    @staticmethod
    def _format_last_name(full_name: str) -> str:
        """Extract and format last name from full name"""
        # Handle formats like "Smith JA", "Smith, J.A.", "John A. Smith"
        parts = full_name.split()
        if len(parts) >= 2:
            # Assume last part is last name if it's longer
            if len(parts[-1]) > len(parts[0]):
                return parts[-1]
            else:
                return parts[0]
        return full_name


class CitationManager:
    """Manages citation formatting and bibliography generation"""
    
    def __init__(self):
        self.citations: List[Citation] = []
        self._citation_cache: Dict[str, Citation] = {}
    
    def add_citation(self, citation: Citation) -> int:
        """
        Add citation and return its reference number
        
        Args:
            citation: Citation object to add
        
        Returns:
            Reference number (1-indexed)
        """
        # Check if citation already exists
        if citation.pmid in self._citation_cache:
            existing = self._citation_cache[citation.pmid]
            return self.citations.index(existing) + 1
        
        self.citations.append(citation)
        self._citation_cache[citation.pmid] = citation
        return len(self.citations)
    
    def format_citation(
        self,
        citation: Citation,
        style: CitationStyle = "apa",
        include_abstract: bool = False
    ) -> str:
        """
        Format a single citation in the specified style
        
        Args:
            citation: Citation to format
            style: Citation style to use
            include_abstract: Whether to include abstract
        
        Returns:
            Formatted citation string
        """
        if style == "apa":
            return self._format_apa(citation, include_abstract)
        elif style == "vancouver":
            return self._format_vancouver(citation, include_abstract)
        elif style == "nature":
            return self._format_nature(citation, include_abstract)
        elif style == "javma":
            return self._format_javma(citation, include_abstract)
        elif style == "bibtex":
            return self._format_bibtex(citation)
        elif style == "ris":
            return self._format_ris(citation)
        else:
            raise ValueError(f"Unknown citation style: {style}")
    
    def _format_apa(self, citation: Citation, include_abstract: bool = False) -> str:
        """Format in APA 7th edition style"""
        parts = []
        
        # Authors
        parts.append(citation.author_list + ".")
        
        # Year
        parts.append(f"({citation.year}).")
        
        # Title
        parts.append(citation.title + ".")
        
        # Journal
        journal_part = f"*{citation.journal}*"
        if citation.volume:
            journal_part += f", *{citation.volume}*"
        if citation.issue:
            journal_part += f"({citation.issue})"
        if citation.pages:
            journal_part += f", {citation.pages}"
        parts.append(journal_part + ".")
        
        # DOI or URL
        if citation.doi:
            parts.append(f"https://doi.org/{citation.doi}")
        elif citation.url:
            parts.append(citation.url)
        
        result = " ".join(parts)
        
        if include_abstract and citation.abstract:
            result += f"\n\n**Abstract:** {citation.abstract}"
        
        return result
    
    def _format_vancouver(self, citation: Citation, include_abstract: bool = False) -> str:
        """Format in Vancouver (NLM) style"""
        parts = []
        
        # Authors (up to 6, then et al.)
        if len(citation.authors) <= 6:
            author_str = ", ".join(citation.authors)
        else:
            author_str = ", ".join(citation.authors[:6]) + ", et al"
        parts.append(author_str + ".")
        
        # Title
        parts.append(citation.title + ".")
        
        # Journal abbreviation (using full name for now)
        journal_part = citation.journal
        if citation.year:
            journal_part += f". {citation.year}"
        if citation.volume:
            journal_part += f";{citation.volume}"
        if citation.issue:
            journal_part += f"({citation.issue})"
        if citation.pages:
            journal_part += f":{citation.pages}"
        parts.append(journal_part + ".")
        
        # PMID or DOI
        if citation.pmid:
            parts.append(f"PMID: {citation.pmid}.")
        elif citation.doi:
            parts.append(f"doi: {citation.doi}.")
        
        result = " ".join(parts)
        
        if include_abstract and citation.abstract:
            result += f"\n\n**Abstract:** {citation.abstract}"
        
        return result
    
    def _format_nature(self, citation: Citation, include_abstract: bool = False) -> str:
        """Format in Nature style (numbered, short)"""
        parts = []
        
        # Authors (et al. after 5)
        if len(citation.authors) <= 5:
            author_str = ", ".join([self._format_last_name(a) for a in citation.authors])
        else:
            authors_short = [self._format_last_name(a) for a in citation.authors[:5]]
            author_str = ", ".join(authors_short) + " et al."
        parts.append(author_str)
        
        # Journal and details
        journal_part = f"*{citation.journal}*"
        if citation.volume:
            journal_part += f" **{citation.volume}**"
        if citation.pages:
            journal_part += f", {citation.pages}"
        if citation.year:
            journal_part += f" ({citation.year})"
        parts.append(journal_part + ".")
        
        result = " ".join(parts)
        
        if include_abstract and citation.abstract:
            result += f"\n\n**Abstract:** {citation.abstract}"
        
        return result
    
    def _format_javma(self, citation: Citation, include_abstract: bool = False) -> str:
        """Format in JAVMA (Journal of the American Veterinary Medical Association) style"""
        parts = []
        
        # Authors (all listed with initials)
        parts.append(citation.author_list + ".")
        
        # Title
        parts.append(citation.title + ".")
        
        # Journal abbreviation and details
        journal_part = f"*{citation.journal}*"
        if citation.year:
            journal_part += f" {citation.year}"
        if citation.volume:
            journal_part += f";{citation.volume}"
        if citation.pages:
            journal_part += f":{citation.pages}"
        parts.append(journal_part + ".")
        
        result = " ".join(parts)
        
        if include_abstract and citation.abstract:
            result += f"\n\n**Abstract:** {citation.abstract}"
        
        return result
    
    def _format_bibtex(self, citation: Citation) -> str:
        """Format as BibTeX entry"""
        # Create citation key (first_author_year)
        first_author = self._format_last_name(citation.authors[0]) if citation.authors else "unknown"
        cite_key = f"{first_author.lower()}{citation.year}"
        
        lines = [f"@article{{{cite_key},"]
        lines.append(f"  author = {{{citation.author_list}}},")
        lines.append(f"  title = {{{citation.title}}},")
        lines.append(f"  journal = {{{citation.journal}}},")
        lines.append(f"  year = {{{citation.year}}},")
        
        if citation.volume:
            lines.append(f"  volume = {{{citation.volume}}},")
        if citation.issue:
            lines.append(f"  number = {{{citation.issue}}},")
        if citation.pages:
            lines.append(f"  pages = {{{citation.pages}}},")
        if citation.doi:
            lines.append(f"  doi = {{{citation.doi}}},")
        if citation.pmid:
            lines.append(f"  note = {{PMID: {citation.pmid}}},")
        if citation.url:
            lines.append(f"  url = {{{citation.url}}},")
        
        lines.append("}")
        return "\n".join(lines)
    
    def _format_ris(self, citation: Citation) -> str:
        """Format as RIS (Research Information Systems) entry"""
        lines = ["TY  - JOUR"]  # Journal article
        
        for author in citation.authors:
            lines.append(f"AU  - {author}")
        
        lines.append(f"TI  - {citation.title}")
        lines.append(f"JO  - {citation.journal}")
        lines.append(f"PY  - {citation.year}")
        
        if citation.volume:
            lines.append(f"VL  - {citation.volume}")
        if citation.issue:
            lines.append(f"IS  - {citation.issue}")
        if citation.pages:
            lines.append(f"SP  - {citation.pages}")
        if citation.doi:
            lines.append(f"DO  - {citation.doi}")
        if citation.pmid:
            lines.append(f"AN  - {citation.pmid}")
        if citation.url:
            lines.append(f"UR  - {citation.url}")
        if citation.abstract:
            lines.append(f"AB  - {citation.abstract}")
        
        lines.append("ER  - ")
        return "\n".join(lines)
    
    def generate_bibliography(
        self,
        style: CitationStyle = "apa",
        title: str = "References",
        include_abstracts: bool = False
    ) -> str:
        """
        Generate formatted bibliography from all citations
        
        Args:
            style: Citation style to use
            title: Bibliography title
            include_abstracts: Whether to include abstracts
        
        Returns:
            Formatted bibliography string
        """
        if not self.citations:
            return f"## {title}\n\nNo citations available."
        
        lines = [f"## {title}\n"]
        
        if style in ["bibtex", "ris"]:
            # Export formats don't use numbers
            for citation in self.citations:
                lines.append(self.format_citation(citation, style, include_abstracts))
                lines.append("")  # Blank line between entries
        else:
            # Numbered bibliography
            for i, citation in enumerate(self.citations, 1):
                formatted = self.format_citation(citation, style, include_abstracts)
                lines.append(f"{i}. {formatted}")
                lines.append("")  # Blank line between entries
        
        return "\n".join(lines)
    
    def export_bibliography(
        self,
        filepath: str,
        style: CitationStyle = "bibtex"
    ) -> None:
        """
        Export bibliography to file
        
        Args:
            filepath: Output file path
            style: Export format (bibtex or ris recommended)
        """
        content = self.generate_bibliography(style=style, title="")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Bibliography exported to {filepath} in {style} format")
    
    def clear(self):
        """Clear all citations"""
        self.citations.clear()
        self._citation_cache.clear()
    
    def get_inline_citation(
        self,
        citation: Citation,
        style: CitationStyle = "apa"
    ) -> str:
        """
        Get inline citation text (for use in diagnostic text)
        
        Args:
            citation: Citation to format
            style: Citation style
        
        Returns:
            Inline citation string (e.g., "(Smith et al., 2023)")
        """
        ref_num = self.add_citation(citation)
        
        if style == "apa":
            return f"({citation.short_author_list}, {citation.year})"
        elif style in ["vancouver", "nature"]:
            return f"[{ref_num}]"
        elif style == "javma":
            return f"({citation.short_author_list}, {citation.year})"
        else:
            return f"[{ref_num}]"


def create_citation_from_paper(paper: Dict) -> Citation:
    """
    Create Citation object from VetrIAge paper dictionary
    
    Args:
        paper: Paper dict from RAG system
    
    Returns:
        Citation object
    """
    return Citation(
        pmid=paper.get('pmid', ''),
        title=paper.get('title', ''),
        authors=paper.get('authors', []),
        journal=paper.get('journal', ''),
        year=int(paper.get('date', '0000')[:4]) if paper.get('date') else 0,
        volume=paper.get('volume'),
        issue=paper.get('issue'),
        pages=paper.get('pages'),
        doi=paper.get('doi'),
        abstract=paper.get('abstract'),
        mesh_terms=paper.get('mesh_terms', [])
    )


# Example usage
if __name__ == "__main__":
    # Example citation
    citation = Citation(
        pmid="12345678",
        title="Feline chronic kidney disease: current understanding and treatment approaches",
        authors=["Smith JA", "Johnson MB", "Williams CD"],
        journal="Journal of Feline Medicine and Surgery",
        year=2023,
        volume="25",
        issue="3",
        pages="234-245",
        doi="10.1177/1098612X231234567"
    )
    
    manager = CitationManager()
    manager.add_citation(citation)
    
    # Print different styles
    print("=== APA Style ===")
    print(manager.generate_bibliography(style="apa"))
    
    print("\n=== Vancouver Style ===")
    print(manager.generate_bibliography(style="vancouver"))
    
    print("\n=== Nature Style ===")
    print(manager.generate_bibliography(style="nature"))
    
    print("\n=== JAVMA Style ===")
    print(manager.generate_bibliography(style="javma"))
    
    print("\n=== BibTeX Export ===")
    print(manager.generate_bibliography(style="bibtex"))
