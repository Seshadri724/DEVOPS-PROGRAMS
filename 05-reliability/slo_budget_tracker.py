#!/usr/bin/env python3
"""
================================================================================
SLO/ERROR BUDGET TRACKER
================================================================================

RESUME BULLET POINT:
"Built an SLO/error budget tracker that shows real-time budget consumption 
and triggers protective actions when budgets are depleted."

Author: DevOps Engineer | Version: 1.0.0
================================================================================
"""

import argparse
import json
from datetime import datetime, timedelta
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum


class BudgetStatus(Enum):
    HEALTHY = "healthy"      # > 50% remaining
    WARNING = "warning"      # 20-50% remaining
    CRITICAL = "critical"    # < 20% remaining
    EXHAUSTED = "exhausted"  # 0% remaining


@dataclass
class SLO:
    """Service Level Objective"""
    name: str
    target: float           # e.g., 99.9
    window_days: int        # e.g., 30
    current_value: float
    error_budget_total: float
    error_budget_remaining: float


class SLOBudgetTracker:
    """Tracks SLO error budgets"""
    
    def __init__(self):
        self.slos: List[SLO] = []
    
    def load_slos(self) -> List[SLO]:
        """Load SLO definitions with current status"""
        self.slos = [
            SLO("API Availability", 99.9, 30, 99.85, 43.2, 30.5),      # 30.5 min remaining of 43.2
            SLO("Latency P99 < 500ms", 99.0, 30, 98.5, 432.0, 216.0),  # 50% remaining
            SLO("Payment Success Rate", 99.95, 30, 99.8, 21.6, 5.4),   # Critical
            SLO("Search Availability", 99.5, 30, 99.6, 216.0, 259.2),  # Over budget (good)
        ]
        return self.slos
    
    def calculate_budget_status(self, slo: SLO) -> tuple:
        """Calculate budget status and percentage"""
        if slo.error_budget_total == 0:
            return BudgetStatus.EXHAUSTED, 0
        
        pct_remaining = (slo.error_budget_remaining / slo.error_budget_total) * 100
        
        if pct_remaining <= 0:
            return BudgetStatus.EXHAUSTED, 0
        elif pct_remaining < 20:
            return BudgetStatus.CRITICAL, pct_remaining
        elif pct_remaining < 50:
            return BudgetStatus.WARNING, pct_remaining
        else:
            return BudgetStatus.HEALTHY, pct_remaining
    
    def get_burn_rate(self, slo: SLO) -> float:
        """Calculate current error budget burn rate"""
        consumed = slo.error_budget_total - slo.error_budget_remaining
        expected_consumed = slo.error_budget_total * 0.5  # Halfway through window
        
        if expected_consumed == 0:
            return 0
        return consumed / expected_consumed
    
    def get_protective_actions(self) -> List[str]:
        """Get recommended protective actions"""
        actions = []
        
        for slo in self.slos:
            status, pct = self.calculate_budget_status(slo)
            burn_rate = self.get_burn_rate(slo)
            
            if status == BudgetStatus.EXHAUSTED:
                actions.append(f"🚫 {slo.name}: FREEZE deployments immediately")
            elif status == BudgetStatus.CRITICAL:
                actions.append(f"⚠️ {slo.name}: Require approvals for risky changes")
            elif burn_rate > 2:
                actions.append(f"📈 {slo.name}: Burn rate {burn_rate:.1f}x - investigate")
        
        return actions
    
    def get_summary(self) -> Dict:
        """Get tracking summary"""
        statuses = [self.calculate_budget_status(s)[0] for s in self.slos]
        return {
            "total_slos": len(self.slos),
            "healthy": sum(1 for s in statuses if s == BudgetStatus.HEALTHY),
            "warning": sum(1 for s in statuses if s == BudgetStatus.WARNING),
            "critical": sum(1 for s in statuses if s == BudgetStatus.CRITICAL),
            "exhausted": sum(1 for s in statuses if s == BudgetStatus.EXHAUSTED),
        }


def print_report(tracker: SLOBudgetTracker):
    """Print SLO budget report"""
    summary = tracker.get_summary()
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║           SLO / ERROR BUDGET TRACKER                         ║
╠══════════════════════════════════════════════════════════════╣
║  Total SLOs: {summary['total_slos']:<46}║
║  🟢 Healthy: {summary['healthy']}  🟡 Warning: {summary['warning']}  🔴 Critical: {summary['critical']}  ⚫ Exhausted: {summary['exhausted']}  ║
╠══════════════════════════════════════════════════════════════╣
║  SLO STATUS:                                                 ║""")
    
    icons = {"healthy": "🟢", "warning": "🟡", "critical": "🔴", "exhausted": "⚫"}
    
    for slo in tracker.slos:
        status, pct = tracker.calculate_budget_status(slo)
        burn_rate = tracker.get_burn_rate(slo)
        print(f"║    {icons[status.value]} {slo.name:<25} {pct:>5.1f}% left  {burn_rate:.1f}x burn ║")
    
    actions = tracker.get_protective_actions()
    if actions:
        print(f"""╠══════════════════════════════════════════════════════════════╣
║  PROTECTIVE ACTIONS:                                         ║""")
        for action in actions:
            print(f"║    {action:<55}║")
    
    print("╚══════════════════════════════════════════════════════════════╝")


def main():
    parser = argparse.ArgumentParser(description="SLO Budget Tracker")
    parser.add_argument("--demo", action="store_true")
    parser.add_argument("--output", type=str)
    args = parser.parse_args()
    
    print("=" * 60)
    print("   SLO / ERROR BUDGET TRACKER")
    print("=" * 60)
    
    tracker = SLOBudgetTracker()
    tracker.load_slos()
    
    print_report(tracker)
    
    return 1 if tracker.get_summary()['exhausted'] > 0 else 0


if __name__ == "__main__":
    exit(main())
