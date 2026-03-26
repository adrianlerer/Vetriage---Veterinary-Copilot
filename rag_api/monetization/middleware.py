"""
FastAPI middleware for API key authentication and rate limiting.
Intercepts requests, validates keys, checks tier limits, and logs usage.
"""

import time
import logging
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from .database import validate_api_key, log_usage, get_monthly_usage, get_minute_usage
from .models import TIER_CONFIG, ENDPOINT_COSTS_USD, Tier

logger = logging.getLogger(__name__)

# Endpoints that don't require auth
PUBLIC_ENDPOINTS = {"/", "/docs", "/redoc", "/openapi.json", "/api/v2/health", "/api/v2/pricing", "/api/v2/register", "/terms", "/privacy", "/refund-policy"}

# Map URL paths to endpoint names for tier checking
ENDPOINT_NAMES = {
    "/api/v2/diagnose": "diagnose",
    "/api/v2/safety-check": "safety-check",
    "/api/v2/search-literature": "search-literature",
    "/api/v2/export-bibliography": "export-bibliography",
    "/api/v2/species-info": "species-info",
    "/api/v2/visualizations": "visualizations",
}


def _resolve_endpoint_name(path: str) -> str:
    """Resolve a URL path to an endpoint name, handling path params."""
    if path in ENDPOINT_NAMES:
        return ENDPOINT_NAMES[path]
    # Handle paths with params like /api/v2/species-info/dog
    for prefix, name in ENDPOINT_NAMES.items():
        if path.startswith(prefix):
            return name
    return path


class APIKeyAuthMiddleware(BaseHTTPMiddleware):
    """Validates API key from X-API-Key header or ?api_key query param."""

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Skip auth for public endpoints
        if path in PUBLIC_ENDPOINTS or path.startswith("/docs") or path.startswith("/redoc"):
            return await call_next(request)

        # Extract API key
        api_key = request.headers.get("X-API-Key") or request.query_params.get("api_key")
        if not api_key:
            return JSONResponse(
                status_code=401,
                content={
                    "error": "api_key_required",
                    "message": "API key required. Pass via X-API-Key header or ?api_key query param.",
                    "docs": "/api/v2/pricing",
                },
            )

        # Validate key
        key_record = validate_api_key(api_key)
        if not key_record:
            return JSONResponse(
                status_code=401,
                content={
                    "error": "invalid_api_key",
                    "message": "Invalid or expired API key.",
                },
            )

        # Attach key info to request state for downstream use
        request.state.api_key = key_record
        request.state.tier = key_record.tier

        response = await call_next(request)
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Enforces per-minute and per-month rate limits based on tier."""

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        if path in PUBLIC_ENDPOINTS or path.startswith("/docs") or path.startswith("/redoc"):
            return await call_next(request)

        # Need auth to have run first
        key_record = getattr(request.state, "api_key", None)
        if not key_record:
            return await call_next(request)

        tier = key_record.tier
        config = TIER_CONFIG[tier]
        endpoint_name = _resolve_endpoint_name(path)

        # Check endpoint access
        allowed = config["endpoints"]
        if allowed != "all" and endpoint_name not in allowed:
            return JSONResponse(
                status_code=403,
                content={
                    "error": "endpoint_not_available",
                    "message": f"Endpoint '{endpoint_name}' is not available on the {config['name']} plan.",
                    "upgrade_to": "pro",
                    "pricing": "/api/v2/pricing",
                },
            )

        # Check feature gates
        if endpoint_name == "search-literature" and not config.get("literature_search"):
            return JSONResponse(status_code=403, content={
                "error": "feature_not_available",
                "message": "Literature search requires Pro plan or higher.",
                "pricing": "/api/v2/pricing",
            })

        # Check per-minute rate limit
        minute_usage = get_minute_usage(key_record.key_id)
        rpm_limit = config["requests_per_minute"]
        if minute_usage >= rpm_limit:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "rate_limit_exceeded",
                    "message": f"Rate limit: {rpm_limit} requests/minute on {config['name']} plan.",
                    "retry_after_seconds": 60,
                },
                headers={"Retry-After": "60"},
            )

        # Check monthly quota
        monthly_limit = config["requests_per_month"]
        if monthly_limit is not None:  # None = unlimited (Enterprise)
            monthly_usage = get_monthly_usage(key_record.key_id)
            if monthly_usage >= monthly_limit:
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "monthly_quota_exceeded",
                        "message": f"Monthly limit of {monthly_limit} requests reached on {config['name']} plan.",
                        "current_usage": monthly_usage,
                        "limit": monthly_limit,
                        "upgrade_to": _next_tier(tier),
                        "pricing": "/api/v2/pricing",
                    },
                )

        response = await call_next(request)
        return response


class UsageTrackingMiddleware(BaseHTTPMiddleware):
    """Logs every API call for billing and analytics."""

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        if path in PUBLIC_ENDPOINTS or path.startswith("/docs") or path.startswith("/redoc"):
            return await call_next(request)

        start_time = time.time()
        response = await call_next(request)
        elapsed_ms = int((time.time() - start_time) * 1000)

        key_record = getattr(request.state, "api_key", None)
        if key_record:
            endpoint_name = _resolve_endpoint_name(path)
            cost = ENDPOINT_COSTS_USD.get(endpoint_name, 0.01)
            try:
                log_usage(
                    key_id=key_record.key_id,
                    endpoint=endpoint_name,
                    response_time_ms=elapsed_ms,
                    status_code=response.status_code,
                    estimated_cost_usd=cost,
                )
            except Exception as e:
                logger.error(f"Failed to log usage: {e}")

        return response


def _next_tier(current: Tier) -> str:
    order = [Tier.FREE, Tier.PRO, Tier.CLINIC, Tier.ENTERPRISE]
    idx = order.index(current)
    if idx < len(order) - 1:
        return order[idx + 1].value
    return "enterprise"
