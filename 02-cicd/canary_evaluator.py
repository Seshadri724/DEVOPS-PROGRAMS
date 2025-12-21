#!/usr/bin/env python3
"""
================================================================================
CANARY EVALUATION SCRIPT
================================================================================

RESUME BULLET POINT:
"Built a canary evaluation script that automatically evaluates canary health 
metrics before full rollout, reducing failed deployment impact."

DESCRIPTION:
Monitors canary deployments and automatically decides whether to proceed with
full rollout or rollback based on predefined success criteria.

Author: DevOps Engineer | Version: 1.0.0
================================================================================
"""

import argparse
import json
import time
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum
import random


class CanaryStatus(Enum):
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    INCONCLUSIVE = "inconclusive"


@dataclass
class CanaryMetrics:
    """Metrics collected during canary evaluation"""
    error_rate: float
    latency_p50: float
    latency_p99: float
    throughput: float
    cpu_usage: float
    memory_usage: float


@dataclass
class CanaryResult:
    """Result of canary evaluation"""
    status: CanaryStatus
    canary_metrics: CanaryMetrics
    baseline_metrics: CanaryMetrics
    duration_seconds: int
    verdict: str
    details: List[str]


class CanaryEvaluator:
    """Evaluates canary deployments against baselines"""
    
    # Success criteria thresholds
    THRESHOLDS = {
        "error_rate_max_increase": 0.5,    # Max 0.5% increase from baseline
        "latency_p99_max_increase": 1.2,   # Max 20% increase
        "latency_p50_max_increase": 1.1,   # Max 10% increase
        "min_sample_size": 100,            # Minimum requests
    }
    
    def __init__(self, service: str, canary_version: str, baseline_version: str):
        self.service = service
        self.canary_version = canary_version
        self.baseline_version = baseline_version
        self.evaluation_results: List[Dict] = []
    
    def collect_metrics(self, is_canary: bool) -> CanaryMetrics:
        """Collect metrics from monitoring system (simulated)"""
        # Simulate slightly worse metrics for canary in some cases
        is_bad_canary = random.random() < 0.3  # 30% chance of bad canary
        
        base_error = random.uniform(0.1, 0.5)
        base_latency = random.uniform(50, 100)
        
        if is_canary and is_bad_canary:
            error_multiplier = random.uniform(1.5, 3.0)
            latency_multiplier = random.uniform(1.3, 2.0)
        else:
            error_multiplier = random.uniform(0.9, 1.1)
            latency_multiplier = random.uniform(0.95, 1.05)
        
        return CanaryMetrics(
            error_rate=base_error * (error_multiplier if is_canary else 1),
            latency_p50=base_latency * (latency_multiplier if is_canary else 1),
            latency_p99=base_latency * 2 * (latency_multiplier if is_canary else 1),
            throughput=random.uniform(100, 200),
            cpu_usage=random.uniform(30, 70),
            memory_usage=random.uniform(40, 80),
        )
    
    def evaluate(self, duration_seconds: int = 60, check_interval: int = 10) -> CanaryResult:
        """Run canary evaluation for specified duration"""
        print(f"\n🐤 Starting canary evaluation...")
        print(f"   Canary: {self.canary_version}")
        print(f"   Baseline: {self.baseline_version}")
        print(f"   Duration: {duration_seconds}s")
        
        start_time = time.time()
        checks = 0
        all_passed = True
        details = []
        
        while time.time() - start_time < duration_seconds:
            checks += 1
            print(f"\n📊 Check #{checks}...")
            
            canary_metrics = self.collect_metrics(is_canary=True)
            baseline_metrics = self.collect_metrics(is_canary=False)
            
            # Evaluate metrics
            check_results = self._evaluate_metrics(canary_metrics, baseline_metrics)
            
            for result in check_results:
                if not result["passed"]:
                    all_passed = False
                    details.append(f"Check #{checks}: {result['message']}")
                    print(f"   ❌ {result['metric']}: {result['message']}")
                else:
                    print(f"   ✅ {result['metric']}: OK")
            
            self.evaluation_results.append({
                "check": checks,
                "canary": vars(canary_metrics),
                "baseline": vars(baseline_metrics),
                "results": check_results,
            })
            
            time.sleep(0.5)  # Shortened for demo
        
        # Determine final verdict
        status = CanaryStatus.PASSED if all_passed else CanaryStatus.FAILED
        verdict = "PROMOTE - Canary is healthy" if all_passed else "ROLLBACK - Canary failed"
        
        return CanaryResult(
            status=status,
            canary_metrics=canary_metrics,
            baseline_metrics=baseline_metrics,
            duration_seconds=int(time.time() - start_time),
            verdict=verdict,
            details=details if details else ["All checks passed"],
        )
    
    def _evaluate_metrics(self, canary: CanaryMetrics, baseline: CanaryMetrics) -> List[Dict]:
        """Evaluate canary metrics against baseline"""
        results = []
        
        # Error rate check
        error_increase = canary.error_rate - baseline.error_rate
        results.append({
            "metric": "error_rate",
            "passed": error_increase <= self.THRESHOLDS["error_rate_max_increase"],
            "message": f"Error rate increased by {error_increase:.2f}%",
        })
        
        # Latency p99 check
        if baseline.latency_p99 > 0:
            latency_ratio = canary.latency_p99 / baseline.latency_p99
            results.append({
                "metric": "latency_p99",
                "passed": latency_ratio <= self.THRESHOLDS["latency_p99_max_increase"],
                "message": f"P99 latency ratio: {latency_ratio:.2f}x",
            })
        
        # Latency p50 check
        if baseline.latency_p50 > 0:
            latency_ratio = canary.latency_p50 / baseline.latency_p50
            results.append({
                "metric": "latency_p50",
                "passed": latency_ratio <= self.THRESHOLDS["latency_p50_max_increase"],
                "message": f"P50 latency ratio: {latency_ratio:.2f}x",
            })
        
        return results


def print_report(result: CanaryResult, evaluator: CanaryEvaluator):
    """Print canary evaluation report"""
    status_icon = "✅" if result.status == CanaryStatus.PASSED else "❌"
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║              CANARY EVALUATION REPORT                        ║
╠══════════════════════════════════════════════════════════════╣
║  Service: {evaluator.service:<49}║
║  Canary Version: {evaluator.canary_version:<42}║
║  Baseline Version: {evaluator.baseline_version:<40}║
╠══════════════════════════════════════════════════════════════╣
║  VERDICT: {status_icon} {result.verdict:<48}║
║  Duration: {result.duration_seconds}s{' ':<49}║
╠══════════════════════════════════════════════════════════════╣
║  METRIC COMPARISON:                     BASELINE    CANARY   ║
║    Error Rate:                          {result.baseline_metrics.error_rate:>6.2f}%    {result.canary_metrics.error_rate:>6.2f}%  ║
║    Latency P50:                         {result.baseline_metrics.latency_p50:>6.0f}ms   {result.canary_metrics.latency_p50:>6.0f}ms ║
║    Latency P99:                         {result.baseline_metrics.latency_p99:>6.0f}ms   {result.canary_metrics.latency_p99:>6.0f}ms ║
╠══════════════════════════════════════════════════════════════╣
║  DETAILS:                                                    ║""")
    
    for detail in result.details[:5]:
        print(f"║    {detail:<56}║")
    
    print("╚══════════════════════════════════════════════════════════════╝")


def main():
    parser = argparse.ArgumentParser(description="Canary Evaluation Script")
    parser.add_argument("--service", default="api-service", help="Service name")
    parser.add_argument("--canary-version", default="v2.0.0", help="Canary version")
    parser.add_argument("--baseline-version", default="v1.9.0", help="Baseline version")
    parser.add_argument("--duration", type=int, default=60, help="Evaluation duration (seconds)")
    parser.add_argument("--demo", action="store_true", help="Run demo")
    parser.add_argument("--output", type=str, help="JSON output file")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("   CANARY EVALUATION SCRIPT")
    print("=" * 60)
    
    evaluator = CanaryEvaluator(
        service=args.service,
        canary_version=args.canary_version,
        baseline_version=args.baseline_version,
    )
    
    result = evaluator.evaluate(duration_seconds=args.duration)
    print_report(result, evaluator)
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump({
                "status": result.status.value,
                "verdict": result.verdict,
                "duration": result.duration_seconds,
                "details": result.details,
            }, f, indent=2)
        print(f"\n📄 Report saved to: {args.output}")
    
    return 0 if result.status == CanaryStatus.PASSED else 1


if __name__ == "__main__":
    exit(main())
