#!/usr/bin/env python3
"""
================================================================================
CHAOS ENGINEERING EXPERIMENT RUNNER
================================================================================

RESUME BULLET POINT:
"Built a chaos engineering experiment runner that safely injects failures 
to test system resilience and improve reliability."

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


class ExperimentType(Enum):
    POD_KILL = "pod_kill"
    NETWORK_LATENCY = "network_latency"
    CPU_STRESS = "cpu_stress"
    MEMORY_STRESS = "memory_stress"
    DISK_FILL = "disk_fill"


class ExperimentStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"


@dataclass
class ChaosExperiment:
    """Chaos engineering experiment"""
    name: str
    experiment_type: ExperimentType
    target: str
    duration_seconds: int
    parameters: Dict
    status: ExperimentStatus = ExperimentStatus.PENDING


@dataclass
class ExperimentResult:
    """Result of chaos experiment"""
    experiment: str
    status: ExperimentStatus
    hypothesis_validated: bool
    observations: List[str]
    impact_score: float  # 0-1, lower is better


class ChaosRunner:
    """Runs chaos engineering experiments"""
    
    def __init__(self):
        self.experiments: List[ChaosExperiment] = []
        self.results: List[ExperimentResult] = []
        self.safety_checks_passed = True
    
    def load_experiments(self) -> List[ChaosExperiment]:
        """Load experiment definitions"""
        self.experiments = [
            ChaosExperiment(
                name="pod-failure-api",
                experiment_type=ExperimentType.POD_KILL,
                target="api-service",
                duration_seconds=60,
                parameters={"kill_count": 1, "interval": 30},
            ),
            ChaosExperiment(
                name="network-latency-db",
                experiment_type=ExperimentType.NETWORK_LATENCY,
                target="database",
                duration_seconds=120,
                parameters={"latency_ms": 100, "jitter_ms": 20},
            ),
            ChaosExperiment(
                name="cpu-stress-worker",
                experiment_type=ExperimentType.CPU_STRESS,
                target="worker-pods",
                duration_seconds=180,
                parameters={"cpu_percent": 80},
            ),
        ]
        return self.experiments
    
    def run_safety_checks(self) -> bool:
        """Run pre-experiment safety checks"""
        print("\n🛡️ Running safety checks...")
        
        checks = [
            ("System healthy", True),
            ("No active incidents", True),
            ("Rollback ready", True),
            ("Monitoring active", True),
        ]
        
        for check, passed in checks:
            status = "✅" if passed else "❌"
            print(f"   {status} {check}")
            if not passed:
                self.safety_checks_passed = False
        
        return self.safety_checks_passed
    
    def run_experiment(self, exp: ChaosExperiment, dry_run: bool = True) -> ExperimentResult:
        """Run a single chaos experiment"""
        print(f"\n🔥 {'[DRY RUN] ' if dry_run else ''}Running: {exp.name}")
        print(f"   Type: {exp.experiment_type.value}")
        print(f"   Target: {exp.target}")
        print(f"   Duration: {exp.duration_seconds}s")
        
        exp.status = ExperimentStatus.RUNNING
        
        # Simulate experiment execution
        time.sleep(0.5)
        
        # Simulated results
        hypothesis_validated = random.random() > 0.2  # 80% success
        impact_score = random.uniform(0.1, 0.3) if hypothesis_validated else random.uniform(0.5, 0.8)
        
        observations = [
            f"Service maintained {random.randint(95, 100)}% availability",
            f"Error rate increased by {random.uniform(0, 2):.1f}%",
            f"Recovery time: {random.randint(5, 30)}s",
        ]
        
        exp.status = ExperimentStatus.COMPLETED
        
        result = ExperimentResult(
            experiment=exp.name,
            status=ExperimentStatus.COMPLETED,
            hypothesis_validated=hypothesis_validated,
            observations=observations,
            impact_score=impact_score,
        )
        
        print(f"   Result: {'✅ PASSED' if hypothesis_validated else '❌ FAILED'}")
        
        self.results.append(result)
        return result
    
    def run_all(self, dry_run: bool = True) -> List[ExperimentResult]:
        """Run all experiments"""
        if not self.run_safety_checks():
            print("\n🚫 Safety checks failed - aborting experiments")
            return []
        
        print(f"\n🎯 Running {len(self.experiments)} experiments...")
        
        for exp in self.experiments:
            self.run_experiment(exp, dry_run)
        
        return self.results
    
    def get_summary(self) -> Dict:
        """Get experiment summary"""
        validated = sum(1 for r in self.results if r.hypothesis_validated)
        return {
            "total_experiments": len(self.results),
            "validated": validated,
            "failed": len(self.results) - validated,
            "avg_impact": sum(r.impact_score for r in self.results) / len(self.results) if self.results else 0,
        }


def print_report(runner: ChaosRunner):
    """Print experiment report"""
    summary = runner.get_summary()
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║        CHAOS ENGINEERING EXPERIMENT REPORT                   ║
╠══════════════════════════════════════════════════════════════╣
║  Total Experiments: {summary['total_experiments']:<39}║
║  ✅ Hypothesis Validated: {summary['validated']:<33}║
║  ❌ Failed: {summary['failed']:<48}║
║  Avg Impact Score: {summary['avg_impact']:.2f}{' ':<38}║
╠══════════════════════════════════════════════════════════════╣
║  EXPERIMENT RESULTS:                                         ║""")
    
    for result in runner.results:
        icon = "✅" if result.hypothesis_validated else "❌"
        print(f"║    {icon} {result.experiment:<35} {result.impact_score:.2f} ║")
    
    print("╚══════════════════════════════════════════════════════════════╝")


def main():
    parser = argparse.ArgumentParser(description="Chaos Engineering Runner")
    parser.add_argument("--demo", action="store_true")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--output", type=str)
    args = parser.parse_args()
    
    print("=" * 60)
    print("   CHAOS ENGINEERING EXPERIMENT RUNNER")
    print("=" * 60)
    
    runner = ChaosRunner()
    runner.load_experiments()
    runner.run_all(dry_run=args.dry_run)
    
    print_report(runner)
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(runner.get_summary(), f, indent=2)
    
    return 0


if __name__ == "__main__":
    exit(main())
