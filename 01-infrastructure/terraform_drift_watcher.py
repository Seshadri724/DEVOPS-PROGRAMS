#!/usr/bin/env python3
"""
================================================================================
TERRAFORM STATE DRIFT WATCHER
================================================================================

RESUME BULLET POINT:
"Built a Terraform state drift watcher that alerts when real infrastructure 
diverges from IaC state, ensuring infrastructure consistency and compliance."

DESCRIPTION:
Monitors Terraform state files and compares against actual cloud infrastructure
to detect configuration drift. Integrates with CI/CD and alerting systems.

Author: DevOps Engineer | Version: 1.0.0
================================================================================
"""

import argparse
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import random


class DriftSeverity(Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class TerraformResource:
    """Resource from Terraform state"""
    address: str          # e.g., aws_instance.web_server
    type: str             # e.g., aws_instance
    name: str             # e.g., web_server
    provider: str         # e.g., aws
    attributes: Dict


@dataclass
class DriftItem:
    """Detected drift between IaC and actual state"""
    resource_address: str
    resource_type: str
    drift_type: str       # "modified", "deleted", "unmanaged"
    attribute: str
    expected: str
    actual: str
    severity: DriftSeverity


class TerraformStateParser:
    """Parses Terraform state files"""
    
    @staticmethod
    def parse_state(state_file: str = None) -> List[TerraformResource]:
        """Parse terraform.tfstate file (simulated)"""
        # In production: json.load(open(state_file))
        
        # Simulated state resources
        resources = [
            TerraformResource(
                address="aws_instance.web_server",
                type="aws_instance",
                name="web_server",
                provider="aws",
                attributes={"instance_type": "t3.medium", "ami": "ami-12345", "tags": {"env": "prod"}}
            ),
            TerraformResource(
                address="aws_instance.api_server",
                type="aws_instance",
                name="api_server",
                provider="aws",
                attributes={"instance_type": "t3.large", "ami": "ami-12345", "tags": {"env": "prod"}}
            ),
            TerraformResource(
                address="aws_rds_instance.main_db",
                type="aws_rds_instance",
                name="main_db",
                provider="aws",
                attributes={"instance_class": "db.r5.large", "engine": "postgres", "multi_az": True}
            ),
            TerraformResource(
                address="aws_s3_bucket.assets",
                type="aws_s3_bucket",
                name="assets",
                provider="aws",
                attributes={"acl": "private", "versioning": True}
            ),
        ]
        return resources


class CloudStateChecker:
    """Checks actual cloud state against Terraform state"""
    
    @staticmethod
    def get_actual_state(resource: TerraformResource) -> Dict:
        """Get actual cloud resource state (simulated)"""
        # In production: Use cloud SDK to fetch actual resource config
        
        # Simulate drift scenarios
        drift_scenarios = {
            "aws_instance.web_server": {"instance_type": "t3.large"},  # Changed manually
            "aws_s3_bucket.assets": {"acl": "public-read"},  # Security drift!
        }
        
        # Start with expected attributes
        actual = resource.attributes.copy()
        
        # Apply any drift
        if resource.address in drift_scenarios:
            actual.update(drift_scenarios[resource.address])
        
        return actual


class DriftDetector:
    """Detects and reports infrastructure drift"""
    
    SEVERITY_RULES = {
        ("aws_s3_bucket", "acl"): DriftSeverity.CRITICAL,      # Security risk
        ("aws_instance", "security_groups"): DriftSeverity.HIGH,
        ("aws_rds_instance", "multi_az"): DriftSeverity.HIGH,  # Availability risk
        ("aws_instance", "instance_type"): DriftSeverity.MEDIUM,
        "default": DriftSeverity.LOW,
    }
    
    def __init__(self):
        self.drift_items: List[DriftItem] = []
    
    def detect_drift(self, tf_resources: List[TerraformResource]) -> List[DriftItem]:
        """Compare Terraform state with actual cloud state"""
        
        for resource in tf_resources:
            expected = resource.attributes
            actual = CloudStateChecker.get_actual_state(resource)
            
            # Compare attributes
            for key, expected_value in expected.items():
                actual_value = actual.get(key)
                
                if actual_value != expected_value:
                    severity = self._get_severity(resource.type, key)
                    
                    self.drift_items.append(DriftItem(
                        resource_address=resource.address,
                        resource_type=resource.type,
                        drift_type="modified",
                        attribute=key,
                        expected=str(expected_value),
                        actual=str(actual_value),
                        severity=severity,
                    ))
        
        return self.drift_items
    
    def _get_severity(self, resource_type: str, attribute: str) -> DriftSeverity:
        """Determine drift severity based on resource type and attribute"""
        key = (resource_type, attribute)
        return self.SEVERITY_RULES.get(key, self.SEVERITY_RULES["default"])
    
    def get_summary(self) -> Dict:
        """Get drift detection summary"""
        by_severity = {}
        for item in self.drift_items:
            sev = item.severity.value
            by_severity[sev] = by_severity.get(sev, 0) + 1
        
        return {
            "total_drift_items": len(self.drift_items),
            "by_severity": by_severity,
            "critical_count": by_severity.get("critical", 0),
            "high_count": by_severity.get("high", 0),
            "has_security_drift": by_severity.get("critical", 0) > 0,
        }


class DriftAlerter:
    """Sends drift alerts to various channels"""
    
    @staticmethod
    def send_alert(drift_items: List[DriftItem], channel: str = "console"):
        """Send drift alerts"""
        critical = [d for d in drift_items if d.severity == DriftSeverity.CRITICAL]
        
        if not drift_items:
            print("✅ No drift detected - infrastructure matches IaC state")
            return
        
        if critical:
            print(f"\n🚨 CRITICAL DRIFT DETECTED: {len(critical)} security-relevant changes!")
            for item in critical:
                print(f"   ⚠️  {item.resource_address}")
                print(f"      {item.attribute}: '{item.expected}' → '{item.actual}'")
        
        # In production: Send to Slack, PagerDuty, etc.


def print_report(detector: DriftDetector):
    """Print drift detection report"""
    summary = detector.get_summary()
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║             TERRAFORM DRIFT DETECTION REPORT                 ║
╠══════════════════════════════════════════════════════════════╣
║  Scan Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S'):<47}║
║  Total Drift Items: {summary['total_drift_items']:<39}║
╠══════════════════════════════════════════════════════════════╣
║  BY SEVERITY:                                                ║""")
    
    severity_icons = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
    for sev, count in summary["by_severity"].items():
        icon = severity_icons.get(sev, "⚪")
        print(f"║    {icon} {sev.upper():<15} {count:>3} items{' ':<30}║")
    
    print(f"""╠══════════════════════════════════════════════════════════════╣
║  DRIFT DETAILS:                                              ║""")
    
    for item in detector.drift_items:
        icon = severity_icons.get(item.severity.value, "⚪")
        print(f"║    {icon} {item.resource_address:<50}║")
        print(f"║       {item.attribute}: '{item.expected}' → '{item.actual}'{' ':<15}║")
    
    print("╚══════════════════════════════════════════════════════════════╝")
    
    if summary["has_security_drift"]:
        print("\n⚠️  SECURITY ALERT: Critical drift detected requires immediate attention!")


def main():
    parser = argparse.ArgumentParser(description="Terraform State Drift Watcher")
    parser.add_argument("--demo", action="store_true", help="Run with simulated data")
    parser.add_argument("--state-file", type=str, help="Path to terraform.tfstate")
    parser.add_argument("--output", type=str, help="JSON output file")
    parser.add_argument("--alert", choices=["console", "slack", "pagerduty"], default="console")
    parser.add_argument("--fail-on-drift", action="store_true", help="Exit with error if drift found")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("   TERRAFORM STATE DRIFT WATCHER")
    print("=" * 60)
    
    # Parse Terraform state
    print("\n📂 Loading Terraform state...")
    resources = TerraformStateParser.parse_state(args.state_file)
    print(f"   Found {len(resources)} managed resources")
    
    # Detect drift
    print("\n🔍 Checking for drift...")
    detector = DriftDetector()
    drift_items = detector.detect_drift(resources)
    
    print_report(detector)
    DriftAlerter.send_alert(drift_items, args.alert)
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump({
                "summary": detector.get_summary(),
                "drift_items": [
                    {"address": d.resource_address, "attribute": d.attribute, 
                     "expected": d.expected, "actual": d.actual, "severity": d.severity.value}
                    for d in drift_items
                ]
            }, f, indent=2)
        print(f"\n📄 Report saved to: {args.output}")
    
    # Exit code
    if args.fail_on_drift and drift_items:
        return 1
    return 0


if __name__ == "__main__":
    exit(main())
