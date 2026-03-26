"""
Data models for VetrIAge monetization layer.
Defines tiers, API keys, and usage records.
"""

from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class Tier(str, Enum):
    FREE = "free"
    PRO = "pro"
    CLINIC = "clinic"
    ENTERPRISE = "enterprise"


# Tier configuration: limits and pricing
TIER_CONFIG = {
    Tier.FREE: {
        "name": "Free",
        "price_monthly_usd": 0,
        "requests_per_month": 50,
        "requests_per_minute": 5,
        "endpoints": ["diagnose", "safety-check", "species-info", "health"],
        "report_generation": False,
        "literature_search": False,
        "bibliography_export": False,
        "priority_support": False,
    },
    Tier.PRO: {
        "name": "Pro",
        "price_monthly_usd": 49,
        "requests_per_month": 1000,
        "requests_per_minute": 30,
        "endpoints": ["diagnose", "safety-check", "species-info", "health", "search-literature"],
        "report_generation": True,
        "literature_search": True,
        "bibliography_export": True,
        "priority_support": False,
    },
    Tier.CLINIC: {
        "name": "Clinic",
        "price_monthly_usd": 149,
        "requests_per_month": 5000,
        "requests_per_minute": 60,
        "endpoints": "all",
        "report_generation": True,
        "literature_search": True,
        "bibliography_export": True,
        "priority_support": True,
    },
    Tier.ENTERPRISE: {
        "name": "Enterprise",
        "price_monthly_usd": None,  # Custom pricing
        "requests_per_month": None,  # Unlimited
        "requests_per_minute": 120,
        "endpoints": "all",
        "report_generation": True,
        "literature_search": True,
        "bibliography_export": True,
        "priority_support": True,
    },
}


# Cost per endpoint (for internal tracking and margin calculation)
ENDPOINT_COSTS_USD = {
    "diagnose": 0.15,        # Embeddings + LLM inference
    "safety-check": 0.02,    # Local DB lookup
    "search-literature": 0.08,  # PubMed + embeddings
    "export-bibliography": 0.01,
    "species-info": 0.01,
    "visualizations": 0.01,
}


class APIKeyRecord(BaseModel):
    key_id: str
    api_key_hash: str
    owner_email: str
    owner_name: Optional[str] = None
    tier: Tier = Tier.FREE
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    metadata: Optional[dict] = None


class UsageRecord(BaseModel):
    key_id: str
    endpoint: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    response_time_ms: int = 0
    status_code: int = 200
    tokens_used: int = 0
    estimated_cost_usd: float = 0.0
