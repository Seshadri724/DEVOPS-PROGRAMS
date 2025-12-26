#!/usr/bin/env python3
"""
================================================================================
GOLDEN SIGNAL MONITOR GENERATOR
================================================================================

RESUME BULLET POINT:
"Built a golden signal monitor generator that auto-creates latency, error, 
traffic, and saturation dashboards per service, enabling consistent observability."

DESCRIPTION:
Automatically generates monitoring configurations for the four golden signals
(Latency, Errors, Traffic, Saturation) based on service metadata.

Author: DevOps Engineer | Version: 1.0.0
================================================================================
"""

import argparse
import json
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class ServiceMetadata:
    """Service metadata for monitor generation"""
    name: str
    type: str  # api, worker, database
    slo_latency_ms: int
    slo_error_rate: float
    slo_availability: float


@dataclass
class Monitor:
    """Generated monitor configuration"""
    name: str
    signal: str  # latency, errors, traffic, saturation
    query: str
    threshold: float
    severity: str


class GoldenSignalGenerator:
    """Generates golden signal monitors for services"""
    
    # Prometheus query templates per signal
    QUERY_TEMPLATES = {
        "latency": 'histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket{{service="{svc}"}}[5m])) by (le)) * 1000',
        "errors": 'sum(rate(http_requests_total{{service="{svc}", status=~"5.."}}[5m])) / sum(rate(http_requests_total{{service="{svc}"}}[5m])) * 100',
        "traffic": 'sum(rate(http_requests_total{{service="{svc}"}}[5m]))',
        "saturation_cpu": 'avg(container_cpu_usage_seconds_total{{service="{svc}"}}) / avg(kube_pod_container_resource_limits_cpu_cores{{service="{svc}"}}) * 100',
        "saturation_memory": 'avg(container_memory_usage_bytes{{service="{svc}"}}) / avg(kube_pod_container_resource_limits_memory_bytes{{service="{svc}"}}) * 100',
    }
    
    def __init__(self, services: List[ServiceMetadata]):
        self.services = services
        self.monitors: List[Monitor] = []
    
    def generate_monitors(self) -> List[Monitor]:
        """Generate all golden signal monitors"""
        for service in self.services:
            self._generate_latency_monitor(service)
            self._generate_error_monitor(service)
            self._generate_traffic_monitor(service)
            self._generate_saturation_monitors(service)
        
        return self.monitors
    
    def _generate_latency_monitor(self, svc: ServiceMetadata):
        """Generate latency monitor (P99)"""
        self.monitors.append(Monitor(
            name=f"{svc.name}_high_latency",
            signal="latency",
            query=self.QUERY_TEMPLATES["latency"].format(svc=svc.name),
            threshold=svc.slo_latency_ms,
            severity="warning",
        ))
    
    def _generate_error_monitor(self, svc: ServiceMetadata):
        """Generate error rate monitor"""
        self.monitors.append(Monitor(
            name=f"{svc.name}_high_error_rate",
            signal="errors",
            query=self.QUERY_TEMPLATES["errors"].format(svc=svc.name),
            threshold=svc.slo_error_rate,
            severity="critical",
        ))
    
    def _generate_traffic_monitor(self, svc: ServiceMetadata):
        """Generate traffic anomaly monitor"""
        self.monitors.append(Monitor(
            name=f"{svc.name}_traffic_anomaly",
            signal="traffic",
            query=self.QUERY_TEMPLATES["traffic"].format(svc=svc.name),
            threshold=0,  # Anomaly detection, no fixed threshold
            severity="info",
        ))
    
    def _generate_saturation_monitors(self, svc: ServiceMetadata):
        """Generate saturation monitors (CPU, Memory)"""
        self.monitors.append(Monitor(
            name=f"{svc.name}_high_cpu",
            signal="saturation",
            query=self.QUERY_TEMPLATES["saturation_cpu"].format(svc=svc.name),
            threshold=80,
            severity="warning",
        ))
        self.monitors.append(Monitor(
            name=f"{svc.name}_high_memory",
            signal="saturation",
            query=self.QUERY_TEMPLATES["saturation_memory"].format(svc=svc.name),
            threshold=85,
            severity="warning",
        ))
    
    def export_prometheus_rules(self) -> str:
        """Export as Prometheus alerting rules"""
        rules = {"groups": [{"name": "golden_signals", "rules": []}]}
        
        for monitor in self.monitors:
            rules["groups"][0]["rules"].append({
                "alert": monitor.name,
                "expr": f"{monitor.query} > {monitor.threshold}",
                "for": "5m",
                "labels": {"severity": monitor.severity, "signal": monitor.signal},
                "annotations": {"summary": f"Golden signal alert: {monitor.name}"},
            })
        
        return json.dumps(rules, indent=2)
    
    def get_summary(self) -> Dict:
        """Get generation summary"""
        by_signal = {}
        for m in self.monitors:
            by_signal[m.signal] = by_signal.get(m.signal, 0) + 1
        
        return {
            "total_monitors": len(self.monitors),
            "services_covered": len(self.services),
            "by_signal": by_signal,
        }


def get_demo_services() -> List[ServiceMetadata]:
    """Get demo service metadata"""
    return [
        ServiceMetadata("api-gateway", "api", slo_latency_ms=200, slo_error_rate=0.5, slo_availability=99.9),
        ServiceMetadata("auth-service", "api", slo_latency_ms=100, slo_error_rate=0.1, slo_availability=99.99),
        ServiceMetadata("payment-service", "api", slo_latency_ms=500, slo_error_rate=0.01, slo_availability=99.99),
        ServiceMetadata("order-worker", "worker", slo_latency_ms=5000, slo_error_rate=1.0, slo_availability=99.5),
    ]


def print_report(generator: GoldenSignalGenerator):
    """Print generation report"""
    summary = generator.get_summary()
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║          GOLDEN SIGNAL MONITOR GENERATOR                     ║
╠══════════════════════════════════════════════════════════════╣
║  Services Covered: {summary['services_covered']:<40}║
║  Total Monitors Generated: {summary['total_monitors']:<32}║
╠══════════════════════════════════════════════════════════════╣
║  BY SIGNAL TYPE:                                             ║
║    📊 Latency:    {summary['by_signal'].get('latency', 0):<41}║
║    ❌ Errors:     {summary['by_signal'].get('errors', 0):<41}║
║    📈 Traffic:    {summary['by_signal'].get('traffic', 0):<41}║
║    💾 Saturation: {summary['by_signal'].get('saturation', 0):<41}║
╠══════════════════════════════════════════════════════════════╣
║  GENERATED MONITORS:                                         ║""")
    
    for monitor in generator.monitors[:8]:
        print(f"║    [{monitor.severity[:4].upper()}] {monitor.name:<45}║")
    
    if len(generator.monitors) > 8:
        print(f"║    ... and {len(generator.monitors) - 8} more{' ':<43}║")
    
    print("╚══════════════════════════════════════════════════════════════╝")


def main():
    parser = argparse.ArgumentParser(description="Golden Signal Monitor Generator")
    parser.add_argument("--demo", action="store_true", help="Run demo")
    parser.add_argument("--output", type=str, help="Output Prometheus rules file")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("   GOLDEN SIGNAL MONITOR GENERATOR")
    print("=" * 60)
    
    services = get_demo_services()
    print(f"\n📋 Loaded {len(services)} service definitions")
    
    generator = GoldenSignalGenerator(services)
    
    print("🔧 Generating golden signal monitors...")
    generator.generate_monitors()
    
    print_report(generator)
    
    if args.output:
        rules = generator.export_prometheus_rules()
        with open(args.output, 'w') as f:
            f.write(rules)
        print(f"\n📄 Prometheus rules saved to: {args.output}")
    
    return 0


if __name__ == "__main__":
    exit(main())
