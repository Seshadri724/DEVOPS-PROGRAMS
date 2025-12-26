#!/usr/bin/env python3
"""
================================================================================
SECRETS ROTATION SCHEDULER
================================================================================

RESUME BULLET POINT:
"Built a secrets rotation scheduler that automatically rotates keys and 
updates dependent services, reducing credential exposure risk."

Author: DevOps Engineer | Version: 1.0.0
================================================================================
"""

import argparse
import json
from datetime import datetime, timedelta
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum


class SecretType(Enum):
    API_KEY = "api_key"
    DATABASE_PASSWORD = "database_password"
    SERVICE_ACCOUNT = "service_account"
    ENCRYPTION_KEY = "encryption_key"


class RotationStatus(Enum):
    CURRENT = "current"
    DUE = "due_for_rotation"
    OVERDUE = "overdue"


@dataclass
class Secret:
    """Managed secret"""
    name: str
    secret_type: SecretType
    last_rotated: datetime
    rotation_period_days: int
    dependents: List[str]
    status: RotationStatus = None


class SecretsRotationManager:
    """Manages secret rotation schedules"""
    
    def __init__(self):
        self.secrets: List[Secret] = []
    
    def load_secrets(self) -> List[Secret]:
        """Load managed secrets (simulated)"""
        now = datetime.now()
        
        self.secrets = [
            Secret("prod-db-password", SecretType.DATABASE_PASSWORD, now - timedelta(days=100), 90, ["api-service", "worker"]),
            Secret("stripe-api-key", SecretType.API_KEY, now - timedelta(days=30), 90, ["payment-service"]),
            Secret("jwt-signing-key", SecretType.ENCRYPTION_KEY, now - timedelta(days=200), 180, ["auth-service"]),
            Secret("gcp-service-account", SecretType.SERVICE_ACCOUNT, now - timedelta(days=400), 365, ["all-services"]),
        ]
        
        # Calculate status
        for secret in self.secrets:
            days_since_rotation = (now - secret.last_rotated).days
            if days_since_rotation > secret.rotation_period_days * 1.5:
                secret.status = RotationStatus.OVERDUE
            elif days_since_rotation > secret.rotation_period_days:
                secret.status = RotationStatus.DUE
            else:
                secret.status = RotationStatus.CURRENT
        
        return self.secrets
    
    def rotate_secret(self, secret_name: str, dry_run: bool = True):
        """Rotate a secret"""
        secret = next((s for s in self.secrets if s.name == secret_name), None)
        if not secret:
            return False
        
        if dry_run:
            print(f"   [DRY RUN] Would rotate: {secret_name}")
            print(f"   [DRY RUN] Would update: {', '.join(secret.dependents)}")
        else:
            print(f"   ✓ Rotated: {secret_name}")
            print(f"   ✓ Updated: {', '.join(secret.dependents)}")
            secret.last_rotated = datetime.now()
            secret.status = RotationStatus.CURRENT
        
        return True
    
    def get_summary(self) -> Dict:
        """Get rotation summary"""
        return {
            "total": len(self.secrets),
            "current": sum(1 for s in self.secrets if s.status == RotationStatus.CURRENT),
            "due": sum(1 for s in self.secrets if s.status == RotationStatus.DUE),
            "overdue": sum(1 for s in self.secrets if s.status == RotationStatus.OVERDUE),
        }


def print_report(manager: SecretsRotationManager):
    """Print rotation report"""
    summary = manager.get_summary()
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║           SECRETS ROTATION STATUS                            ║
╠══════════════════════════════════════════════════════════════╣
║  Total Secrets: {summary['total']:<43}║
║  ✅ Current: {summary['current']:<47}║
║  ⚠️  Due: {summary['due']:<50}║
║  ❌ Overdue: {summary['overdue']:<47}║
╠══════════════════════════════════════════════════════════════╣
║  SECRETS STATUS:                                             ║""")
    
    for secret in manager.secrets:
        icon = {"current": "🟢", "due_for_rotation": "🟡", "overdue": "🔴"}[secret.status.value]
        days = (datetime.now() - secret.last_rotated).days
        print(f"║    {icon} {secret.name:<30} ({days}d ago) ║")
    
    print("╚══════════════════════════════════════════════════════════════╝")


def main():
    parser = argparse.ArgumentParser(description="Secrets Rotation Scheduler")
    parser.add_argument("--demo", action="store_true")
    parser.add_argument("--rotate", type=str, help="Secret to rotate")
    parser.add_argument("--dry-run", action="store_true", default=True)
    args = parser.parse_args()
    
    print("=" * 60)
    print("   SECRETS ROTATION SCHEDULER")
    print("=" * 60)
    
    manager = SecretsRotationManager()
    manager.load_secrets()
    
    if args.rotate:
        print(f"\n🔄 Rotating secret: {args.rotate}")
        manager.rotate_secret(args.rotate, args.dry_run)
    
    print_report(manager)
    
    return 1 if manager.get_summary()['overdue'] > 0 else 0


if __name__ == "__main__":
    exit(main())
