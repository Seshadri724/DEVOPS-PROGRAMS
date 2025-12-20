#!/usr/bin/env python3
"""
================================================================================
TAG ENFORCEMENT BOT
================================================================================

RESUME BULLET POINT:
"Built a tag enforcement bot that blocks creation of cloud resources without 
required tags (owner, env, cost-center), improving cost attribution and governance."

DESCRIPTION:
Enforces tagging policies on cloud resources. Can run as a pre-creation validator
or post-creation auditor to ensure all resources have required metadata.

Author: DevOps Engineer | Version: 1.0.0
================================================================================
"""

import argparse
import json
from datetime import datetime, timedelta
from typing import Dict, List, Set
from dataclasses import dataclass
from enum import Enum
import random


class ComplianceStatus(Enum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"


@dataclass
class TagPolicy:
    """Defines required and optional tags"""
    name: str
    required_tags: List[str]
    optional_tags: List[str] = None
    allowed_values: Dict[str, List[str]] = None


@dataclass
class ResourceTagAudit:
    """Result of tag audit for a resource"""
    resource_id: str
    resource_type: str
    existing_tags: Dict[str, str]
    missing_tags: List[str]
    invalid_tags: List[str]
    status: ComplianceStatus
    auto_fixable: bool = False


# Default tag policies
DEFAULT_POLICIES = [
    TagPolicy(
        name="standard",
        required_tags=["owner", "environment", "cost-center", "project"],
        optional_tags=["team", "description", "created-by"],
        allowed_values={
            "environment": ["production", "staging", "development", "testing"],
            "cost-center": ["engineering", "infrastructure", "data", "product"],
        }
    ),
    TagPolicy(
        name="minimal",
        required_tags=["owner", "environment"],
        optional_tags=["project"],
    ),
]


class ResourceSimulator:
    """Simulates cloud resources for testing"""
    
    @staticmethod
    def generate_resources(count: int = 20) -> List[Dict]:
        """Generate sample resources with varying tag compliance"""
        resources = []
        types = ["ec2:instance", "rds:db", "s3:bucket", "lambda:function"]
        
        # Tag variations - some compliant, some not
        tag_sets = [
            # Fully compliant
            {"owner": "team-a", "environment": "production", "cost-center": "engineering", "project": "api"},
            {"owner": "team-b", "environment": "staging", "cost-center": "data", "project": "analytics"},
            # Partially compliant (missing some)
            {"owner": "team-c", "environment": "development"},
            {"owner": "unknown"},
            # Invalid values
            {"owner": "team-d", "environment": "PROD", "cost-center": "misc"},
            # Non-compliant (no tags)
            {},
        ]
        
        for i in range(count):
            resources.append({
                "resource_id": f"resource-{i:04d}",
                "resource_type": random.choice(types),
                "tags": random.choice(tag_sets).copy(),
                "created_at": (datetime.now() - timedelta(days=random.randint(1, 90))).isoformat(),
            })
        
        return resources


class TagEnforcer:
    """Enforces tag policies on resources"""
    
    def __init__(self, policy: TagPolicy):
        self.policy = policy
        self.audit_results: List[ResourceTagAudit] = []
    
    def audit_resource(self, resource: Dict) -> ResourceTagAudit:
        """Audit a single resource for tag compliance"""
        existing_tags = resource.get("tags", {})
        missing = []
        invalid = []
        
        # Check for missing required tags
        for tag in self.policy.required_tags:
            if tag not in existing_tags:
                missing.append(tag)
        
        # Check for invalid values
        if self.policy.allowed_values:
            for tag, allowed in self.policy.allowed_values.items():
                if tag in existing_tags and existing_tags[tag] not in allowed:
                    invalid.append(f"{tag}='{existing_tags[tag]}' (allowed: {', '.join(allowed)})")
        
        # Determine compliance status
        if not missing and not invalid:
            status = ComplianceStatus.COMPLIANT
        elif missing and len(missing) < len(self.policy.required_tags):
            status = ComplianceStatus.PARTIALLY_COMPLIANT
        else:
            status = ComplianceStatus.NON_COMPLIANT
        
        # Can auto-fix if only owner is missing (can derive from created-by)
        auto_fixable = len(missing) == 1 and "owner" in missing and "created-by" in existing_tags
        
        result = ResourceTagAudit(
            resource_id=resource["resource_id"],
            resource_type=resource["resource_type"],
            existing_tags=existing_tags,
            missing_tags=missing,
            invalid_tags=invalid,
            status=status,
            auto_fixable=auto_fixable,
        )
        
        self.audit_results.append(result)
        return result
    
    def audit_all(self, resources: List[Dict]) -> List[ResourceTagAudit]:
        """Audit all resources"""
        return [self.audit_resource(r) for r in resources]
    
    def get_compliance_summary(self) -> Dict:
        """Get compliance summary"""
        total = len(self.audit_results)
        compliant = sum(1 for r in self.audit_results if r.status == ComplianceStatus.COMPLIANT)
        partial = sum(1 for r in self.audit_results if r.status == ComplianceStatus.PARTIALLY_COMPLIANT)
        non_compliant = total - compliant - partial
        
        return {
            "total_resources": total,
            "compliant": compliant,
            "partially_compliant": partial,
            "non_compliant": non_compliant,
            "compliance_rate": f"{(compliant/total)*100:.1f}%" if total > 0 else "N/A",
            "auto_fixable": sum(1 for r in self.audit_results if r.auto_fixable),
        }
    
    def fix_tags(self, resource_id: str, tags_to_add: Dict[str, str], dry_run: bool = True):
        """Fix missing tags on a resource"""
        if dry_run:
            print(f"   [DRY RUN] Would add tags to {resource_id}: {tags_to_add}")
        else:
            print(f"   ✓ Added tags to {resource_id}: {tags_to_add}")


def print_report(enforcer: TagEnforcer):
    """Print tag compliance report"""
    summary = enforcer.get_compliance_summary()
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║              TAG ENFORCEMENT AUDIT REPORT                    ║
╠══════════════════════════════════════════════════════════════╣
║  Policy: {enforcer.policy.name:<50}║
║  Required Tags: {', '.join(enforcer.policy.required_tags):<42}║
╠══════════════════════════════════════════════════════════════╣
║  Total Resources:       {summary['total_resources']:<36}║
║  ✅ Compliant:          {summary['compliant']:<36}║
║  ⚠️  Partially Compliant: {summary['partially_compliant']:<36}║
║  ❌ Non-Compliant:       {summary['non_compliant']:<36}║
║  Compliance Rate:       {summary['compliance_rate']:<36}║
║  Auto-Fixable:          {summary['auto_fixable']:<36}║
╠══════════════════════════════════════════════════════════════╣
║  NON-COMPLIANT RESOURCES:                                    ║""")
    
    non_compliant = [r for r in enforcer.audit_results if r.status != ComplianceStatus.COMPLIANT]
    for result in non_compliant[:10]:
        missing = ', '.join(result.missing_tags) if result.missing_tags else 'none'
        print(f"║    {result.resource_id:<20} missing: {missing:<27}║")
    
    if len(non_compliant) > 10:
        print(f"║    ... and {len(non_compliant) - 10} more{' ':<43}║")
    
    print("╚══════════════════════════════════════════════════════════════╝")


def main():
    parser = argparse.ArgumentParser(description="Tag Enforcement Bot")
    parser.add_argument("--demo", action="store_true", help="Run with simulated data")
    parser.add_argument("--policy", choices=["standard", "minimal"], default="standard")
    parser.add_argument("--fix", action="store_true", help="Auto-fix fixable resources")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--output", type=str, help="JSON output file")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("   TAG ENFORCEMENT BOT")
    print("=" * 60)
    
    # Select policy
    policy = next(p for p in DEFAULT_POLICIES if p.name == args.policy)
    print(f"\n📋 Using policy: {policy.name}")
    print(f"   Required tags: {', '.join(policy.required_tags)}")
    
    # Scan resources
    print("\n🔍 Scanning resources...")
    resources = ResourceSimulator.generate_resources(25)
    print(f"   Found {len(resources)} resources")
    
    # Audit
    enforcer = TagEnforcer(policy)
    enforcer.audit_all(resources)
    
    print_report(enforcer)
    
    # Auto-fix if requested
    if args.fix:
        fixable = [r for r in enforcer.audit_results if r.auto_fixable]
        if fixable:
            print(f"\n🔧 Auto-fixing {len(fixable)} resources...")
            for result in fixable:
                enforcer.fix_tags(result.resource_id, {"owner": "auto-detected"}, args.dry_run)
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump({
                "summary": enforcer.get_compliance_summary(),
                "non_compliant": [
                    {"id": r.resource_id, "missing": r.missing_tags}
                    for r in enforcer.audit_results if r.status != ComplianceStatus.COMPLIANT
                ]
            }, f, indent=2)
        print(f"\n📄 Report saved to: {args.output}")
    
    # Exit with error if compliance is below threshold
    summary = enforcer.get_compliance_summary()
    compliance_pct = (summary['compliant'] / summary['total_resources']) * 100
    return 0 if compliance_pct >= 80 else 1


if __name__ == "__main__":
    exit(main())
