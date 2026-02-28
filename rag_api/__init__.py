"""
VetrIAge RAG Module
===================

Retrieval-Augmented Generation system for veterinary diagnostics.
"""

from .vetriage_rag import (
    VetriageRAG,
    Paper,
    initialize_rag_system,
    quick_diagnosis
)

__all__ = [
    'VetriageRAG',
    'Paper',
    'initialize_rag_system',
    'quick_diagnosis'
]

__version__ = '2.0.0'
__author__ = 'VetrIAge Team'
