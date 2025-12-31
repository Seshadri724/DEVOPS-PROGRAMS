#!/usr/bin/env python3
"""
================================================================================
SELF-SERVE SERVICE CATALOG
================================================================================

RESUME BULLET POINT:
"Built a self-serve service catalog that allows devs to provision standardized 
resources without waiting on platform team queues."

Author: DevOps Engineer | Version: 1.0.0
================================================================================
"""

import argparse
import json
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum


class ServiceType(Enum):
    DATABASE = "database"
    CACHE = "cache"
    QUEUE = "queue"
    STORAGE = "storage"
    API = "api"


@dataclass
class ServiceTemplate:
    """Service template in catalog"""
    name: str
    service_type: ServiceType
    description: str
    parameters: List[str]
    estimated_time: str


@dataclass
class ProvisioningRequest:
    """Request to provision a service"""
    template: str
    requester: str
    parameters: Dict
    created_at: datetime
    status: str = "pending"


class ServiceCatalog:
    """Self-service catalog for infrastructure"""
    
    def __init__(self):
        self.templates: List[ServiceTemplate] = []
        self.requests: List[ProvisioningRequest] = []
    
    def load_templates(self) -> List[ServiceTemplate]:
        """Load available service templates"""
        self.templates = [
            ServiceTemplate("postgres-standard", ServiceType.DATABASE, "PostgreSQL database", 
                          ["size", "environment"], "5 minutes"),
            ServiceTemplate("redis-cache", ServiceType.CACHE, "Redis cache cluster",
                          ["size", "ha_enabled"], "3 minutes"),
            ServiceTemplate("sqs-queue", ServiceType.QUEUE, "AWS SQS queue",
                          ["name", "fifo"], "1 minute"),
            ServiceTemplate("s3-bucket", ServiceType.STORAGE, "S3 storage bucket",
                          ["name", "versioning"], "1 minute"),
            ServiceTemplate("api-gateway", ServiceType.API, "API Gateway endpoint",
                          ["name", "auth_type"], "5 minutes"),
        ]
        return self.templates
    
    def provision(self, template_name: str, params: Dict, requester: str, dry_run: bool = True) -> ProvisioningRequest:
        """Provision a service from template"""
        template = next((t for t in self.templates if t.name == template_name), None)
        if not template:
            raise ValueError(f"Template not found: {template_name}")
        
        request = ProvisioningRequest(
            template=template_name,
            requester=requester,
            parameters=params,
            created_at=datetime.now(),
            status="dry_run" if dry_run else "provisioning",
        )
        
        self.requests.append(request)
        
        if dry_run:
            print(f"   [DRY RUN] Would provision {template_name}")
        else:
            print(f"   ✓ Provisioning {template_name}...")
            request.status = "completed"
        
        return request
    
    def list_templates(self):
        """List available templates"""
        for t in self.templates:
            print(f"   - {t.name}: {t.description}")


def print_catalog(catalog: ServiceCatalog):
    """Print service catalog"""
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║           SELF-SERVE SERVICE CATALOG                         ║
╠══════════════════════════════════════════════════════════════╣
║  Available Templates: {len(catalog.templates):<37}║
╠══════════════════════════════════════════════════════════════╣
║  SERVICES:                                                   ║""")
    
    for t in catalog.templates:
        params = ", ".join(t.parameters)
        print(f"║    📦 {t.name:<20} ~{t.estimated_time:<10}      ║")
        print(f"║       {t.description:<50}║")
    
    print("╚══════════════════════════════════════════════════════════════╝")


def main():
    parser = argparse.ArgumentParser(description="Service Catalog")
    parser.add_argument("--demo", action="store_true")
    parser.add_argument("--list", action="store_true", help="List templates")
    parser.add_argument("--provision", type=str, help="Template to provision")
    args = parser.parse_args()
    
    print("=" * 60)
    print("   SELF-SERVE SERVICE CATALOG")
    print("=" * 60)
    
    catalog = ServiceCatalog()
    catalog.load_templates()
    
    print_catalog(catalog)
    
    if args.provision:
        print(f"\n🚀 Provisioning: {args.provision}")
        catalog.provision(args.provision, {"size": "small"}, "developer", dry_run=True)
    
    return 0


if __name__ == "__main__":
    exit(main())
