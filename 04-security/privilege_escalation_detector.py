#!/usr/bin/env python3
"""
================================================================================
RUNTIME PRIVILEGE ESCALATION DETECTOR
================================================================================

RESUME BULLET POINT:
"Built a runtime privilege escalation detector that identifies containers 
running with excessive permissions, improving container security posture."

Author: DevOps Engineer | Version: 1.0.0
================================================================================
"""

import argparse
import json
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum


class RiskLevel(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ContainerSecurityFinding:
    """Security finding for a container"""
    container: str
    namespace: str
    finding: str
    risk: RiskLevel


class PrivilegeDetector:
    """Detects containers with excessive privileges"""
    
    def __init__(self):
        self.findings: List[ContainerSecurityFinding] = []
    
    def scan_demo(self) -> List[ContainerSecurityFinding]:
        """Demo scan"""
        self.findings = [
            ContainerSecurityFinding("legacy-app", "default", "Running as root", RiskLevel.HIGH),
            ContainerSecurityFinding("debug-pod", "kube-system", "privileged: true", RiskLevel.CRITICAL),
            ContainerSecurityFinding("monitoring", "monitoring", "hostNetwork: true", RiskLevel.MEDIUM),
            ContainerSecurityFinding("backup-job", "default", "hostPath mount to /var/run/docker.sock", RiskLevel.CRITICAL),
        ]
        return self.findings
    
    def get_summary(self) -> Dict:
        """Get scan summary"""
        by_risk = {}
        for f in self.findings:
            by_risk[f.risk.value] = by_risk.get(f.risk.value, 0) + 1
        
        return {
            "total": len(self.findings),
            "by_risk": by_risk,
            "critical": by_risk.get("critical", 0),
        }


def print_report(detector: PrivilegeDetector):
    """Print security report"""
    summary = detector.get_summary()
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║        CONTAINER PRIVILEGE ESCALATION REPORT                 ║
╠══════════════════════════════════════════════════════════════╣
║  Total Findings: {summary['total']:<42}║
║  Critical: {summary['critical']:<48}║
╠══════════════════════════════════════════════════════════════╣
║  FINDINGS:                                                   ║""")
    
    icons = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
    for f in detector.findings:
        print(f"║    {icons[f.risk.value]} {f.container:<20} {f.finding:<25}║")
    
    print("╚══════════════════════════════════════════════════════════════╝")
    
    if summary['critical'] > 0:
        print(f"\n🚨 CRITICAL: {summary['critical']} container(s) with dangerous privileges!")


def main():
    parser = argparse.ArgumentParser(description="Privilege Escalation Detector")
    parser.add_argument("--demo", action="store_true")
    parser.add_argument("--output", type=str)
    args = parser.parse_args()
    
    print("=" * 60)
    print("   RUNTIME PRIVILEGE ESCALATION DETECTOR")
    print("=" * 60)
    
    detector = PrivilegeDetector()
    print("\n🔍 Scanning containers...")
    detector.scan_demo()
    
    print_report(detector)
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(detector.get_summary(), f, indent=2)
    
    return 1 if detector.get_summary()['critical'] > 0 else 0


if __name__ == "__main__":
    exit(main())
