#!/usr/bin/env python3
"""
================================================================================
RELEASE FREEZE ENFORCER
================================================================================

RESUME BULLET POINT:
"Built a release freeze enforcer that blocks deployments during incidents or 
high-risk windows, reducing change-related outages."

DESCRIPTION:
Prevents deployments during defined freeze periods (incidents, holidays, 
maintenance windows) with override capabilities for emergencies.

Author: DevOps Engineer | Version: 1.0.0
================================================================================
"""

import argparse
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class FreezeType(Enum):
    INCIDENT = "incident"
    HOLIDAY = "holiday"
    MAINTENANCE = "maintenance"
    MANUAL = "manual"


class FreezeStatus(Enum):
    ACTIVE = "active"
    SCHEDULED = "scheduled"
    EXPIRED = "expired"


@dataclass
class FreezeWindow:
    """Represents a deployment freeze window"""
    id: str
    freeze_type: FreezeType
    reason: str
    start_time: datetime
    end_time: datetime
    created_by: str
    environments: List[str]
    allow_emergency: bool = True


@dataclass
class DeploymentRequest:
    """Incoming deployment request"""
    service: str
    version: str
    environment: str
    requester: str
    is_emergency: bool = False


class FreezeManager:
    """Manages deployment freeze windows"""
    
    def __init__(self):
        self.freeze_windows: List[FreezeWindow] = []
        self.blocked_deployments: List[Dict] = []
        self.overridden_deployments: List[Dict] = []
    
    def add_freeze(self, freeze: FreezeWindow):
        """Add a freeze window"""
        self.freeze_windows.append(freeze)
        print(f"   🔒 Added freeze: {freeze.reason}")
    
    def get_active_freezes(self, environment: str = None) -> List[FreezeWindow]:
        """Get currently active freeze windows"""
        now = datetime.now()
        active = []
        
        for freeze in self.freeze_windows:
            if freeze.start_time <= now <= freeze.end_time:
                if environment is None or environment in freeze.environments:
                    active.append(freeze)
        
        return active
    
    def check_deployment(self, request: DeploymentRequest) -> tuple:
        """
        Check if deployment is allowed.
        Returns (allowed: bool, reason: str, freeze: FreezeWindow or None)
        """
        active_freezes = self.get_active_freezes(request.environment)
        
        if not active_freezes:
            return True, "No active freeze windows", None
        
        # Check if emergency override is allowed
        for freeze in active_freezes:
            if request.is_emergency and freeze.allow_emergency:
                self.overridden_deployments.append({
                    "request": request,
                    "freeze": freeze,
                    "timestamp": datetime.now(),
                })
                return True, f"Emergency override for freeze: {freeze.reason}", freeze
            
            self.blocked_deployments.append({
                "request": request,
                "freeze": freeze,
                "timestamp": datetime.now(),
            })
            return False, f"Blocked by freeze: {freeze.reason}", freeze
        
        return True, "Allowed", None
    
    def get_status(self) -> Dict:
        """Get current freeze status"""
        now = datetime.now()
        active = [f for f in self.freeze_windows if f.start_time <= now <= f.end_time]
        scheduled = [f for f in self.freeze_windows if f.start_time > now]
        
        return {
            "active_freezes": len(active),
            "scheduled_freezes": len(scheduled),
            "blocked_deployments": len(self.blocked_deployments),
            "overridden_deployments": len(self.overridden_deployments),
            "production_frozen": any("production" in f.environments for f in active),
        }


def create_demo_freezes() -> List[FreezeWindow]:
    """Create demo freeze windows"""
    now = datetime.now()
    
    return [
        FreezeWindow(
            id="FREEZE-001",
            freeze_type=FreezeType.INCIDENT,
            reason="Ongoing production incident - SEV1",
            start_time=now - timedelta(hours=2),
            end_time=now + timedelta(hours=4),
            created_by="oncall@company.com",
            environments=["production", "staging"],
        ),
        FreezeWindow(
            id="FREEZE-002",
            freeze_type=FreezeType.HOLIDAY,
            reason="Holiday code freeze",
            start_time=now + timedelta(days=5),
            end_time=now + timedelta(days=12),
            created_by="platform-team",
            environments=["production"],
        ),
    ]


def print_status(manager: FreezeManager):
    """Print freeze status"""
    status = manager.get_status()
    active = manager.get_active_freezes()
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║              RELEASE FREEZE ENFORCER STATUS                  ║
╠══════════════════════════════════════════════════════════════╣
║  Active Freezes: {status['active_freezes']:<42}║
║  Scheduled Freezes: {status['scheduled_freezes']:<39}║
║  Production Frozen: {'YES 🔒' if status['production_frozen'] else 'NO 🟢':<39}║
╠══════════════════════════════════════════════════════════════╣
║  DEPLOYMENT STATS:                                           ║
║    Blocked: {status['blocked_deployments']:<48}║
║    Emergency Overrides: {status['overridden_deployments']:<35}║
╠══════════════════════════════════════════════════════════════╣
║  ACTIVE FREEZE WINDOWS:                                      ║""")
    
    if active:
        for freeze in active:
            remaining = freeze.end_time - datetime.now()
            hours = remaining.total_seconds() / 3600
            print(f"║    🔒 {freeze.reason:<40} ({hours:.1f}h) ║")
    else:
        print(f"║    ✅ No active freezes - deployments allowed{' ':<15}║")
    
    print("╚══════════════════════════════════════════════════════════════╝")


def main():
    parser = argparse.ArgumentParser(description="Release Freeze Enforcer")
    parser.add_argument("--demo", action="store_true", help="Run demo")
    parser.add_argument("--check", action="store_true", help="Check if deployment allowed")
    parser.add_argument("--service", type=str, default="api-service")
    parser.add_argument("--env", type=str, default="production")
    parser.add_argument("--emergency", action="store_true", help="Mark as emergency")
    parser.add_argument("--status", action="store_true", help="Show status")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("   RELEASE FREEZE ENFORCER")
    print("=" * 60)
    
    manager = FreezeManager()
    
    # Load demo freezes
    print("\n📋 Loading freeze windows...")
    for freeze in create_demo_freezes():
        manager.add_freeze(freeze)
    
    if args.check:
        print(f"\n🔍 Checking deployment: {args.service} → {args.env}")
        request = DeploymentRequest(
            service=args.service,
            version="v2.0.0",
            environment=args.env,
            requester="developer@company.com",
            is_emergency=args.emergency,
        )
        
        allowed, reason, freeze = manager.check_deployment(request)
        
        if allowed:
            print(f"   ✅ ALLOWED: {reason}")
        else:
            print(f"   ❌ BLOCKED: {reason}")
            if freeze:
                print(f"      Freeze ends: {freeze.end_time}")
                if freeze.allow_emergency:
                    print("      💡 Use --emergency flag to override")
    
    print_status(manager)
    return 0


if __name__ == "__main__":
    exit(main())
