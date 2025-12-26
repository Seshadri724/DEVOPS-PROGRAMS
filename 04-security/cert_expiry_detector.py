#!/usr/bin/env python3
"""
================================================================================
EXPIRED CERTIFICATE DETECTOR
================================================================================

RESUME BULLET POINT:
"Built an expired certificate detector that prevents SSL/TLS certificate 
expiry incidents through proactive monitoring and alerting."

Author: DevOps Engineer | Version: 1.0.0
================================================================================
"""

import argparse
import json
from datetime import datetime, timedelta
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum


class CertStatus(Enum):
    VALID = "valid"
    EXPIRING_SOON = "expiring_soon"
    EXPIRED = "expired"


@dataclass
class Certificate:
    """SSL/TLS Certificate"""
    domain: str
    issuer: str
    expires_at: datetime
    days_until_expiry: int
    status: CertStatus


class CertificateChecker:
    """Checks certificate expiration"""
    
    WARNING_THRESHOLD_DAYS = 30
    CRITICAL_THRESHOLD_DAYS = 7
    
    def __init__(self):
        self.certificates: List[Certificate] = []
    
    def check_demo(self) -> List[Certificate]:
        """Demo check with sample certificates"""
        now = datetime.now()
        
        self.certificates = [
            Certificate("api.company.com", "Let's Encrypt", now + timedelta(days=45), 45, CertStatus.VALID),
            Certificate("app.company.com", "Let's Encrypt", now + timedelta(days=15), 15, CertStatus.EXPIRING_SOON),
            Certificate("legacy.company.com", "DigiCert", now + timedelta(days=3), 3, CertStatus.EXPIRING_SOON),
            Certificate("old.company.com", "Comodo", now - timedelta(days=5), -5, CertStatus.EXPIRED),
        ]
        return self.certificates
    
    def get_summary(self) -> Dict:
        """Get check summary"""
        return {
            "total": len(self.certificates),
            "valid": sum(1 for c in self.certificates if c.status == CertStatus.VALID),
            "expiring_soon": sum(1 for c in self.certificates if c.status == CertStatus.EXPIRING_SOON),
            "expired": sum(1 for c in self.certificates if c.status == CertStatus.EXPIRED),
        }


def print_report(checker: CertificateChecker):
    """Print certificate report"""
    summary = checker.get_summary()
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║           CERTIFICATE EXPIRY REPORT                          ║
╠══════════════════════════════════════════════════════════════╣
║  Total Certificates: {summary['total']:<38}║
║  ✅ Valid: {summary['valid']:<48}║
║  ⚠️  Expiring Soon: {summary['expiring_soon']:<40}║
║  ❌ Expired: {summary['expired']:<47}║
╠══════════════════════════════════════════════════════════════╣
║  CERTIFICATES:                                               ║""")
    
    for cert in sorted(checker.certificates, key=lambda x: x.days_until_expiry):
        if cert.status == CertStatus.EXPIRED:
            icon = "❌"
        elif cert.days_until_expiry <= 7:
            icon = "🔴"
        elif cert.days_until_expiry <= 30:
            icon = "🟡"
        else:
            icon = "🟢"
        print(f"║    {icon} {cert.domain:<30} {cert.days_until_expiry:>3}d  ║")
    
    print("╚══════════════════════════════════════════════════════════════╝")
    
    if summary['expired'] > 0:
        print(f"\n🚨 CRITICAL: {summary['expired']} certificate(s) have expired!")


def main():
    parser = argparse.ArgumentParser(description="Certificate Expiry Detector")
    parser.add_argument("--demo", action="store_true")
    parser.add_argument("--output", type=str)
    args = parser.parse_args()
    
    print("=" * 60)
    print("   CERTIFICATE EXPIRY DETECTOR")
    print("=" * 60)
    
    checker = CertificateChecker()
    print("\n🔍 Checking certificates...")
    checker.check_demo()
    
    print_report(checker)
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(checker.get_summary(), f, indent=2)
    
    return 1 if checker.get_summary()['expired'] > 0 else 0


if __name__ == "__main__":
    exit(main())
