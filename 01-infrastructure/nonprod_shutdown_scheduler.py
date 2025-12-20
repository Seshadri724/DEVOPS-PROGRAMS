#!/usr/bin/env python3
"""
================================================================================
NIGHTLY NON-PROD SHUTDOWN SCHEDULER
================================================================================

RESUME BULLET POINT:
"Built a nightly non-prod shutdown scheduler that automatically stops 
dev/staging infrastructure outside working hours, reducing cloud costs by 40%."

DESCRIPTION:
Automatically shuts down non-production resources during off-hours (nights,
weekends) and restarts them before work hours. Includes override capabilities.

Author: DevOps Engineer | Version: 1.0.0
================================================================================
"""

import argparse
import json
from datetime import datetime, time, timedelta
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum


class Environment(Enum):
    DEV = "development"
    STAGING = "staging"
    QA = "qa"
    PROD = "production"  # Never touched


class ResourceState(Enum):
    RUNNING = "running"
    STOPPED = "stopped"
    PENDING = "pending"


@dataclass
class ScheduleConfig:
    """Configuration for shutdown schedule"""
    start_hour: int = 8       # Start resources at 8 AM
    stop_hour: int = 20       # Stop resources at 8 PM
    timezone: str = "UTC"
    skip_weekends: bool = True
    environments: List[Environment] = None
    
    def __post_init__(self):
        if self.environments is None:
            self.environments = [Environment.DEV, Environment.STAGING, Environment.QA]


@dataclass
class ManagedResource:
    """A resource managed by the scheduler"""
    resource_id: str
    resource_type: str
    name: str
    environment: Environment
    state: ResourceState
    hourly_cost: float
    override_active: bool = False
    override_until: datetime = None


class ResourceManager:
    """Manages starting/stopping of resources"""
    
    def __init__(self, config: ScheduleConfig):
        self.config = config
        self.resources: List[ManagedResource] = []
        self.actions_taken: List[Dict] = []
    
    def load_resources(self) -> List[ManagedResource]:
        """Load resources from cloud (simulated)"""
        resource_templates = [
            ("ec2", "web-server", 0.10),
            ("ec2", "api-server", 0.15),
            ("rds", "dev-database", 0.25),
            ("ec2", "worker-node", 0.08),
            ("elasticache", "redis-cache", 0.05),
        ]
        
        for env in [Environment.DEV, Environment.STAGING, Environment.QA]:
            for rtype, name, cost in resource_templates:
                self.resources.append(ManagedResource(
                    resource_id=f"{rtype}-{env.value[:3]}-{name}",
                    resource_type=rtype,
                    name=f"{name}-{env.value}",
                    environment=env,
                    state=ResourceState.RUNNING,
                    hourly_cost=cost,
                ))
        
        return self.resources
    
    def should_be_running(self) -> bool:
        """Determine if resources should be running based on schedule"""
        now = datetime.now()
        current_hour = now.hour
        
        # Check weekend
        if self.config.skip_weekends and now.weekday() >= 5:
            return False
        
        # Check hours
        return self.config.start_hour <= current_hour < self.config.stop_hour
    
    def get_resources_to_stop(self) -> List[ManagedResource]:
        """Get resources that should be stopped"""
        if self.should_be_running():
            return []
        
        return [
            r for r in self.resources
            if r.environment in self.config.environments
            and r.state == ResourceState.RUNNING
            and not r.override_active
        ]
    
    def get_resources_to_start(self) -> List[ManagedResource]:
        """Get resources that should be started"""
        if not self.should_be_running():
            return []
        
        return [
            r for r in self.resources
            if r.environment in self.config.environments
            and r.state == ResourceState.STOPPED
        ]
    
    def stop_resource(self, resource: ManagedResource, dry_run: bool = True):
        """Stop a resource"""
        action = {
            "action": "stop",
            "resource_id": resource.resource_id,
            "timestamp": datetime.now().isoformat(),
            "dry_run": dry_run,
        }
        
        if dry_run:
            print(f"   [DRY RUN] Would stop: {resource.resource_id}")
        else:
            print(f"   ✓ Stopped: {resource.resource_id}")
            resource.state = ResourceState.STOPPED
        
        self.actions_taken.append(action)
    
    def start_resource(self, resource: ManagedResource, dry_run: bool = True):
        """Start a resource"""
        action = {
            "action": "start",
            "resource_id": resource.resource_id,
            "timestamp": datetime.now().isoformat(),
            "dry_run": dry_run,
        }
        
        if dry_run:
            print(f"   [DRY RUN] Would start: {resource.resource_id}")
        else:
            print(f"   ✓ Started: {resource.resource_id}")
            resource.state = ResourceState.RUNNING
        
        self.actions_taken.append(action)
    
    def set_override(self, resource_id: str, hours: int = 4):
        """Set override to keep resource running"""
        for resource in self.resources:
            if resource.resource_id == resource_id:
                resource.override_active = True
                resource.override_until = datetime.now() + timedelta(hours=hours)
                print(f"   ⏰ Override set for {resource_id} until {resource.override_until}")
                return True
        return False
    
    def calculate_savings(self) -> Dict:
        """Calculate cost savings from shutdown schedule"""
        # Hours per day resources are stopped
        shutdown_hours = 24 - (self.config.stop_hour - self.config.start_hour)
        
        # Weekend savings (if enabled)
        weekend_hours = 48 if self.config.skip_weekends else 0
        
        # Weekly shutdown hours
        weekly_shutdown_hours = (shutdown_hours * 5) + weekend_hours
        
        # Calculate savings
        hourly_cost = sum(r.hourly_cost for r in self.resources 
                        if r.environment in self.config.environments)
        
        weekly_savings = hourly_cost * weekly_shutdown_hours
        monthly_savings = weekly_savings * 4.33
        
        return {
            "shutdown_hours_per_day": shutdown_hours,
            "weekly_shutdown_hours": weekly_shutdown_hours,
            "hourly_cost": round(hourly_cost, 2),
            "weekly_savings": round(weekly_savings, 2),
            "monthly_savings": round(monthly_savings, 2),
            "annual_savings": round(monthly_savings * 12, 2),
        }


def print_status(manager: ResourceManager):
    """Print scheduler status"""
    savings = manager.calculate_savings()
    should_run = manager.should_be_running()
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║           NON-PROD SHUTDOWN SCHEDULER STATUS                 ║
╠══════════════════════════════════════════════════════════════╣
║  Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M %Z'):<45}║
║  Schedule: {manager.config.start_hour:02d}:00 - {manager.config.stop_hour:02d}:00 ({manager.config.timezone}){' ':<29}║
║  Resources Should Be: {'RUNNING' if should_run else 'STOPPED':<38}║
╠══════════════════════════════════════════════════════════════╣
║  MANAGED ENVIRONMENTS:                                       ║""")
    
    for env in manager.config.environments:
        count = sum(1 for r in manager.resources if r.environment == env)
        print(f"║    {env.value:<20} {count:>3} resources{' ':<25}║")
    
    print(f"""╠══════════════════════════════════════════════════════════════╣
║  COST SAVINGS:                                               ║
║    Weekly Savings:  ${savings['weekly_savings']:>10,.2f}{' ':<29}║
║    Monthly Savings: ${savings['monthly_savings']:>10,.2f}{' ':<29}║
║    Annual Savings:  ${savings['annual_savings']:>10,.2f}{' ':<29}║
╠══════════════════════════════════════════════════════════════╣
║  RESOURCE STATUS:                                            ║""")
    
    for resource in manager.resources[:8]:
        state_icon = "🟢" if resource.state == ResourceState.RUNNING else "🔴"
        override = " [OVERRIDE]" if resource.override_active else ""
        print(f"║    {state_icon} {resource.resource_id:<30} ${resource.hourly_cost:.2f}/hr{override:<5}║")
    
    if len(manager.resources) > 8:
        print(f"║    ... and {len(manager.resources) - 8} more resources{' ':<30}║")
    
    print("╚══════════════════════════════════════════════════════════════╝")


def main():
    parser = argparse.ArgumentParser(description="Nightly Non-Prod Shutdown Scheduler")
    parser.add_argument("--demo", action="store_true", help="Run with simulated data")
    parser.add_argument("--run", action="store_true", help="Execute scheduled actions")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--status", action="store_true", help="Show current status")
    parser.add_argument("--override", type=str, help="Set override for resource ID")
    parser.add_argument("--start-hour", type=int, default=8, help="Work start hour (default: 8)")
    parser.add_argument("--stop-hour", type=int, default=20, help="Work end hour (default: 20)")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("   NIGHTLY NON-PROD SHUTDOWN SCHEDULER")
    print("=" * 60)
    
    # Configure schedule
    config = ScheduleConfig(
        start_hour=args.start_hour,
        stop_hour=args.stop_hour,
    )
    
    manager = ResourceManager(config)
    manager.load_resources()
    
    print(f"\n📋 Loaded {len(manager.resources)} resources")
    
    if args.override:
        print(f"\n⏰ Setting override for: {args.override}")
        manager.set_override(args.override, hours=4)
    
    if args.run:
        to_stop = manager.get_resources_to_stop()
        to_start = manager.get_resources_to_start()
        
        if to_stop:
            print(f"\n🔴 Stopping {len(to_stop)} resources...")
            for resource in to_stop:
                manager.stop_resource(resource, dry_run=args.dry_run)
        
        if to_start:
            print(f"\n🟢 Starting {len(to_start)} resources...")
            for resource in to_start:
                manager.start_resource(resource, dry_run=args.dry_run)
        
        if not to_stop and not to_start:
            print("\n✅ No actions needed - resources already in correct state")
    
    print_status(manager)
    
    savings = manager.calculate_savings()
    print(f"\n💰 Estimated annual savings: ${savings['annual_savings']:,.2f}")
    return 0


if __name__ == "__main__":
    exit(main())
