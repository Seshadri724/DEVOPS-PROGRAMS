#!/usr/bin/env python3
"""
================================================================================
ALERT DEDUPLICATION ENGINE
================================================================================

RESUME BULLET POINT:
"Built an alert deduplication engine that groups similar alerts to reduce 
on-call noise and improve incident response efficiency."

DESCRIPTION:
Groups similar alerts together to prevent alert storms from overwhelming
on-call engineers, while ensuring no critical issues are missed.

Author: DevOps Engineer | Version: 1.0.0
================================================================================
"""

import argparse
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List
from dataclasses import dataclass, field
from enum import Enum
import random


class AlertSeverity(Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


@dataclass
class Alert:
    """Single alert"""
    id: str
    name: str
    severity: AlertSeverity
    service: str
    message: str
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class AlertGroup:
    """Group of deduplicated alerts"""
    signature: str
    name: str
    severity: AlertSeverity
    count: int
    first_seen: datetime
    last_seen: datetime
    services: List[str]
    alerts: List[Alert]


class AlertDeduplicator:
    """Deduplicates and groups similar alerts"""
    
    # Keys used for grouping (fingerprint)
    GROUPING_KEYS = ["name", "severity"]
    
    SUPPRESSION_WINDOW = timedelta(minutes=5)
    
    def __init__(self):
        self.groups: Dict[str, AlertGroup] = {}
        self.suppressed_count = 0
    
    def _get_signature(self, alert: Alert) -> str:
        """Generate fingerprint for grouping"""
        fingerprint = f"{alert.name}|{alert.severity.value}"
        return hashlib.md5(fingerprint.encode()).hexdigest()[:12]
    
    def process_alert(self, alert: Alert) -> bool:
        """Process alert, returns True if alert should be sent"""
        signature = self._get_signature(alert)
        
        if signature in self.groups:
            group = self.groups[signature]
            time_since_last = alert.timestamp - group.last_seen
            
            # Suppress if within window
            if time_since_last < self.SUPPRESSION_WINDOW:
                group.count += 1
                group.last_seen = alert.timestamp
                if alert.service not in group.services:
                    group.services.append(alert.service)
                group.alerts.append(alert)
                self.suppressed_count += 1
                return False  # Suppressed
            else:
                # Window expired, treat as new
                group.count += 1
                group.last_seen = alert.timestamp
                group.alerts.append(alert)
                return True  # Send summary
        else:
            # New alert type
            self.groups[signature] = AlertGroup(
                signature=signature,
                name=alert.name,
                severity=alert.severity,
                count=1,
                first_seen=alert.timestamp,
                last_seen=alert.timestamp,
                services=[alert.service],
                alerts=[alert],
            )
            return True  # Send new alert
    
    def get_active_groups(self) -> List[AlertGroup]:
        """Get currently active alert groups"""
        now = datetime.now()
        active_window = timedelta(minutes=30)
        return [g for g in self.groups.values() 
                if now - g.last_seen < active_window]
    
    def get_summary(self) -> Dict:
        """Get deduplication summary"""
        total_processed = sum(g.count for g in self.groups.values())
        unique_alerts = len(self.groups)
        
        return {
            "total_alerts_processed": total_processed,
            "unique_alert_types": unique_alerts,
            "alerts_suppressed": self.suppressed_count,
            "suppression_rate": f"{(self.suppressed_count / total_processed * 100):.1f}%" if total_processed else "0%",
            "active_groups": len(self.get_active_groups()),
        }


class AlertGenerator:
    """Generates sample alerts for testing"""
    
    ALERT_TYPES = [
        ("HighErrorRate", AlertSeverity.CRITICAL, "Error rate > 5%"),
        ("HighLatency", AlertSeverity.WARNING, "P99 latency > 500ms"),
        ("PodCrashLooping", AlertSeverity.CRITICAL, "Pod restarting"),
        ("HighCPU", AlertSeverity.WARNING, "CPU > 80%"),
        ("DiskSpaceLow", AlertSeverity.WARNING, "Disk < 10%"),
    ]
    
    @staticmethod
    def generate(count: int = 50) -> List[Alert]:
        """Generate sample alerts"""
        alerts = []
        services = ["api", "auth", "payment", "worker"]
        
        for i in range(count):
            template = random.choice(AlertGenerator.ALERT_TYPES)
            
            alerts.append(Alert(
                id=f"alert-{i:04d}",
                name=template[0],
                severity=template[1],
                service=random.choice(services),
                message=template[2],
                timestamp=datetime.now() - timedelta(minutes=random.randint(0, 30)),
            ))
        
        return sorted(alerts, key=lambda x: x.timestamp)


def print_report(dedup: AlertDeduplicator):
    """Print deduplication report"""
    summary = dedup.get_summary()
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║              ALERT DEDUPLICATION REPORT                      ║
╠══════════════════════════════════════════════════════════════╣
║  Total Alerts Processed: {summary['total_alerts_processed']:<34}║
║  Unique Alert Types: {summary['unique_alert_types']:<38}║
║  Alerts Suppressed: {summary['alerts_suppressed']:<39}║
║  Suppression Rate: {summary['suppression_rate']:<40}║
╠══════════════════════════════════════════════════════════════╣
║  ACTIVE ALERT GROUPS:                                        ║""")
    
    severity_icons = {"critical": "🔴", "warning": "🟡", "info": "🔵"}
    
    for group in sorted(dedup.get_active_groups(), key=lambda x: x.count, reverse=True):
        icon = severity_icons[group.severity.value]
        print(f"║    {icon} {group.name:<25} x{group.count:<4} {', '.join(group.services[:3]):<15}║")
    
    print("╚══════════════════════════════════════════════════════════════╝")
    print(f"\n💡 Reduced {summary['total_alerts_processed']} alerts to {summary['unique_alert_types']} groups")


def main():
    parser = argparse.ArgumentParser(description="Alert Deduplication Engine")
    parser.add_argument("--demo", action="store_true", help="Run demo")
    parser.add_argument("--count", type=int, default=50, help="Number of alerts")
    parser.add_argument("--output", type=str, help="JSON output file")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("   ALERT DEDUPLICATION ENGINE")
    print("=" * 60)
    
    dedup = AlertDeduplicator()
    
    print("\n📥 Processing incoming alerts...")
    alerts = AlertGenerator.generate(args.count)
    
    sent_count = 0
    for alert in alerts:
        if dedup.process_alert(alert):
            sent_count += 1
    
    print(f"   Processed {len(alerts)} alerts, sent {sent_count} notifications")
    
    print_report(dedup)
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(dedup.get_summary(), f, indent=2)
        print(f"\n📄 Report saved to: {args.output}")
    
    return 0


if __name__ == "__main__":
    exit(main())
