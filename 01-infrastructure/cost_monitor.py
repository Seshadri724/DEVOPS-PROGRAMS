#!/usr/bin/env python3
"""
================================================================================
AUTOMATED CLOUD COST MONITORING & BUDGET ALERTS
================================================================================

RESUME BULLET POINT:
"Implemented automated cloud cost monitoring and budget alerts, preventing 
unexpected monthly bill overruns and improving financial predictability."

DESCRIPTION:
Real-time cloud cost monitoring with intelligent alerting. Tracks spending,
detects anomalies, forecasts costs, and sends proactive budget alerts.

Author: DevOps Engineer | Version: 1.0.0
================================================================================
"""

import json
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
import random
import math


class AlertSeverity(Enum):
    INFO = "info"           # 50% threshold
    WARNING = "warning"     # 75% threshold
    CRITICAL = "critical"   # 90% threshold
    EMERGENCY = "emergency" # 100%+ threshold


@dataclass
class DailyCost:
    """Daily cost data with service breakdown"""
    date: datetime
    total: float
    by_service: Dict[str, float] = field(default_factory=dict)


@dataclass
class Budget:
    """Budget configuration"""
    name: str
    amount: float
    period: str  # "monthly", "weekly", "daily"
    owner_email: str
    slack_channel: str = None


@dataclass
class CostAlert:
    """Cost alert notification"""
    budget: Budget
    severity: AlertSeverity
    current_spend: float
    percentage: float
    forecast: float
    message: str


class CostDataSimulator:
    """Simulates cloud cost data (replace with real APIs in production)"""
    
    @staticmethod
    def generate_costs(days: int = 30, base_cost: float = 500) -> List[DailyCost]:
        """Generate realistic historical cost data"""
        costs = []
        services = ["ec2", "rds", "s3", "eks", "lambda", "cloudwatch"]
        
        for i in range(days, 0, -1):
            date = datetime.now() - timedelta(days=i)
            # Weekend adjustment + variance + occasional spikes
            factor = 0.6 if date.weekday() >= 5 else 1.0
            variance = random.uniform(0.85, 1.15)
            spike = 2.0 if random.random() < 0.1 else 1.0
            
            total = base_cost * factor * variance * spike
            by_service = {s: total * random.uniform(0.1, 0.3) for s in services}
            
            costs.append(DailyCost(date=date, total=total, by_service=by_service))
        return costs


class CostAnalyzer:
    """Analyzes cost data for trends and forecasting"""
    
    def __init__(self, costs: List[DailyCost]):
        self.costs = costs
    
    def get_period_spend(self, period: str) -> float:
        """Get spend for current period"""
        today = datetime.now()
        if period == "daily":
            return self.costs[-1].total if self.costs else 0
        elif period == "weekly":
            cutoff = today - timedelta(days=7)
            return sum(c.total for c in self.costs if c.date >= cutoff)
        else:  # monthly
            cutoff = today.replace(day=1)
            return sum(c.total for c in self.costs if c.date >= cutoff)
    
    def forecast_eom(self) -> Tuple[float, float]:
        """Forecast end-of-month spend"""
        today = datetime.now()
        days_elapsed = today.day
        current = self.get_period_spend("monthly")
        
        if days_elapsed == 0:
            return 0, 0
        
        daily_rate = current / days_elapsed
        forecast = current + (daily_rate * (30 - days_elapsed))
        confidence = min(95, 50 + (days_elapsed / 30) * 50)
        return round(forecast, 2), round(confidence, 1)
    
    def detect_anomalies(self) -> List[DailyCost]:
        """Detect cost spikes using z-score"""
        if len(self.costs) < 7:
            return []
        
        totals = [c.total for c in self.costs]
        mean = sum(totals) / len(totals)
        std = math.sqrt(sum((x - mean)**2 for x in totals) / len(totals))
        
        if std == 0:
            return []
        return [c for c in self.costs if (c.total - mean) / std > 2.0]
    
    def get_trend(self) -> str:
        """Determine cost trend"""
        if len(self.costs) < 14:
            return "insufficient_data"
        
        recent = sum(c.total for c in self.costs[-7:]) / 7
        previous = sum(c.total for c in self.costs[-14:-7]) / 7
        change = ((recent - previous) / previous) * 100
        
        if change > 10:
            return f"📈 increasing (+{change:.1f}%)"
        elif change < -10:
            return f"📉 decreasing ({change:.1f}%)"
        return f"➡️ stable ({change:+.1f}%)"


class BudgetManager:
    """Manages budget tracking and alerts"""
    
    def __init__(self):
        self.budgets: List[Budget] = []
    
    def add_budget(self, budget: Budget):
        self.budgets.append(budget)
    
    def check_budgets(self, analyzer: CostAnalyzer) -> List[CostAlert]:
        """Check all budgets and generate alerts"""
        alerts = []
        
        for budget in self.budgets:
            spend = analyzer.get_period_spend(budget.period)
            pct = (spend / budget.amount) * 100
            forecast, _ = analyzer.forecast_eom()
            
            severity = None
            if pct >= 100:
                severity = AlertSeverity.EMERGENCY
            elif pct >= 90:
                severity = AlertSeverity.CRITICAL
            elif pct >= 75:
                severity = AlertSeverity.WARNING
            elif pct >= 50:
                severity = AlertSeverity.INFO
            
            if severity:
                emoji = {"info": "ℹ️", "warning": "⚠️", 
                        "critical": "🚨", "emergency": "🔥"}[severity.value]
                msg = f"{emoji} {budget.name}: ${spend:,.2f} ({pct:.1f}% of ${budget.amount:,.2f})"
                
                alerts.append(CostAlert(
                    budget=budget, severity=severity,
                    current_spend=spend, percentage=pct,
                    forecast=forecast, message=msg
                ))
        return alerts


def print_report(analyzer: CostAnalyzer, alerts: List[CostAlert]):
    """Print cost monitoring report"""
    forecast, conf = analyzer.forecast_eom()
    
    print("\n" + "=" * 60)
    print("   CLOUD COST MONITORING REPORT")
    print("=" * 60)
    print(f"\n📊 CURRENT SPEND:")
    print(f"   Today:      ${analyzer.get_period_spend('daily'):>10,.2f}")
    print(f"   This Week:  ${analyzer.get_period_spend('weekly'):>10,.2f}")
    print(f"   This Month: ${analyzer.get_period_spend('monthly'):>10,.2f}")
    
    print(f"\n📈 FORECAST:")
    print(f"   End-of-Month: ${forecast:>10,.2f} ({conf}% confidence)")
    print(f"   Trend: {analyzer.get_trend()}")
    
    anomalies = analyzer.detect_anomalies()
    if anomalies:
        print(f"\n⚠️ ANOMALIES DETECTED: {len(anomalies)} days with unusual spending")
        for a in anomalies[:3]:
            print(f"   {a.date.strftime('%Y-%m-%d')}: ${a.total:,.2f}")
    
    if alerts:
        print(f"\n🔔 ALERTS ({len(alerts)}):")
        for alert in alerts:
            print(f"   {alert.message}")
    else:
        print("\n✅ All budgets within thresholds")
    
    print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Cloud Cost Monitoring & Budget Alerts")
    parser.add_argument("--demo", action="store_true", help="Run with simulated data")
    parser.add_argument("--budget", type=float, default=15000, help="Monthly budget")
    parser.add_argument("--output", type=str, help="JSON output file")
    parser.add_argument("--days", type=int, default=30, help="Days of history")
    args = parser.parse_args()
    
    print("\n🔍 Loading cost data...")
    costs = CostDataSimulator.generate_costs(args.days, args.budget / 30)
    analyzer = CostAnalyzer(costs)
    
    # Configure budget
    manager = BudgetManager()
    manager.add_budget(Budget(
        name="Production Cloud Spend",
        amount=args.budget,
        period="monthly",
        owner_email="platform@company.com"
    ))
    
    # Check and alert
    alerts = manager.check_budgets(analyzer)
    print_report(analyzer, alerts)
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump({
                "monthly_spend": analyzer.get_period_spend("monthly"),
                "forecast": analyzer.forecast_eom()[0],
                "alerts": len(alerts)
            }, f, indent=2)
        print(f"📄 Exported to: {args.output}")
    
    return 1 if any(a.severity in [AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY] 
                   for a in alerts) else 0


if __name__ == "__main__":
    exit(main())
