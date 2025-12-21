#!/usr/bin/env python3
"""
================================================================================
CONFIG DRIFT DETECTOR FOR CI PIPELINES
================================================================================

RESUME BULLET POINT:
"Built a config drift detector that ensures CI/CD pipelines across repositories
follow baseline standards, maintaining consistency and security."

DESCRIPTION:
Scans CI/CD configuration files (GitHub Actions, GitLab CI, etc.) across repos
to detect deviations from organizational standards and best practices.

Author: DevOps Engineer | Version: 1.0.0
================================================================================
"""

import argparse
import json
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum


class DriftSeverity(Enum):
    CRITICAL = "critical"  # Security issue
    HIGH = "high"          # Major deviation
    MEDIUM = "medium"      # Minor deviation
    LOW = "low"            # Style/preference


@dataclass
class PipelineConfig:
    """Represents a CI/CD pipeline configuration"""
    repo: str
    file_path: str
    platform: str  # github, gitlab, jenkins
    config: Dict


@dataclass
class PipelineDrift:
    """Detected drift from baseline"""
    repo: str
    rule: str
    severity: DriftSeverity
    expected: str
    actual: str
    auto_fixable: bool = False


class BaselineRules:
    """Defines baseline rules for CI/CD pipelines"""
    
    RULES = {
        "docker_image_pinned": {
            "description": "Docker images should use pinned versions",
            "severity": DriftSeverity.HIGH,
            "check": lambda c: not any("latest" in str(v) for v in c.values()),
        },
        "secrets_not_hardcoded": {
            "description": "Secrets should use environment variables",
            "severity": DriftSeverity.CRITICAL,
            "check": lambda c: "password" not in str(c).lower() or "secrets." in str(c),
        },
        "timeout_configured": {
            "description": "Jobs should have timeout limits",
            "severity": DriftSeverity.MEDIUM,
            "check": lambda c: "timeout" in str(c).lower(),
        },
        "caching_enabled": {
            "description": "Build caching should be enabled",
            "severity": DriftSeverity.LOW,
            "check": lambda c: "cache" in str(c).lower(),
        },
        "security_scan_present": {
            "description": "Security scanning step should exist",
            "severity": DriftSeverity.HIGH,
            "check": lambda c: any(x in str(c).lower() for x in ["security", "snyk", "trivy"]),
        },
    }


class PipelineScanner:
    """Scans repositories for CI/CD configurations"""
    
    @staticmethod
    def scan_repos() -> List[PipelineConfig]:
        """Scan repositories for pipeline configs (simulated)"""
        configs = [
            PipelineConfig(
                repo="api-service",
                file_path=".github/workflows/ci.yml",
                platform="github",
                config={
                    "jobs": {"build": {"image": "node:18", "timeout": "30m", "cache": True}},
                    "security_scan": True,
                }
            ),
            PipelineConfig(
                repo="frontend-app",
                file_path=".github/workflows/ci.yml",
                platform="github",
                config={
                    "jobs": {"build": {"image": "node:latest"}},  # Uses latest!
                    # Missing timeout, cache, security
                }
            ),
            PipelineConfig(
                repo="data-pipeline",
                file_path=".gitlab-ci.yml",
                platform="gitlab",
                config={
                    "jobs": {"build": {"image": "python:3.11", "timeout": "60m"}},
                    # Missing cache, security
                }
            ),
        ]
        return configs


class DriftDetector:
    """Detects pipeline configuration drift"""
    
    def __init__(self):
        self.drifts: List[PipelineDrift] = []
    
    def analyze_pipelines(self, configs: List[PipelineConfig]) -> List[PipelineDrift]:
        """Analyze all pipeline configs against baseline"""
        print("\n🔍 Analyzing pipeline configurations...")
        
        for config in configs:
            self._check_pipeline(config)
        
        return self.drifts
    
    def _check_pipeline(self, config: PipelineConfig):
        """Check a single pipeline against all rules"""
        for rule_name, rule in BaselineRules.RULES.items():
            try:
                passes = rule["check"](config.config)
            except Exception:
                passes = False
            
            if not passes:
                self.drifts.append(PipelineDrift(
                    repo=config.repo,
                    rule=rule_name,
                    severity=rule["severity"],
                    expected=rule["description"],
                    actual=f"Rule violated in {config.file_path}",
                ))
    
    def get_summary(self) -> Dict:
        """Get drift detection summary"""
        by_severity = {}
        by_repo = {}
        
        for drift in self.drifts:
            sev = drift.severity.value
            by_severity[sev] = by_severity.get(sev, 0) + 1
            by_repo[drift.repo] = by_repo.get(drift.repo, 0) + 1
        
        return {
            "total_drifts": len(self.drifts),
            "by_severity": by_severity,
            "by_repo": by_repo,
            "repos_analyzed": len(set(d.repo for d in self.drifts)),
            "critical_count": by_severity.get("critical", 0),
        }


def print_report(detector: DriftDetector, configs: List[PipelineConfig]):
    """Print drift detection report"""
    summary = detector.get_summary()
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║           CI PIPELINE DRIFT DETECTION REPORT                 ║
╠══════════════════════════════════════════════════════════════╣
║  Repositories Scanned: {len(configs):<36}║
║  Total Drifts Found: {summary['total_drifts']:<38}║
╠══════════════════════════════════════════════════════════════╣
║  BY SEVERITY:                                                ║""")
    
    for sev in ["critical", "high", "medium", "low"]:
        count = summary["by_severity"].get(sev, 0)
        icons = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
        print(f"║    {icons[sev]} {sev.upper():<12} {count:>3} issues{' ':<30}║")
    
    print(f"""╠══════════════════════════════════════════════════════════════╣
║  BY REPOSITORY:                                              ║""")
    
    for repo, count in summary["by_repo"].items():
        print(f"║    {repo:<30} {count:>3} issues{' ':<17}║")
    
    print(f"""╠══════════════════════════════════════════════════════════════╣
║  DRIFT DETAILS:                                              ║""")
    
    for drift in detector.drifts[:8]:
        icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}[drift.severity.value]
        print(f"║    {icon} {drift.repo:<20} {drift.rule:<30}║")
    
    print("╚══════════════════════════════════════════════════════════════╝")


def main():
    parser = argparse.ArgumentParser(description="CI Pipeline Drift Detector")
    parser.add_argument("--demo", action="store_true", help="Run with demo data")
    parser.add_argument("--output", type=str, help="JSON output file")
    parser.add_argument("--strict", action="store_true", help="Fail on any critical drift")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("   CI PIPELINE DRIFT DETECTOR")
    print("=" * 60)
    
    print("\n📂 Scanning repositories...")
    configs = PipelineScanner.scan_repos()
    print(f"   Found {len(configs)} pipeline configurations")
    
    detector = DriftDetector()
    detector.analyze_pipelines(configs)
    
    print_report(detector, configs)
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump({
                "summary": detector.get_summary(),
                "drifts": [{"repo": d.repo, "rule": d.rule, "severity": d.severity.value} 
                          for d in detector.drifts]
            }, f, indent=2)
        print(f"\n📄 Report saved to: {args.output}")
    
    return 1 if detector.get_summary()["critical_count"] > 0 else 0


if __name__ == "__main__":
    exit(main())
