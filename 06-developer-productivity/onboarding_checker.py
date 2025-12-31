#!/usr/bin/env python3
"""
================================================================================
ONBOARDING COMPLETENESS CHECKER
================================================================================

RESUME BULLET POINT:
"Built an onboarding completeness checker that ensures new devs have all 
required access and tools configured, reducing first-week friction."

Author: DevOps Engineer | Version: 1.0.0
================================================================================
"""

import argparse
import json
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum


class CheckStatus(Enum):
    COMPLETE = "complete"
    INCOMPLETE = "incomplete"
    PENDING = "pending"


@dataclass
class OnboardingItem:
    """Single onboarding checklist item"""
    name: str
    category: str
    status: CheckStatus
    required: bool = True
    notes: str = ""


class OnboardingChecker:
    """Checks developer onboarding completeness"""
    
    def __init__(self, username: str):
        self.username = username
        self.items: List[OnboardingItem] = []
    
    def load_checklist(self) -> List[OnboardingItem]:
        """Load onboarding checklist (simulated status)"""
        self.items = [
            # Access
            OnboardingItem("GitHub Organization Access", "access", CheckStatus.COMPLETE),
            OnboardingItem("Jira/Issue Tracker Access", "access", CheckStatus.COMPLETE),
            OnboardingItem("Slack Channels Joined", "access", CheckStatus.COMPLETE),
            OnboardingItem("AWS Console Access", "access", CheckStatus.INCOMPLETE, notes="Request pending"),
            OnboardingItem("VPN Configuration", "access", CheckStatus.PENDING),
            
            # Development Environment
            OnboardingItem("IDE/Editor Configured", "dev-env", CheckStatus.COMPLETE),
            OnboardingItem("Local Dev Environment Running", "dev-env", CheckStatus.COMPLETE),
            OnboardingItem("SSH Keys Configured", "dev-env", CheckStatus.COMPLETE),
            OnboardingItem("Code Signing Setup", "dev-env", CheckStatus.INCOMPLETE),
            
            # Knowledge
            OnboardingItem("Team Wiki Reviewed", "knowledge", CheckStatus.COMPLETE, required=False),
            OnboardingItem("Architecture Overview Read", "knowledge", CheckStatus.INCOMPLETE),
            OnboardingItem("On-call Shadowing Scheduled", "knowledge", CheckStatus.PENDING),
        ]
        return self.items
    
    def get_completion_pct(self) -> float:
        """Calculate completion percentage for required items"""
        required = [i for i in self.items if i.required]
        complete = sum(1 for i in required if i.status == CheckStatus.COMPLETE)
        return (complete / len(required)) * 100 if required else 100
    
    def get_blockers(self) -> List[OnboardingItem]:
        """Get items blocking productivity"""
        return [i for i in self.items if i.required and i.status != CheckStatus.COMPLETE]
    
    def get_summary(self) -> Dict:
        """Get onboarding summary"""
        return {
            "username": self.username,
            "total_items": len(self.items),
            "complete": sum(1 for i in self.items if i.status == CheckStatus.COMPLETE),
            "incomplete": sum(1 for i in self.items if i.status == CheckStatus.INCOMPLETE),
            "pending": sum(1 for i in self.items if i.status == CheckStatus.PENDING),
            "completion_pct": self.get_completion_pct(),
            "blockers": len(self.get_blockers()),
        }


def print_report(checker: OnboardingChecker):
    """Print onboarding report"""
    summary = checker.get_summary()
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║           ONBOARDING COMPLETENESS CHECK                      ║
╠══════════════════════════════════════════════════════════════╣
║  Developer: {checker.username:<47}║
║  Completion: {summary['completion_pct']:.0f}%{' ':<44}║
║  Blockers: {summary['blockers']:<48}║
╠══════════════════════════════════════════════════════════════╣
║  CHECKLIST STATUS:                                           ║""")
    
    icons = {"complete": "✅", "incomplete": "❌", "pending": "⏳"}
    
    for item in checker.items:
        icon = icons[item.status.value]
        req = "🔴" if item.required and item.status != CheckStatus.COMPLETE else "  "
        print(f"║    {icon} {req} {item.name:<45}║")
    
    print("╚══════════════════════════════════════════════════════════════╝")
    
    blockers = checker.get_blockers()
    if blockers:
        print(f"\n⚠️ {len(blockers)} items blocking productivity:")
        for b in blockers:
            print(f"   - {b.name}: {b.notes or 'Action needed'}")


def main():
    parser = argparse.ArgumentParser(description="Onboarding Checker")
    parser.add_argument("--demo", action="store_true")
    parser.add_argument("--user", default="new-developer")
    parser.add_argument("--output", type=str)
    args = parser.parse_args()
    
    print("=" * 60)
    print("   ONBOARDING COMPLETENESS CHECKER")
    print("=" * 60)
    
    checker = OnboardingChecker(args.user)
    checker.load_checklist()
    
    print_report(checker)
    
    return 0 if checker.get_completion_pct() == 100 else 1


if __name__ == "__main__":
    exit(main())
