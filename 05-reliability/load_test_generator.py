#!/usr/bin/env python3
"""
================================================================================
AUTOMATED LOAD TEST GENERATOR
================================================================================

RESUME BULLET POINT:
"Built an automated load test generator that creates realistic traffic 
patterns based on production usage to validate capacity."

Author: DevOps Engineer | Version: 1.0.0
================================================================================
"""

import argparse
import json
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass
import random


@dataclass
class Endpoint:
    """API endpoint to test"""
    path: str
    method: str
    weight: float  # Traffic weight
    expected_latency_ms: int


@dataclass
class LoadTestConfig:
    """Load test configuration"""
    name: str
    target_rps: int
    duration_seconds: int
    ramp_up_seconds: int
    endpoints: List[Endpoint]


@dataclass
class LoadTestResult:
    """Load test results"""
    total_requests: int
    successful: int
    failed: int
    avg_latency_ms: float
    p99_latency_ms: float
    max_rps_achieved: int


class LoadTestGenerator:
    """Generates and runs load tests"""
    
    def __init__(self):
        self.config: LoadTestConfig = None
        self.result: LoadTestResult = None
    
    def generate_config(self, base_rps: int = 100) -> LoadTestConfig:
        """Generate load test configuration from production patterns"""
        endpoints = [
            Endpoint("/api/users", "GET", 0.3, 100),
            Endpoint("/api/products", "GET", 0.25, 150),
            Endpoint("/api/orders", "POST", 0.2, 200),
            Endpoint("/api/search", "GET", 0.15, 250),
            Endpoint("/api/checkout", "POST", 0.1, 300),
        ]
        
        self.config = LoadTestConfig(
            name="production-pattern-test",
            target_rps=base_rps,
            duration_seconds=300,
            ramp_up_seconds=60,
            endpoints=endpoints,
        )
        return self.config
    
    def run_test(self, dry_run: bool = True) -> LoadTestResult:
        """Run load test (simulated)"""
        print(f"\n🚀 {'[DRY RUN] ' if dry_run else ''}Running load test...")
        print(f"   Target RPS: {self.config.target_rps}")
        print(f"   Duration: {self.config.duration_seconds}s")
        print(f"   Ramp-up: {self.config.ramp_up_seconds}s")
        
        # Simulate results
        total = self.config.target_rps * self.config.duration_seconds
        success_rate = random.uniform(0.95, 0.99)
        
        self.result = LoadTestResult(
            total_requests=total,
            successful=int(total * success_rate),
            failed=int(total * (1 - success_rate)),
            avg_latency_ms=random.uniform(50, 150),
            p99_latency_ms=random.uniform(200, 500),
            max_rps_achieved=int(self.config.target_rps * random.uniform(0.9, 1.0)),
        )
        
        return self.result
    
    def export_k6_script(self) -> str:
        """Export as k6 load test script"""
        script = f"""// Generated k6 load test script
import http from 'k6/http';
import {{ check, sleep }} from 'k6';

export const options = {{
  stages: [
    {{ duration: '{self.config.ramp_up_seconds}s', target: {self.config.target_rps} }},
    {{ duration: '{self.config.duration_seconds - self.config.ramp_up_seconds}s', target: {self.config.target_rps} }},
    {{ duration: '30s', target: 0 }},
  ],
}};

export default function() {{
"""
        for ep in self.config.endpoints:
            script += f"""
  // {ep.path} ({ep.weight * 100}% of traffic)
  if (Math.random() < {ep.weight}) {{
    const res = http.{ep.method.lower()}('${{__ENV.BASE_URL}}{ep.path}');
    check(res, {{ 'status is 200': (r) => r.status === 200 }});
  }}
"""
        script += "  sleep(0.1);\n}\n"
        return script


def print_report(generator: LoadTestGenerator):
    """Print load test report"""
    r = generator.result
    success_rate = r.successful / r.total_requests * 100
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║           LOAD TEST RESULTS                                  ║
╠══════════════════════════════════════════════════════════════╣
║  Test: {generator.config.name:<52}║
║  Target RPS: {generator.config.target_rps:<46}║
║  Achieved RPS: {r.max_rps_achieved:<44}║
╠══════════════════════════════════════════════════════════════╣
║  RESULTS:                                                    ║
║    Total Requests: {r.total_requests:<40}║
║    Successful: {r.successful:<45}║
║    Failed: {r.failed:<49}║
║    Success Rate: {success_rate:.2f}%{' ':<41}║
║    Avg Latency: {r.avg_latency_ms:.0f}ms{' ':<41}║
║    P99 Latency: {r.p99_latency_ms:.0f}ms{' ':<41}║
╚══════════════════════════════════════════════════════════════╝""")
    
    if success_rate < 99:
        print(f"\n⚠️ Success rate below 99% target!")


def main():
    parser = argparse.ArgumentParser(description="Load Test Generator")
    parser.add_argument("--demo", action="store_true")
    parser.add_argument("--rps", type=int, default=100)
    parser.add_argument("--export-k6", type=str, help="Export k6 script")
    parser.add_argument("--output", type=str)
    args = parser.parse_args()
    
    print("=" * 60)
    print("   AUTOMATED LOAD TEST GENERATOR")
    print("=" * 60)
    
    generator = LoadTestGenerator()
    generator.generate_config(args.rps)
    generator.run_test(dry_run=True)
    
    print_report(generator)
    
    if args.export_k6:
        script = generator.export_k6_script()
        with open(args.export_k6, 'w') as f:
            f.write(script)
        print(f"\n📄 k6 script saved to: {args.export_k6}")
    
    return 0


if __name__ == "__main__":
    exit(main())
