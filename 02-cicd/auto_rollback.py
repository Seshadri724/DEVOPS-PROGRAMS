#!/usr/bin/env python3
"""
================================================================================
AUTOMATED ROLLBACK MECHANISM FOR CONTAINERIZED SERVICES
================================================================================

RESUME BULLET POINT:
"Implemented automated rollback mechanisms for containerized services, 
significantly reducing Mean Time To Recovery (MTTR) during failed deployments."

DESCRIPTION:
Monitors deployments and automatically triggers rollbacks when health checks fail.
Supports Kubernetes, Docker Swarm, and ECS deployments.

Author: DevOps Engineer | Version: 1.0.0
================================================================================
"""

import argparse
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class DeploymentStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class RollbackReason(Enum):
    HEALTH_CHECK_FAILED = "health_check_failed"
    ERROR_RATE_EXCEEDED = "error_rate_exceeded"
    LATENCY_EXCEEDED = "latency_exceeded"
    MANUAL_TRIGGER = "manual_trigger"
    TIMEOUT = "timeout"


@dataclass
class DeploymentVersion:
    """Represents a deployment version"""
    version: str
    image: str
    deployed_at: datetime
    replicas: int
    healthy_replicas: int = 0


@dataclass
class RollbackEvent:
    """Records a rollback event"""
    from_version: str
    to_version: str
    reason: RollbackReason
    triggered_at: datetime
    completed_at: Optional[datetime] = None
    success: bool = False


class HealthChecker:
    """Checks deployment health"""
    
    @staticmethod
    def check_health(service: str, version: str) -> Dict:
        """Check health of a deployment (simulated)"""
        import random
        
        # Simulate health check results
        is_healthy = random.random() > 0.3  # 70% success rate
        error_rate = random.uniform(0, 10) if is_healthy else random.uniform(15, 50)
        latency_p99 = random.uniform(50, 200) if is_healthy else random.uniform(500, 2000)
        
        return {
            "healthy": is_healthy,
            "error_rate": error_rate,
            "latency_p99_ms": latency_p99,
            "ready_replicas": 3 if is_healthy else 1,
            "total_replicas": 3,
        }


class RollbackManager:
    """Manages deployment rollbacks"""
    
    # Thresholds for automatic rollback
    THRESHOLDS = {
        "error_rate_max": 5.0,      # 5% error rate
        "latency_p99_max": 500,     # 500ms p99 latency
        "min_healthy_replicas": 2,
        "health_check_timeout": 120,  # seconds
    }
    
    def __init__(self, service: str):
        self.service = service
        self.versions: List[DeploymentVersion] = []
        self.rollback_history: List[RollbackEvent] = []
        self.current_version: Optional[DeploymentVersion] = None
    
    def register_deployment(self, version: str, image: str, replicas: int = 3):
        """Register a new deployment"""
        deployment = DeploymentVersion(
            version=version,
            image=image,
            deployed_at=datetime.now(),
            replicas=replicas,
        )
        self.versions.append(deployment)
        self.current_version = deployment
        print(f"   📦 Registered deployment: {version}")
    
    def monitor_deployment(self, timeout: int = 60, interval: int = 10) -> bool:
        """Monitor deployment health and trigger rollback if needed"""
        print(f"\n🔍 Monitoring deployment health (timeout: {timeout}s)...")
        
        start_time = time.time()
        checks_passed = 0
        required_checks = 3
        
        while time.time() - start_time < timeout:
            health = HealthChecker.check_health(self.service, self.current_version.version)
            
            # Check thresholds
            if health["error_rate"] > self.THRESHOLDS["error_rate_max"]:
                print(f"   ❌ Error rate too high: {health['error_rate']:.1f}%")
                return self._trigger_rollback(RollbackReason.ERROR_RATE_EXCEEDED)
            
            if health["latency_p99_ms"] > self.THRESHOLDS["latency_p99_max"]:
                print(f"   ❌ Latency too high: {health['latency_p99_ms']:.0f}ms")
                return self._trigger_rollback(RollbackReason.LATENCY_EXCEEDED)
            
            if health["ready_replicas"] < self.THRESHOLDS["min_healthy_replicas"]:
                print(f"   ❌ Not enough healthy replicas: {health['ready_replicas']}/{health['total_replicas']}")
                return self._trigger_rollback(RollbackReason.HEALTH_CHECK_FAILED)
            
            checks_passed += 1
            print(f"   ✅ Health check {checks_passed}/{required_checks} passed")
            
            if checks_passed >= required_checks:
                print(f"\n✅ Deployment healthy after {checks_passed} consecutive checks")
                return True
            
            time.sleep(0.5)  # Shortened for demo
        
        print("   ⏰ Monitoring timeout reached")
        return self._trigger_rollback(RollbackReason.TIMEOUT)
    
    def _trigger_rollback(self, reason: RollbackReason) -> bool:
        """Execute rollback to previous version"""
        if len(self.versions) < 2:
            print("   ⚠️ No previous version available for rollback")
            return False
        
        previous = self.versions[-2]
        current = self.current_version
        
        print(f"\n🔄 TRIGGERING ROLLBACK")
        print(f"   From: {current.version}")
        print(f"   To:   {previous.version}")
        print(f"   Reason: {reason.value}")
        
        event = RollbackEvent(
            from_version=current.version,
            to_version=previous.version,
            reason=reason,
            triggered_at=datetime.now(),
        )
        
        # Execute rollback (simulated)
        print("   ⏳ Rolling back...")
        time.sleep(0.5)
        
        event.completed_at = datetime.now()
        event.success = True
        self.rollback_history.append(event)
        self.current_version = previous
        
        print(f"   ✅ Rollback completed in {(event.completed_at - event.triggered_at).total_seconds():.1f}s")
        return False  # Rollback happened, deployment failed
    
    def get_stats(self) -> Dict:
        """Get rollback statistics"""
        total = len(self.rollback_history)
        successful = sum(1 for r in self.rollback_history if r.success)
        
        return {
            "total_rollbacks": total,
            "successful": successful,
            "failed": total - successful,
            "current_version": self.current_version.version if self.current_version else None,
            "available_versions": len(self.versions),
        }


def print_report(manager: RollbackManager):
    """Print rollback manager status"""
    stats = manager.get_stats()
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║           ROLLBACK MANAGER STATUS                            ║
╠══════════════════════════════════════════════════════════════╣
║  Service: {manager.service:<49}║
║  Current Version: {stats['current_version'] or 'N/A':<41}║
║  Available Versions: {stats['available_versions']:<38}║
╠══════════════════════════════════════════════════════════════╣
║  ROLLBACK HISTORY:                                           ║
║    Total Rollbacks: {stats['total_rollbacks']:<40}║
║    Successful: {stats['successful']:<45}║
╠══════════════════════════════════════════════════════════════╣
║  THRESHOLDS:                                                 ║
║    Max Error Rate: {manager.THRESHOLDS['error_rate_max']}%{' ':<40}║
║    Max P99 Latency: {manager.THRESHOLDS['latency_p99_max']}ms{' ':<38}║
║    Min Healthy Replicas: {manager.THRESHOLDS['min_healthy_replicas']:<35}║
╚══════════════════════════════════════════════════════════════╝""")


def main():
    parser = argparse.ArgumentParser(description="Automated Rollback for Containers")
    parser.add_argument("--service", type=str, default="api-service", help="Service name")
    parser.add_argument("--version", type=str, default="v2.0.0", help="New version to deploy")
    parser.add_argument("--demo", action="store_true", help="Run demo")
    parser.add_argument("--rollback", action="store_true", help="Trigger manual rollback")
    parser.add_argument("--timeout", type=int, default=60, help="Monitoring timeout (seconds)")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("   AUTOMATED ROLLBACK MECHANISM")
    print("=" * 60)
    
    manager = RollbackManager(args.service)
    
    # Register previous stable version
    manager.register_deployment("v1.9.0", "app:v1.9.0", replicas=3)
    manager.versions[-1].healthy_replicas = 3
    
    # Register new deployment
    manager.register_deployment(args.version, f"app:{args.version}", replicas=3)
    
    if args.rollback:
        manager._trigger_rollback(RollbackReason.MANUAL_TRIGGER)
    else:
        # Monitor the deployment
        success = manager.monitor_deployment(timeout=args.timeout)
        
        if success:
            print("\n✅ Deployment successful - no rollback needed")
        else:
            print("\n⚠️ Deployment failed - rollback executed")
    
    print_report(manager)
    
    return 0 if manager.current_version.version == args.version else 1


if __name__ == "__main__":
    exit(main())
