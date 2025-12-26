#!/usr/bin/env python3
"""
================================================================================
IAM PERMISSION AUDITING TOOL
================================================================================

RESUME BULLET POINT:
"Built an IAM permission auditing tool to detect over-privileged roles and 
enforce least-privilege access across cloud environments."

DESCRIPTION:
Analyzes IAM policies to identify over-permissive roles, unused permissions,
and violations of least-privilege principles.

Author: DevOps Engineer | Version: 1.0.0
================================================================================
"""

import argparse
import json
from datetime import datetime, timedelta
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum
import random


class RiskLevel(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class IAMPrincipal:
    """IAM user, role, or service account"""
    name: str
    type: str  # user, role, service_account
    permissions: List[str]
    last_used: datetime
    created_at: datetime


@dataclass
class PermissionFinding:
    """Finding from permission audit"""
    principal: str
    finding_type: str
    risk: RiskLevel
    description: str
    recommendation: str


class IAMAuditor:
    """Audits IAM permissions"""
    
    # Dangerous permissions
    HIGH_RISK_PERMISSIONS = [
        "*:*",
        "iam:*",
        "sts:AssumeRole",
        "s3:*",
        "ec2:*",
        "lambda:*",
    ]
    
    ADMIN_PERMISSIONS = ["*:*", "AdministratorAccess"]
    
    def __init__(self):
        self.principals: List[IAMPrincipal] = []
        self.findings: List[PermissionFinding] = []
    
    def load_principals(self) -> List[IAMPrincipal]:
        """Load IAM principals (simulated)"""
        demo_principals = [
            IAMPrincipal(
                name="admin-user",
                type="user",
                permissions=["*:*"],
                last_used=datetime.now() - timedelta(days=90),
                created_at=datetime.now() - timedelta(days=365),
            ),
            IAMPrincipal(
                name="deploy-role",
                type="role",
                permissions=["s3:*", "ec2:*", "lambda:*", "iam:PassRole"],
                last_used=datetime.now() - timedelta(days=1),
                created_at=datetime.now() - timedelta(days=180),
            ),
            IAMPrincipal(
                name="read-only-role",
                type="role",
                permissions=["s3:GetObject", "s3:ListBucket"],
                last_used=datetime.now() - timedelta(days=5),
                created_at=datetime.now() - timedelta(days=30),
            ),
            IAMPrincipal(
                name="unused-service-account",
                type="service_account",
                permissions=["s3:*", "dynamodb:*"],
                last_used=datetime.now() - timedelta(days=120),
                created_at=datetime.now() - timedelta(days=200),
            ),
        ]
        self.principals = demo_principals
        return self.principals
    
    def audit(self) -> List[PermissionFinding]:
        """Run full IAM audit"""
        for principal in self.principals:
            self._check_admin_access(principal)
            self._check_high_risk_permissions(principal)
            self._check_unused_principal(principal)
            self._check_wildcard_permissions(principal)
        
        return self.findings
    
    def _check_admin_access(self, principal: IAMPrincipal):
        """Check for admin access"""
        for perm in principal.permissions:
            if perm in self.ADMIN_PERMISSIONS:
                self.findings.append(PermissionFinding(
                    principal=principal.name,
                    finding_type="admin_access",
                    risk=RiskLevel.CRITICAL,
                    description=f"Has full admin access ({perm})",
                    recommendation="Replace with specific permissions",
                ))
                break
    
    def _check_high_risk_permissions(self, principal: IAMPrincipal):
        """Check for high-risk permissions"""
        risky = [p for p in principal.permissions if p in self.HIGH_RISK_PERMISSIONS and p not in self.ADMIN_PERMISSIONS]
        if risky:
            self.findings.append(PermissionFinding(
                principal=principal.name,
                finding_type="high_risk_permissions",
                risk=RiskLevel.HIGH,
                description=f"Has high-risk permissions: {', '.join(risky[:3])}",
                recommendation="Review and restrict permissions",
            ))
    
    def _check_unused_principal(self, principal: IAMPrincipal):
        """Check for unused principals"""
        days_unused = (datetime.now() - principal.last_used).days
        if days_unused > 90:
            self.findings.append(PermissionFinding(
                principal=principal.name,
                finding_type="unused_principal",
                risk=RiskLevel.MEDIUM,
                description=f"Not used in {days_unused} days",
                recommendation="Disable or delete if no longer needed",
            ))
    
    def _check_wildcard_permissions(self, principal: IAMPrincipal):
        """Check for wildcard permissions"""
        wildcards = [p for p in principal.permissions if '*' in p and p != '*:*']
        if wildcards:
            self.findings.append(PermissionFinding(
                principal=principal.name,
                finding_type="wildcard_permissions",
                risk=RiskLevel.MEDIUM,
                description=f"Has wildcard permissions: {', '.join(wildcards[:2])}",
                recommendation="Use specific resource ARNs",
            ))
    
    def get_summary(self) -> Dict:
        """Get audit summary"""
        by_risk = {}
        for f in self.findings:
            by_risk[f.risk.value] = by_risk.get(f.risk.value, 0) + 1
        
        return {
            "principals_audited": len(self.principals),
            "total_findings": len(self.findings),
            "by_risk": by_risk,
            "critical_count": by_risk.get("critical", 0),
        }


def print_report(auditor: IAMAuditor):
    """Print audit report"""
    summary = auditor.get_summary()
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║              IAM PERMISSION AUDIT REPORT                     ║
╠══════════════════════════════════════════════════════════════╣
║  Principals Audited: {summary['principals_audited']:<38}║
║  Total Findings: {summary['total_findings']:<42}║
╠══════════════════════════════════════════════════════════════╣
║  BY RISK LEVEL:                                              ║""")
    
    icons = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
    for risk in ["critical", "high", "medium", "low"]:
        count = summary['by_risk'].get(risk, 0)
        print(f"║    {icons[risk]} {risk.upper():<12} {count:>3} findings{' ':<26}║")
    
    print(f"""╠══════════════════════════════════════════════════════════════╣
║  FINDINGS:                                                   ║""")
    
    for finding in auditor.findings:
        icon = icons[finding.risk.value]
        print(f"║    {icon} {finding.principal:<20} {finding.finding_type:<20}║")
    
    print("╚══════════════════════════════════════════════════════════════╝")


def main():
    parser = argparse.ArgumentParser(description="IAM Permission Auditor")
    parser.add_argument("--demo", action="store_true", help="Run demo")
    parser.add_argument("--output", type=str, help="JSON output file")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("   IAM PERMISSION AUDITING TOOL")
    print("=" * 60)
    
    auditor = IAMAuditor()
    
    print("\n📂 Loading IAM principals...")
    auditor.load_principals()
    print(f"   Found {len(auditor.principals)} principals")
    
    print("\n🔍 Running audit...")
    auditor.audit()
    
    print_report(auditor)
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(auditor.get_summary(), f, indent=2)
        print(f"\n📄 Report saved to: {args.output}")
    
    return 1 if auditor.get_summary()['critical_count'] > 0 else 0


if __name__ == "__main__":
    exit(main())
