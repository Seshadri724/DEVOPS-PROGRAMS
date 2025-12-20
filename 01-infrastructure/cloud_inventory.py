#!/usr/bin/env python3
"""
================================================================================
CLOUD RESOURCE INVENTORY & DRIFT DETECTION SYSTEM
================================================================================

RESUME BULLET POINT:
"Built a cloud resource inventory and drift detection system using Python and 
cloud APIs, identifying unmanaged resources and reducing infrastructure sprawl 
and cost leakage."

DESCRIPTION:
This tool scans cloud infrastructure to build a complete inventory of all 
resources across accounts/projects. It compares actual cloud state against 
expected state (from IaC, CMDB, or baseline) to detect:
- Unmanaged resources (not in IaC)
- Configuration drift (settings changed outside IaC)
- Orphaned resources (no owner tags)
- Shadow IT resources

USE CASES:
1. Audit cloud accounts for untracked resources
2. Detect configuration drift from Terraform/CloudFormation state
3. Find resources created manually (outside IaC)
4. Identify orphaned resources for cleanup
5. Cost optimization by finding forgotten resources

ARCHITECTURE:
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Cloud APIs    │────▶│  Inventory       │────▶│  Drift Report   │
│  (AWS/GCP/Azure)│     │  Collector       │     │  Generator      │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌──────────────────┐
                        │  Expected State  │
                        │  (IaC/Baseline)  │
                        └──────────────────┘

Author: DevOps Engineer
Version: 1.0.0
================================================================================
"""

import json
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import random


# =============================================================================
# ENUMS AND DATA STRUCTURES
# =============================================================================

class CloudProvider(Enum):
    """Supported cloud providers"""
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"


class ResourceType(Enum):
    """Types of cloud resources we track"""
    COMPUTE = "compute"           # VMs, EC2, Compute Engine
    STORAGE = "storage"           # S3, GCS, Blob Storage
    DATABASE = "database"         # RDS, CloudSQL, CosmosDB
    NETWORK = "network"           # VPC, Subnets, Load Balancers
    CONTAINER = "container"       # EKS, GKE, AKS clusters
    SERVERLESS = "serverless"     # Lambda, Cloud Functions
    IAM = "iam"                   # Users, Roles, Policies


class DriftType(Enum):
    """Types of drift detected"""
    UNMANAGED = "unmanaged"       # Resource not in IaC
    MODIFIED = "modified"         # Config differs from IaC
    ORPHANED = "orphaned"         # No owner/missing tags
    DELETED = "deleted"           # In IaC but not in cloud


@dataclass
class CloudResource:
    """
    Represents a single cloud resource.
    
    This data class captures all essential information about a cloud resource
    needed for inventory tracking and drift detection.
    """
    resource_id: str              # Unique identifier (ARN, resource ID)
    resource_type: ResourceType   # Type of resource
    provider: CloudProvider       # Cloud provider
    region: str                   # Region/location
    name: str                     # Human-readable name
    tags: Dict[str, str]          # Resource tags
    created_at: datetime          # Creation timestamp
    last_modified: datetime       # Last modification time
    configuration: Dict[str, Any] # Resource configuration
    monthly_cost: float = 0.0     # Estimated monthly cost
    
    def has_required_tags(self, required_tags: List[str]) -> bool:
        """Check if resource has all required tags"""
        return all(tag in self.tags for tag in required_tags)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            **asdict(self),
            "resource_type": self.resource_type.value,
            "provider": self.provider.value,
            "created_at": self.created_at.isoformat(),
            "last_modified": self.last_modified.isoformat(),
        }


@dataclass
class DriftResult:
    """
    Represents a detected drift between expected and actual state.
    """
    resource: CloudResource
    drift_type: DriftType
    expected_config: Optional[Dict[str, Any]] = None
    actual_config: Optional[Dict[str, Any]] = None
    differences: List[str] = field(default_factory=list)
    severity: str = "medium"      # low, medium, high, critical
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for reporting"""
        return {
            "resource_id": self.resource.resource_id,
            "resource_name": self.resource.name,
            "resource_type": self.resource.resource_type.value,
            "drift_type": self.drift_type.value,
            "differences": self.differences,
            "severity": self.severity,
            "monthly_cost_at_risk": self.resource.monthly_cost,
        }


# =============================================================================
# CLOUD API SIMULATORS (Replace with real SDK calls in production)
# =============================================================================

class CloudAPISimulator:
    """
    Simulates cloud API responses for demonstration purposes.
    
    In production, replace these methods with actual SDK calls:
    - AWS: boto3.client('ec2'), boto3.client('s3'), etc.
    - GCP: google.cloud.compute_v1, google.cloud.storage, etc.
    - Azure: azure.mgmt.compute, azure.mgmt.storage, etc.
    """
    
    @staticmethod
    def generate_demo_resources(provider: CloudProvider, count: int = 20) -> List[CloudResource]:
        """
        Generate realistic demo resources for testing.
        
        This simulates what you'd get from real cloud API calls.
        """
        resources = []
        regions = {
            CloudProvider.AWS: ["us-east-1", "us-west-2", "eu-west-1"],
            CloudProvider.GCP: ["us-central1", "europe-west1", "asia-east1"],
            CloudProvider.AZURE: ["eastus", "westeurope", "southeastasia"],
        }
        
        resource_templates = [
            # Compute instances
            (ResourceType.COMPUTE, "web-server-{}", 45.0),
            (ResourceType.COMPUTE, "api-server-{}", 65.0),
            (ResourceType.COMPUTE, "worker-node-{}", 35.0),
            # Storage
            (ResourceType.STORAGE, "app-data-bucket-{}", 12.0),
            (ResourceType.STORAGE, "logs-bucket-{}", 8.0),
            # Databases
            (ResourceType.DATABASE, "main-db-{}", 150.0),
            (ResourceType.DATABASE, "analytics-db-{}", 200.0),
            # Network
            (ResourceType.NETWORK, "main-vpc-{}", 0.0),
            (ResourceType.NETWORK, "lb-frontend-{}", 25.0),
            # Containers
            (ResourceType.CONTAINER, "k8s-cluster-{}", 300.0),
        ]
        
        # Tags that might be present (some resources will be missing tags)
        possible_tags = {
            "owner": ["platform-team", "dev-team", "data-team", None],
            "environment": ["production", "staging", "development", None],
            "cost-center": ["engineering", "infrastructure", None],
            "managed-by": ["terraform", "cloudformation", "manual", None],
        }
        
        for i in range(count):
            template = random.choice(resource_templates)
            region = random.choice(regions[provider])
            
            # Generate random tags (some will be missing required tags)
            tags = {}
            for tag_key, tag_values in possible_tags.items():
                value = random.choice(tag_values)
                if value:
                    tags[tag_key] = value
            
            # Create resource with realistic configuration
            resource = CloudResource(
                resource_id=f"{provider.value}-{template[0].value}-{i:04d}",
                resource_type=template[0],
                provider=provider,
                region=region,
                name=template[1].format(i),
                tags=tags,
                created_at=datetime.now() - timedelta(days=random.randint(1, 365)),
                last_modified=datetime.now() - timedelta(days=random.randint(0, 30)),
                configuration={
                    "size": random.choice(["small", "medium", "large"]),
                    "encrypted": random.choice([True, False]),
                    "public_access": random.choice([True, False]),
                },
                monthly_cost=template[2] * random.uniform(0.8, 1.2),
            )
            resources.append(resource)
        
        return resources


# =============================================================================
# CORE INVENTORY COLLECTOR
# =============================================================================

class CloudInventoryCollector:
    """
    Collects and manages cloud resource inventory.
    
    This class is responsible for:
    1. Fetching resources from cloud APIs
    2. Building a unified inventory across providers
    3. Caching results for performance
    4. Filtering and querying resources
    """
    
    def __init__(self, providers: List[CloudProvider] = None):
        """
        Initialize the inventory collector.
        
        Args:
            providers: List of cloud providers to scan. Defaults to all.
        """
        self.providers = providers or list(CloudProvider)
        self.inventory: Dict[str, CloudResource] = {}
        self.last_scan: Optional[datetime] = None
        
    def collect_inventory(self) -> Dict[str, CloudResource]:
        """
        Scan all configured cloud providers and collect resource inventory.
        
        Returns:
            Dictionary mapping resource IDs to CloudResource objects.
        """
        print("🔍 Starting cloud inventory collection...")
        
        for provider in self.providers:
            print(f"   Scanning {provider.value.upper()}...")
            
            # In production, replace with real API calls:
            # if provider == CloudProvider.AWS:
            #     resources = self._collect_aws_resources()
            # elif provider == CloudProvider.GCP:
            #     resources = self._collect_gcp_resources()
            # etc.
            
            # Demo: Generate simulated resources
            resources = CloudAPISimulator.generate_demo_resources(provider)
            
            for resource in resources:
                self.inventory[resource.resource_id] = resource
        
        self.last_scan = datetime.now()
        print(f"✅ Collected {len(self.inventory)} resources across {len(self.providers)} providers")
        
        return self.inventory
    
    def get_resources_by_type(self, resource_type: ResourceType) -> List[CloudResource]:
        """Filter inventory by resource type"""
        return [r for r in self.inventory.values() if r.resource_type == resource_type]
    
    def get_resources_by_provider(self, provider: CloudProvider) -> List[CloudResource]:
        """Filter inventory by cloud provider"""
        return [r for r in self.inventory.values() if r.provider == provider]
    
    def get_untagged_resources(self, required_tags: List[str]) -> List[CloudResource]:
        """Find resources missing required tags"""
        return [r for r in self.inventory.values() 
                if not r.has_required_tags(required_tags)]
    
    def calculate_total_cost(self) -> float:
        """Calculate total monthly cost of all resources"""
        return sum(r.monthly_cost for r in self.inventory.values())


# =============================================================================
# DRIFT DETECTION ENGINE
# =============================================================================

class DriftDetector:
    """
    Detects drift between expected cloud state (IaC) and actual state.
    
    This is the core intelligence of the system. It compares:
    1. What resources SHOULD exist (from Terraform state, etc.)
    2. What resources ACTUALLY exist (from cloud APIs)
    3. Whether configurations match
    """
    
    def __init__(self, 
                 inventory: Dict[str, CloudResource],
                 expected_state: Optional[Dict[str, Any]] = None):
        """
        Initialize drift detector.
        
        Args:
            inventory: Current cloud inventory from collector
            expected_state: Expected state from IaC (Terraform state, etc.)
        """
        self.inventory = inventory
        self.expected_state = expected_state or {}
        self.required_tags = ["owner", "environment", "cost-center"]
        
    def detect_all_drift(self) -> List[DriftResult]:
        """
        Run all drift detection checks.
        
        Returns:
            List of DriftResult objects describing all detected drift.
        """
        results = []
        
        print("\n🔎 Running drift detection...")
        
        # Check 1: Find unmanaged resources (not in IaC)
        results.extend(self._detect_unmanaged_resources())
        
        # Check 2: Find orphaned resources (missing required tags)
        results.extend(self._detect_orphaned_resources())
        
        # Check 3: Find configuration drift
        results.extend(self._detect_config_drift())
        
        # Check 4: Find deleted resources (in IaC but not in cloud)
        results.extend(self._detect_deleted_resources())
        
        print(f"⚠️  Found {len(results)} drift issues")
        
        return results
    
    def _detect_unmanaged_resources(self) -> List[DriftResult]:
        """
        Find resources that exist in cloud but not in IaC.
        
        These are typically resources created manually or by scripts
        that bypass the IaC workflow.
        """
        results = []
        
        for resource in self.inventory.values():
            # Check if resource is managed by IaC
            managed_by = resource.tags.get("managed-by", "").lower()
            
            if managed_by not in ["terraform", "cloudformation", "pulumi"]:
                results.append(DriftResult(
                    resource=resource,
                    drift_type=DriftType.UNMANAGED,
                    differences=["Resource not managed by IaC"],
                    severity="high" if resource.monthly_cost > 100 else "medium",
                ))
        
        return results
    
    def _detect_orphaned_resources(self) -> List[DriftResult]:
        """
        Find resources missing required tags (ownership unknown).
        
        Orphaned resources are a major source of cost leakage and
        operational confusion.
        """
        results = []
        
        for resource in self.inventory.values():
            missing_tags = [
                tag for tag in self.required_tags 
                if tag not in resource.tags
            ]
            
            if missing_tags:
                results.append(DriftResult(
                    resource=resource,
                    drift_type=DriftType.ORPHANED,
                    differences=[f"Missing required tags: {', '.join(missing_tags)}"],
                    severity="medium",
                ))
        
        return results
    
    def _detect_config_drift(self) -> List[DriftResult]:
        """
        Find resources whose configuration differs from expected state.
        
        This catches cases where someone modified a resource via console
        or CLI instead of updating IaC.
        """
        results = []
        
        for resource_id, expected in self.expected_state.items():
            if resource_id in self.inventory:
                actual = self.inventory[resource_id]
                differences = []
                
                # Compare configurations
                for key, expected_value in expected.get("configuration", {}).items():
                    actual_value = actual.configuration.get(key)
                    if actual_value != expected_value:
                        differences.append(
                            f"{key}: expected '{expected_value}', got '{actual_value}'"
                        )
                
                if differences:
                    results.append(DriftResult(
                        resource=actual,
                        drift_type=DriftType.MODIFIED,
                        expected_config=expected.get("configuration"),
                        actual_config=actual.configuration,
                        differences=differences,
                        severity="high",
                    ))
        
        return results
    
    def _detect_deleted_resources(self) -> List[DriftResult]:
        """
        Find resources defined in IaC but missing from cloud.
        
        This might indicate accidental deletion or failed deployments.
        """
        results = []
        
        for resource_id, expected in self.expected_state.items():
            if resource_id not in self.inventory:
                # Create a placeholder resource for reporting
                placeholder = CloudResource(
                    resource_id=resource_id,
                    resource_type=ResourceType.COMPUTE,  # Default
                    provider=CloudProvider.AWS,  # Default
                    region="unknown",
                    name=expected.get("name", "unknown"),
                    tags={},
                    created_at=datetime.now(),
                    last_modified=datetime.now(),
                    configuration=expected.get("configuration", {}),
                )
                
                results.append(DriftResult(
                    resource=placeholder,
                    drift_type=DriftType.DELETED,
                    expected_config=expected.get("configuration"),
                    differences=["Resource exists in IaC but not in cloud"],
                    severity="critical",
                ))
        
        return results


# =============================================================================
# REPORT GENERATOR
# =============================================================================

class ReportGenerator:
    """
    Generates human-readable and machine-readable reports.
    
    Supports multiple output formats:
    - Console (pretty-printed)
    - JSON (for integration with other tools)
    - Markdown (for documentation)
    """
    
    @staticmethod
    def generate_inventory_summary(inventory: Dict[str, CloudResource]) -> str:
        """Generate a summary of the cloud inventory"""
        
        # Count by type
        by_type = {}
        for resource in inventory.values():
            type_name = resource.resource_type.value
            by_type[type_name] = by_type.get(type_name, 0) + 1
        
        # Count by provider
        by_provider = {}
        for resource in inventory.values():
            provider_name = resource.provider.value
            by_provider[provider_name] = by_provider.get(provider_name, 0) + 1
        
        # Calculate costs
        total_cost = sum(r.monthly_cost for r in inventory.values())
        
        report = """
╔══════════════════════════════════════════════════════════════════╗
║                    CLOUD INVENTORY SUMMARY                        ║
╠══════════════════════════════════════════════════════════════════╣
"""
        report += f"║  Total Resources: {len(inventory):<46}║\n"
        report += f"║  Estimated Monthly Cost: ${total_cost:,.2f}{' ':<34}║\n"
        report += "╠══════════════════════════════════════════════════════════════════╣\n"
        report += "║  BY RESOURCE TYPE:                                               ║\n"
        
        for type_name, count in sorted(by_type.items()):
            report += f"║    {type_name:<20} {count:>5} resources{' ':<26}║\n"
        
        report += "╠══════════════════════════════════════════════════════════════════╣\n"
        report += "║  BY CLOUD PROVIDER:                                              ║\n"
        
        for provider, count in sorted(by_provider.items()):
            report += f"║    {provider.upper():<20} {count:>5} resources{' ':<26}║\n"
        
        report += "╚══════════════════════════════════════════════════════════════════╝"
        
        return report
    
    @staticmethod
    def generate_drift_report(drift_results: List[DriftResult]) -> str:
        """Generate a detailed drift report"""
        
        if not drift_results:
            return "✅ No drift detected! Infrastructure matches expected state."
        
        # Group by severity
        by_severity = {"critical": [], "high": [], "medium": [], "low": []}
        for result in drift_results:
            by_severity[result.severity].append(result)
        
        # Group by drift type
        by_type = {}
        for result in drift_results:
            type_name = result.drift_type.value
            by_type[type_name] = by_type.get(type_name, 0) + 1
        
        # Calculate cost at risk
        cost_at_risk = sum(r.resource.monthly_cost for r in drift_results)
        
        report = """
╔══════════════════════════════════════════════════════════════════╗
║                      DRIFT DETECTION REPORT                       ║
╠══════════════════════════════════════════════════════════════════╣
"""
        report += f"║  Total Issues: {len(drift_results):<49}║\n"
        report += f"║  Monthly Cost at Risk: ${cost_at_risk:,.2f}{' ':<36}║\n"
        report += "╠══════════════════════════════════════════════════════════════════╣\n"
        report += "║  BY DRIFT TYPE:                                                  ║\n"
        
        for type_name, count in sorted(by_type.items()):
            report += f"║    {type_name:<20} {count:>5} issues{' ':<29}║\n"
        
        report += "╠══════════════════════════════════════════════════════════════════╣\n"
        report += "║  BY SEVERITY:                                                    ║\n"
        
        for severity in ["critical", "high", "medium", "low"]:
            count = len(by_severity[severity])
            if count > 0:
                emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}[severity]
                report += f"║    {emoji} {severity.upper():<17} {count:>5} issues{' ':<28}║\n"
        
        report += "╠══════════════════════════════════════════════════════════════════╣\n"
        report += "║  TOP ISSUES:                                                     ║\n"
        
        # Show top 5 critical/high issues
        top_issues = sorted(drift_results, key=lambda x: 
                           {"critical": 0, "high": 1, "medium": 2, "low": 3}[x.severity])[:5]
        
        for issue in top_issues:
            report += f"║    [{issue.severity.upper()[:4]}] {issue.resource.name[:30]:<30}     ║\n"
            for diff in issue.differences[:1]:
                report += f"║           └─ {diff[:50]:<50}║\n"
        
        report += "╚══════════════════════════════════════════════════════════════════╝"
        
        return report
    
    @staticmethod
    def export_to_json(inventory: Dict[str, CloudResource], 
                       drift_results: List[DriftResult]) -> str:
        """Export full results to JSON for integration with other tools"""
        
        output = {
            "scan_timestamp": datetime.now().isoformat(),
            "summary": {
                "total_resources": len(inventory),
                "total_drift_issues": len(drift_results),
                "total_monthly_cost": sum(r.monthly_cost for r in inventory.values()),
            },
            "inventory": [r.to_dict() for r in inventory.values()],
            "drift_results": [r.to_dict() for r in drift_results],
        }
        
        return json.dumps(output, indent=2, default=str)


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """
    Main entry point for the Cloud Inventory & Drift Detection tool.
    
    This function:
    1. Parses command-line arguments
    2. Runs inventory collection
    3. Performs drift detection
    4. Generates reports
    """
    
    # -------------------------------------------------------------------------
    # ARGUMENT PARSING
    # -------------------------------------------------------------------------
    parser = argparse.ArgumentParser(
        description="Cloud Resource Inventory & Drift Detection System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --demo                    Run with simulated data
  %(prog)s --provider aws            Scan only AWS
  %(prog)s --output report.json      Export results to JSON
  %(prog)s --check-tags              Focus on tag compliance
        """
    )
    
    parser.add_argument(
        "--demo", 
        action="store_true",
        help="Run in demo mode with simulated cloud data"
    )
    
    parser.add_argument(
        "--provider",
        choices=["aws", "gcp", "azure", "all"],
        default="all",
        help="Cloud provider to scan (default: all)"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        help="Output file for JSON export"
    )
    
    parser.add_argument(
        "--check-tags",
        action="store_true",
        help="Focus on tag compliance checking"
    )
    
    parser.add_argument(
        "--required-tags",
        nargs="+",
        default=["owner", "environment", "cost-center"],
        help="Required tags to check (default: owner, environment, cost-center)"
    )
    
    args = parser.parse_args()
    
    # -------------------------------------------------------------------------
    # INITIALIZATION
    # -------------------------------------------------------------------------
    print("=" * 70)
    print("   CLOUD RESOURCE INVENTORY & DRIFT DETECTION SYSTEM")
    print("=" * 70)
    print(f"   Scan Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Configure providers
    if args.provider == "all":
        providers = list(CloudProvider)
    else:
        providers = [CloudProvider(args.provider)]
    
    # -------------------------------------------------------------------------
    # INVENTORY COLLECTION
    # -------------------------------------------------------------------------
    collector = CloudInventoryCollector(providers=providers)
    inventory = collector.collect_inventory()
    
    # Print inventory summary
    print(ReportGenerator.generate_inventory_summary(inventory))
    
    # -------------------------------------------------------------------------
    # DRIFT DETECTION
    # -------------------------------------------------------------------------
    
    # Simulate expected state (in production, load from Terraform state file)
    expected_state = {}  # Empty for demo, would be loaded from terraform.tfstate
    
    detector = DriftDetector(inventory, expected_state)
    detector.required_tags = args.required_tags
    drift_results = detector.detect_all_drift()
    
    # Print drift report
    print(ReportGenerator.generate_drift_report(drift_results))
    
    # -------------------------------------------------------------------------
    # TAG COMPLIANCE CHECK (if requested)
    # -------------------------------------------------------------------------
    if args.check_tags:
        untagged = collector.get_untagged_resources(args.required_tags)
        print(f"\n📋 TAG COMPLIANCE:")
        print(f"   Resources missing required tags: {len(untagged)}")
        for resource in untagged[:10]:  # Show first 10
            missing = [t for t in args.required_tags if t not in resource.tags]
            print(f"   - {resource.name}: missing {', '.join(missing)}")
    
    # -------------------------------------------------------------------------
    # EXPORT (if requested)
    # -------------------------------------------------------------------------
    if args.output:
        json_output = ReportGenerator.export_to_json(inventory, drift_results)
        with open(args.output, 'w') as f:
            f.write(json_output)
        print(f"\n📄 Results exported to: {args.output}")
    
    # -------------------------------------------------------------------------
    # SUMMARY
    # -------------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("   SCAN COMPLETE")
    print("=" * 70)
    print(f"   Total Resources: {len(inventory)}")
    print(f"   Drift Issues: {len(drift_results)}")
    print(f"   Monthly Cost: ${collector.calculate_total_cost():,.2f}")
    print("=" * 70)
    
    # Return exit code based on drift severity
    critical_issues = [r for r in drift_results if r.severity == "critical"]
    return 1 if critical_issues else 0


if __name__ == "__main__":
    exit(main())
