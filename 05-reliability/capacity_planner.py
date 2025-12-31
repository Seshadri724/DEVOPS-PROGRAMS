#!/usr/bin/env python3
"""
================================================================================
CAPACITY PLANNING CALCULATOR
================================================================================

RESUME BULLET POINT:
"Built a capacity planning calculator that forecasts resource needs based 
on growth trends, enabling proactive infrastructure scaling."

Author: DevOps Engineer | Version: 1.0.0
================================================================================
"""

import argparse
import json
from datetime import datetime, timedelta
from typing import Dict, List
from dataclasses import dataclass
import math


@dataclass
class ResourceUsage:
    """Historical resource usage data"""
    date: datetime
    cpu_percent: float
    memory_percent: float
    requests_per_second: int


@dataclass
class CapacityForecast:
    """Capacity forecast result"""
    resource: str
    current_usage: float
    growth_rate_monthly: float
    days_until_80_pct: int
    days_until_100_pct: int
    recommended_scale_date: datetime


class CapacityPlanner:
    """Plans capacity based on usage trends"""
    
    def __init__(self):
        self.history: List[ResourceUsage] = []
        self.forecasts: List[CapacityForecast] = []
    
    def load_history(self) -> List[ResourceUsage]:
        """Load usage history (simulated)"""
        now = datetime.now()
        
        # Simulate 30 days of growing usage
        for days_ago in range(30, 0, -1):
            growth_factor = 1 + (30 - days_ago) * 0.015  # 1.5% daily growth
            self.history.append(ResourceUsage(
                date=now - timedelta(days=days_ago),
                cpu_percent=40 * growth_factor,
                memory_percent=50 * growth_factor,
                requests_per_second=int(1000 * growth_factor),
            ))
        
        return self.history
    
    def calculate_growth_rate(self, metric: str) -> float:
        """Calculate monthly growth rate for a metric"""
        if len(self.history) < 2:
            return 0
        
        first = getattr(self.history[0], metric)
        last = getattr(self.history[-1], metric)
        days = (self.history[-1].date - self.history[0].date).days
        
        if first == 0 or days == 0:
            return 0
        
        daily_rate = (last / first) ** (1 / days) - 1
        monthly_rate = (1 + daily_rate) ** 30 - 1
        return monthly_rate * 100
    
    def forecast_resource(self, name: str, current: float, growth_rate: float) -> CapacityForecast:
        """Forecast when resource will hit thresholds"""
        if growth_rate <= 0:
            return CapacityForecast(name, current, 0, 999, 999, datetime.now() + timedelta(days=365))
        
        daily_rate = (1 + growth_rate / 100) ** (1 / 30) - 1
        
        days_to_80 = math.log(80 / current) / math.log(1 + daily_rate) if current < 80 else 0
        days_to_100 = math.log(100 / current) / math.log(1 + daily_rate) if current < 100 else 0
        
        return CapacityForecast(
            resource=name,
            current_usage=current,
            growth_rate_monthly=growth_rate,
            days_until_80_pct=int(max(0, days_to_80)),
            days_until_100_pct=int(max(0, days_to_100)),
            recommended_scale_date=datetime.now() + timedelta(days=max(0, days_to_80 - 7)),
        )
    
    def run_forecast(self) -> List[CapacityForecast]:
        """Run capacity forecast"""
        print("\n📊 Calculating forecasts...")
        
        cpu_growth = self.calculate_growth_rate('cpu_percent')
        mem_growth = self.calculate_growth_rate('memory_percent')
        rps_growth = self.calculate_growth_rate('requests_per_second')
        
        current = self.history[-1]
        
        self.forecasts = [
            self.forecast_resource("CPU", current.cpu_percent, cpu_growth),
            self.forecast_resource("Memory", current.memory_percent, mem_growth),
            self.forecast_resource("Traffic (RPS)", current.requests_per_second / 50, rps_growth),  # Normalized
        ]
        
        return self.forecasts
    
    def get_recommendations(self) -> List[str]:
        """Get scaling recommendations"""
        recommendations = []
        
        for forecast in self.forecasts:
            if forecast.days_until_80_pct < 14:
                recommendations.append(f"⚠️ {forecast.resource}: Scale within {forecast.days_until_80_pct} days")
            elif forecast.days_until_80_pct < 30:
                recommendations.append(f"📅 {forecast.resource}: Plan scaling in next month")
        
        return recommendations


def print_report(planner: CapacityPlanner):
    """Print capacity report"""
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║           CAPACITY PLANNING REPORT                           ║
╠══════════════════════════════════════════════════════════════╣
║  Analysis Period: {len(planner.history)} days{' ':<39}║
╠══════════════════════════════════════════════════════════════╣
║  RESOURCE FORECASTS:                                         ║""")
    
    for f in planner.forecasts:
        status = "🔴" if f.days_until_80_pct < 14 else "🟡" if f.days_until_80_pct < 30 else "🟢"
        print(f"║    {status} {f.resource:<15} {f.current_usage:>5.1f}%  +{f.growth_rate_monthly:.1f}%/mo  {f.days_until_80_pct:>3}d to 80% ║")
    
    print(f"""╠══════════════════════════════════════════════════════════════╣
║  RECOMMENDATIONS:                                            ║""")
    
    for rec in planner.get_recommendations():
        print(f"║    {rec:<55}║")
    
    if not planner.get_recommendations():
        print(f"║    ✅ No immediate scaling needed{' ':<26}║")
    
    print("╚══════════════════════════════════════════════════════════════╝")


def main():
    parser = argparse.ArgumentParser(description="Capacity Planning Calculator")
    parser.add_argument("--demo", action="store_true")
    parser.add_argument("--output", type=str)
    args = parser.parse_args()
    
    print("=" * 60)
    print("   CAPACITY PLANNING CALCULATOR")
    print("=" * 60)
    
    planner = CapacityPlanner()
    planner.load_history()
    planner.run_forecast()
    
    print_report(planner)
    
    return 0


if __name__ == "__main__":
    exit(main())
