#!/usr/bin/env python3
"""
================================================================================
SERVICE HEALTH AGGREGATION TOOL
================================================================================

RESUME BULLET POINT:
"Built a service health aggregation tool that unified metrics into a single 
operational view for faster incident triage."

DESCRIPTION:
Aggregates health status from multiple services into a unified dashboard view,
enabling quick identification of system-wide issues.

Author: DevOps Engineer | Version: 1.0.0
================================================================================
"""

import argparse
import json
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum
import random


class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ServiceHealth:
    """Health status of a single service"""
    name: str
    status: HealthStatus
    latency_ms: float
    error_rate: float
    uptime_pct: float
    last_check: datetime
    dependencies: List[str]


@dataclass
class SystemHealth:
    """Aggregated system health"""
    overall_status: HealthStatus
    services: List[ServiceHealth]
    healthy_count: int
    degraded_count: int
    unhealthy_count: int


class HealthAggregator:
    """Collects and aggregates service health"""
    
    def __init__(self):
        self.services: List[ServiceHealth] = []
    
    def collect_health(self) -> List[ServiceHealth]:
        """Collect health from all services (simulated)"""
        service_defs = [
            ("api-gateway", ["auth", "users"]),
            ("auth", ["redis", "postgres"]),
            ("users", ["postgres"]),
            ("orders", ["postgres", "payment"]),
            ("payment", ["stripe-api"]),
            ("notifications", ["redis", "email-service"]),
            ("postgres", []),
            ("redis", []),
        ]
        
        for name, deps in service_defs:
            status = random.choices(
                [HealthStatus.HEALTHY, HealthStatus.DEGRADED, HealthStatus.UNHEALTHY],
                weights=[0.7, 0.2, 0.1]
            )[0]
            
            self.services.append(ServiceHealth(
                name=name,
                status=status,
                latency_ms=random.uniform(10, 500) if status != HealthStatus.UNHEALTHY else random.uniform(1000, 5000),
                error_rate=random.uniform(0, 1) if status == HealthStatus.HEALTHY else random.uniform(1, 20),
                uptime_pct=random.uniform(99, 100) if status == HealthStatus.HEALTHY else random.uniform(90, 99),
                last_check=datetime.now(),
                dependencies=deps,
            ))
        
        return self.services
    
    def get_system_health(self) -> SystemHealth:
        """Calculate overall system health"""
        healthy = sum(1 for s in self.services if s.status == HealthStatus.HEALTHY)
        degraded = sum(1 for s in self.services if s.status == HealthStatus.DEGRADED)
        unhealthy = sum(1 for s in self.services if s.status == HealthStatus.UNHEALTHY)
        
        if unhealthy > 0:
            overall = HealthStatus.UNHEALTHY
        elif degraded > 0:
            overall = HealthStatus.DEGRADED
        else:
            overall = HealthStatus.HEALTHY
        
        return SystemHealth(
            overall_status=overall,
            services=self.services,
            healthy_count=healthy,
            degraded_count=degraded,
            unhealthy_count=unhealthy,
        )
    
    def get_dependency_impact(self, service_name: str) -> List[str]:
        """Find services that depend on the given service"""
        impacted = []
        for service in self.services:
            if service_name in service.dependencies:
                impacted.append(service.name)
        return impacted


def print_dashboard(system_health: SystemHealth, aggregator: HealthAggregator):
    """Print health dashboard"""
    status_icons = {"healthy": "🟢", "degraded": "🟡", "unhealthy": "🔴", "unknown": "⚪"}
    overall_icon = status_icons[system_health.overall_status.value]
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║              SERVICE HEALTH DASHBOARD                        ║
╠══════════════════════════════════════════════════════════════╣
║  Overall Status: {overall_icon} {system_health.overall_status.value.upper():<42}║
║  Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S'):<44}║
╠══════════════════════════════════════════════════════════════╣
║  SUMMARY:                                                    ║
║    🟢 Healthy:   {system_health.healthy_count:<43}║
║    🟡 Degraded:  {system_health.degraded_count:<43}║
║    🔴 Unhealthy: {system_health.unhealthy_count:<43}║
╠══════════════════════════════════════════════════════════════╣
║  SERVICE STATUS:                                             ║""")
    
    for svc in sorted(system_health.services, key=lambda x: x.status.value):
        icon = status_icons[svc.status.value]
        print(f"║    {icon} {svc.name:<20} {svc.latency_ms:>6.0f}ms  {svc.error_rate:>5.2f}% err  ║")
    
    # Show impacted services if any unhealthy
    unhealthy = [s for s in system_health.services if s.status == HealthStatus.UNHEALTHY]
    if unhealthy:
        print(f"╠══════════════════════════════════════════════════════════════╣")
        print(f"║  ⚠️  IMPACT ANALYSIS:                                         ║")
        for svc in unhealthy:
            impacted = aggregator.get_dependency_impact(svc.name)
            if impacted:
                print(f"║    {svc.name} outage impacts: {', '.join(impacted):<30}║")
    
    print("╚══════════════════════════════════════════════════════════════╝")


def main():
    parser = argparse.ArgumentParser(description="Service Health Aggregator")
    parser.add_argument("--demo", action="store_true", help="Run demo")
    parser.add_argument("--output", type=str, help="JSON output file")
    parser.add_argument("--watch", action="store_true", help="Continuous monitoring")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("   SERVICE HEALTH AGGREGATION TOOL")
    print("=" * 60)
    
    aggregator = HealthAggregator()
    
    print("\n📡 Collecting health from services...")
    aggregator.collect_health()
    
    system_health = aggregator.get_system_health()
    print_dashboard(system_health, aggregator)
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump({
                "overall": system_health.overall_status.value,
                "services": [{"name": s.name, "status": s.status.value, 
                             "latency_ms": s.latency_ms, "error_rate": s.error_rate}
                            for s in system_health.services]
            }, f, indent=2)
        print(f"\n📄 Report saved to: {args.output}")
    
    return 0 if system_health.overall_status == HealthStatus.HEALTHY else 1


if __name__ == "__main__":
    exit(main())
