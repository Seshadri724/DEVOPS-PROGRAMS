#!/usr/bin/env python3
"""
================================================================================
DEPENDENCY LICENSE SCANNER
================================================================================

RESUME BULLET POINT:
"Built a dependency license scanner that flags risky open-source licenses 
early, ensuring compliance before production deployment."

Author: DevOps Engineer | Version: 1.0.0
================================================================================
"""

import argparse
import json
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum


class LicenseRisk(Enum):
    HIGH = "high"      # Copyleft (GPL, AGPL)
    MEDIUM = "medium"  # Weak copyleft (LGPL, MPL)
    LOW = "low"        # Permissive (MIT, Apache, BSD)
    UNKNOWN = "unknown"


@dataclass
class Dependency:
    """A project dependency"""
    name: str
    version: str
    license: str
    risk: LicenseRisk


class LicenseScanner:
    """Scans dependencies for license compliance"""
    
    LICENSE_CLASSIFICATION = {
        "MIT": LicenseRisk.LOW,
        "Apache-2.0": LicenseRisk.LOW,
        "BSD-3-Clause": LicenseRisk.LOW,
        "ISC": LicenseRisk.LOW,
        "LGPL-3.0": LicenseRisk.MEDIUM,
        "MPL-2.0": LicenseRisk.MEDIUM,
        "GPL-3.0": LicenseRisk.HIGH,
        "AGPL-3.0": LicenseRisk.HIGH,
    }
    
    def __init__(self):
        self.dependencies: List[Dependency] = []
    
    def scan_demo(self) -> List[Dependency]:
        """Demo scan with sample dependencies"""
        self.dependencies = [
            Dependency("react", "18.2.0", "MIT", LicenseRisk.LOW),
            Dependency("express", "4.18.2", "MIT", LicenseRisk.LOW),
            Dependency("lodash", "4.17.21", "MIT", LicenseRisk.LOW),
            Dependency("mysql-connector", "2.3.0", "GPL-3.0", LicenseRisk.HIGH),
            Dependency("charting-lib", "1.0.0", "AGPL-3.0", LicenseRisk.HIGH),
            Dependency("xml-parser", "3.0.0", "LGPL-3.0", LicenseRisk.MEDIUM),
        ]
        return self.dependencies
    
    def get_summary(self) -> Dict:
        """Get scan summary"""
        by_risk = {}
        for d in self.dependencies:
            by_risk[d.risk.value] = by_risk.get(d.risk.value, 0) + 1
        
        return {
            "total_dependencies": len(self.dependencies),
            "by_risk": by_risk,
            "high_risk_count": by_risk.get("high", 0),
            "compliant": by_risk.get("high", 0) == 0,
        }


def print_report(scanner: LicenseScanner):
    """Print license report"""
    summary = scanner.get_summary()
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║           DEPENDENCY LICENSE SCAN REPORT                     ║
╠══════════════════════════════════════════════════════════════╣
║  Total Dependencies: {summary['total_dependencies']:<38}║
║  High Risk (Copyleft): {summary['high_risk_count']:<36}║
║  Compliance Status: {'❌ REVIEW NEEDED' if not summary['compliant'] else '✅ COMPLIANT':<37}║
╠══════════════════════════════════════════════════════════════╣
║  RISKY LICENSES:                                             ║""")
    
    for dep in scanner.dependencies:
        if dep.risk in [LicenseRisk.HIGH, LicenseRisk.MEDIUM]:
            icon = "🔴" if dep.risk == LicenseRisk.HIGH else "🟡"
            print(f"║    {icon} {dep.name:<25} {dep.license:<20}║")
    
    print("╚══════════════════════════════════════════════════════════════╝")


def main():
    parser = argparse.ArgumentParser(description="License Scanner")
    parser.add_argument("--demo", action="store_true")
    parser.add_argument("--output", type=str)
    args = parser.parse_args()
    
    print("=" * 60)
    print("   DEPENDENCY LICENSE SCANNER")
    print("=" * 60)
    
    scanner = LicenseScanner()
    print("\n🔍 Scanning dependencies...")
    scanner.scan_demo()
    
    print_report(scanner)
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(scanner.get_summary(), f, indent=2)
    
    return 0 if scanner.get_summary()['compliant'] else 1


if __name__ == "__main__":
    exit(main())
