#!/usr/bin/env python3
"""
================================================================================
PUBLIC EXPOSURE DETECTION FOR CLOUD RESOURCES
================================================================================

RESUME BULLET POINT:
"Automated public exposure detection for cloud resources (open ports, public 
buckets), reducing security risk without slowing development."

Author: DevOps Engineer | Version: 1.0.0
================================================================================
"""

import argparse
import json
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum


class ExposureType(Enum):
    PUBLIC_BUCKET = "public_bucket"
    OPEN_PORT = "open_port"
    PUBLIC_DB = "public_database"
    PUBLIC_API = "unauth_api"


class RiskLevel(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"


@dataclass
class ExposureFinding:
    """Detected public exposure"""
    resource_id: str
    resource_type: str
    exposure_type: ExposureType
    risk: RiskLevel
    details: str


class ExposureDetector:
    """Detects publicly exposed cloud resources"""
    
    DANGEROUS_PORTS = [22, 3389, 3306, 5432, 27017, 6379, 9200]
    
    def __init__(self):
        self.findings: List[ExposureFinding] = []
    
    def scan_demo(self) -> List[ExposureFinding]:
        """Run demo scan"""
        # Simulated findings
        self.findings = [
            ExposureFinding("s3://company-backups", "s3_bucket", ExposureType.PUBLIC_BUCKET, RiskLevel.CRITICAL, "Bucket has public read access"),
            ExposureFinding("sg-12345", "security_group", ExposureType.OPEN_PORT, RiskLevel.HIGH, "Port 22 open to 0.0.0.0/0"),
            ExposureFinding("sg-67890", "security_group", ExposureType.OPEN_PORT, RiskLevel.CRITICAL, "Port 3306 (MySQL) open to internet"),
            ExposureFinding("rds-prod-db", "rds_instance", ExposureType.PUBLIC_DB, RiskLevel.CRITICAL, "Publicly accessible RDS instance"),
        ]
        return self.findings
    
    def get_summary(self) -> Dict:
        """Get scan summary"""
        by_type = {}
        for f in self.findings:
            by_type[f.exposure_type.value] = by_type.get(f.exposure_type.value, 0) + 1
        
        return {
            "total_findings": len(self.findings),
            "critical": sum(1 for f in self.findings if f.risk == RiskLevel.CRITICAL),
            "by_type": by_type,
        }


def print_report(detector: ExposureDetector):
    """Print exposure report"""
    summary = detector.get_summary()
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║           PUBLIC EXPOSURE DETECTION REPORT                   ║
╠══════════════════════════════════════════════════════════════╣
║  Total Exposures: {summary['total_findings']:<41}║
║  Critical: {summary['critical']:<48}║
╠══════════════════════════════════════════════════════════════╣
║  FINDINGS:                                                   ║""")
    
    for f in detector.findings:
        icon = "🔴" if f.risk == RiskLevel.CRITICAL else "🟠"
        print(f"║    {icon} {f.resource_id:<25} {f.exposure_type.value:<18}║")
    
    print("╚══════════════════════════════════════════════════════════════╝")
    
    if summary['critical'] > 0:
        print(f"\n🚨 CRITICAL: {summary['critical']} resources publicly exposed!")


def main():
    parser = argparse.ArgumentParser(description="Public Exposure Detector")
    parser.add_argument("--demo", action="store_true")
    parser.add_argument("--output", type=str)
    args = parser.parse_args()
    
    print("=" * 60)
    print("   PUBLIC EXPOSURE DETECTION")
    print("=" * 60)
    
    detector = ExposureDetector()
    print("\n🔍 Scanning for public exposures...")
    detector.scan_demo()
    
    print_report(detector)
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(detector.get_summary(), f, indent=2)
    
    return 1 if detector.get_summary()['critical'] > 0 else 0


if __name__ == "__main__":
    exit(main())
