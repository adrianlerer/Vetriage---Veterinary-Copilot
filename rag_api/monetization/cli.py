#!/usr/bin/env python3
"""
CLI tool for managing VetrIAge API keys and billing.

Usage:
    python -m monetization.cli setup              # Initialize database
    python -m monetization.cli create-key EMAIL    # Create a free API key
    python -m monetization.cli create-key EMAIL --tier pro --name "Dr. Smith"
    python -m monetization.cli list-keys           # List all active keys
    python -m monetization.cli usage KEY_ID        # Show usage for a key
    python -m monetization.cli upgrade KEY_ID pro  # Upgrade tier
    python -m monetization.cli deactivate KEY_ID   # Deactivate a key
"""

import sys
import argparse
from .database import init_db, create_api_key, get_usage_summary, update_tier, deactivate_key, get_db
from .models import Tier, TIER_CONFIG


def cmd_setup(args):
    init_db()
    print("Database initialized successfully.")


def cmd_create_key(args):
    tier = Tier(args.tier)
    key_id, raw_key = create_api_key(args.email, args.name, tier)
    config = TIER_CONFIG[tier]
    print(f"\n  API Key Created")
    print(f"  {'='*50}")
    print(f"  Key ID:    {key_id}")
    print(f"  API Key:   {raw_key}")
    print(f"  Tier:      {config['name']} (${config['price_monthly_usd'] or 'custom'}/mo)")
    print(f"  Limits:    {config['requests_per_month'] or 'unlimited'} req/month, {config['requests_per_minute']} req/min")
    print(f"  Owner:     {args.email}")
    print(f"\n  IMPORTANT: Save this API key now. It cannot be retrieved later.\n")


def cmd_list_keys(args):
    with get_db() as conn:
        rows = conn.execute(
            "SELECT key_id, owner_email, owner_name, tier, is_active, created_at FROM api_keys ORDER BY created_at DESC"
        ).fetchall()
    if not rows:
        print("No API keys found.")
        return
    print(f"\n  {'Key ID':<20} {'Email':<30} {'Tier':<12} {'Active':<8} {'Created'}")
    print(f"  {'-'*90}")
    for r in rows:
        print(f"  {r['key_id']:<20} {r['owner_email']:<30} {r['tier']:<12} {'yes' if r['is_active'] else 'no':<8} {r['created_at'][:10]}")
    print()


def cmd_usage(args):
    summary = get_usage_summary(args.key_id)
    print(f"\n  Usage for {args.key_id}")
    print(f"  Period: {summary['period']}")
    print(f"  Total requests: {summary['total_requests']}")
    print(f"  Total cost: ${summary['total_cost_usd']:.4f}")
    if summary["by_endpoint"]:
        print(f"\n  {'Endpoint':<25} {'Requests':<10} {'Cost':<10} {'Avg ms'}")
        print(f"  {'-'*55}")
        for ep in summary["by_endpoint"]:
            print(f"  {ep['endpoint']:<25} {ep['requests']:<10} ${ep['cost_usd']:<9.4f} {ep['avg_response_ms']}ms")
    print()


def cmd_upgrade(args):
    new_tier = Tier(args.tier)
    update_tier(args.key_id, new_tier)
    print(f"Upgraded {args.key_id} to {new_tier.value}.")


def cmd_deactivate(args):
    deactivate_key(args.key_id)
    print(f"Deactivated {args.key_id}.")


def main():
    parser = argparse.ArgumentParser(description="VetrIAge API Key Management")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("setup", help="Initialize database")

    p_create = sub.add_parser("create-key", help="Create an API key")
    p_create.add_argument("email")
    p_create.add_argument("--name", default=None)
    p_create.add_argument("--tier", default="free", choices=[t.value for t in Tier])

    sub.add_parser("list-keys", help="List all API keys")

    p_usage = sub.add_parser("usage", help="Show usage for a key")
    p_usage.add_argument("key_id")

    p_upgrade = sub.add_parser("upgrade", help="Upgrade a key's tier")
    p_upgrade.add_argument("key_id")
    p_upgrade.add_argument("tier", choices=[t.value for t in Tier])

    p_deactivate = sub.add_parser("deactivate", help="Deactivate an API key")
    p_deactivate.add_argument("key_id")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    commands = {
        "setup": cmd_setup,
        "create-key": cmd_create_key,
        "list-keys": cmd_list_keys,
        "usage": cmd_usage,
        "upgrade": cmd_upgrade,
        "deactivate": cmd_deactivate,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
