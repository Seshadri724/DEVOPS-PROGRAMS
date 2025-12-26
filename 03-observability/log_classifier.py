#!/usr/bin/env python3
"""
================================================================================
LOG ERROR CLASSIFICATION & NOISE REDUCTION SYSTEM
================================================================================

RESUME BULLET POINT:
"Created a log error classification and noise-reduction system, reducing alert 
fatigue and improving on-call signal quality."

DESCRIPTION:
Classifies log errors by severity, groups similar errors, and filters noise
to surface actionable issues while reducing alert fatigue.

Author: DevOps Engineer | Version: 1.0.0
================================================================================
"""

import argparse
import json
import re
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict
import random


class LogLevel(Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class LogEntry:
    """A single log entry"""
    timestamp: datetime
    level: LogLevel
    service: str
    message: str
    trace_id: str = None


@dataclass
class ErrorCluster:
    """Group of similar errors"""
    pattern: str
    signature: str
    count: int
    first_seen: datetime
    last_seen: datetime
    samples: List[LogEntry]
    is_noise: bool = False


class LogClassifier:
    """Classifies and groups log entries"""
    
    # Known noise patterns to filter
    NOISE_PATTERNS = [
        r"health check",
        r"connection reset by peer",
        r"context canceled",
        r"request canceled",
        r"EOF",
    ]
    
    # Patterns to normalize for grouping
    NORMALIZE_PATTERNS = [
        (r'\d{4}-\d{2}-\d{2}', '<DATE>'),
        (r'\d{2}:\d{2}:\d{2}', '<TIME>'),
        (r'\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b', '<UUID>'),
        (r'\b\d+\.\d+\.\d+\.\d+\b', '<IP>'),
        (r'\b\d+\b', '<NUM>'),
    ]
    
    def __init__(self):
        self.clusters: Dict[str, ErrorCluster] = {}
        self.noise_count = 0
    
    def classify(self, entry: LogEntry) -> str:
        """Classify a log entry and return its cluster signature"""
        # Check if noise
        if self._is_noise(entry):
            self.noise_count += 1
            return None
        
        # Normalize message for grouping
        normalized = self._normalize_message(entry.message)
        signature = hashlib.md5(normalized.encode()).hexdigest()[:12]
        
        if signature in self.clusters:
            cluster = self.clusters[signature]
            cluster.count += 1
            cluster.last_seen = entry.timestamp
            if len(cluster.samples) < 3:
                cluster.samples.append(entry)
        else:
            self.clusters[signature] = ErrorCluster(
                pattern=normalized,
                signature=signature,
                count=1,
                first_seen=entry.timestamp,
                last_seen=entry.timestamp,
                samples=[entry],
            )
        
        return signature
    
    def _is_noise(self, entry: LogEntry) -> bool:
        """Check if entry matches known noise patterns"""
        msg_lower = entry.message.lower()
        return any(re.search(p, msg_lower) for p in self.NOISE_PATTERNS)
    
    def _normalize_message(self, message: str) -> str:
        """Normalize message for pattern matching"""
        result = message
        for pattern, replacement in self.NORMALIZE_PATTERNS:
            result = re.sub(pattern, replacement, result)
        return result
    
    def get_actionable_errors(self, min_count: int = 2) -> List[ErrorCluster]:
        """Get errors that need attention (not noise, occurred multiple times)"""
        return [c for c in self.clusters.values() 
                if not c.is_noise and c.count >= min_count]
    
    def get_summary(self) -> Dict:
        """Get classification summary"""
        total_errors = sum(c.count for c in self.clusters.values())
        actionable = self.get_actionable_errors()
        
        return {
            "total_entries": total_errors + self.noise_count,
            "unique_patterns": len(self.clusters),
            "noise_filtered": self.noise_count,
            "actionable_clusters": len(actionable),
            "noise_reduction_pct": round(self.noise_count / (total_errors + self.noise_count) * 100, 1) if total_errors + self.noise_count > 0 else 0,
        }


class LogGenerator:
    """Generates sample logs for testing"""
    
    ERROR_TEMPLATES = [
        "Database connection failed: timeout after <NUM>ms",
        "API request failed: status <NUM>",
        "User authentication failed for user_id: <UUID>",
        "Payment processing error: transaction <UUID>",
        "health check passed",  # Noise
        "connection reset by peer",  # Noise
        "File not found: /path/to/file",
        "Rate limit exceeded for IP <IP>",
    ]
    
    @staticmethod
    def generate(count: int = 100) -> List[LogEntry]:
        """Generate sample log entries"""
        entries = []
        services = ["api", "auth", "payment", "worker"]
        
        for _ in range(count):
            template = random.choice(LogGenerator.ERROR_TEMPLATES)
            message = template
            message = re.sub('<NUM>', str(random.randint(1, 10000)), message)
            message = re.sub('<UUID>', f"{random.randint(0, 0xffffffff):08x}-0000-0000-0000-000000000000", message)
            message = re.sub('<IP>', f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,255)}", message)
            
            entries.append(LogEntry(
                timestamp=datetime.now() - timedelta(minutes=random.randint(0, 60)),
                level=random.choice([LogLevel.ERROR, LogLevel.WARNING, LogLevel.CRITICAL]),
                service=random.choice(services),
                message=message,
                trace_id=f"trace-{random.randint(1000, 9999)}",
            ))
        
        return entries


def print_report(classifier: LogClassifier):
    """Print classification report"""
    summary = classifier.get_summary()
    actionable = classifier.get_actionable_errors()
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║         LOG ERROR CLASSIFICATION REPORT                      ║
╠══════════════════════════════════════════════════════════════╣
║  Total Entries Processed: {summary['total_entries']:<33}║
║  Unique Error Patterns: {summary['unique_patterns']:<35}║
║  Noise Filtered: {summary['noise_filtered']:<42}║
║  Noise Reduction: {summary['noise_reduction_pct']}%{' ':<38}║
║  Actionable Clusters: {summary['actionable_clusters']:<37}║
╠══════════════════════════════════════════════════════════════╣
║  TOP ERROR PATTERNS:                                         ║""")
    
    for cluster in sorted(actionable, key=lambda x: x.count, reverse=True)[:5]:
        print(f"║    [{cluster.count:>4}x] {cluster.pattern[:45]:<45}║")
    
    print("╚══════════════════════════════════════════════════════════════╝")
    
    if actionable:
        print(f"\n🎯 {len(actionable)} unique error patterns need attention")


def main():
    parser = argparse.ArgumentParser(description="Log Error Classification")
    parser.add_argument("--demo", action="store_true", help="Run with demo data")
    parser.add_argument("--count", type=int, default=100, help="Number of logs to process")
    parser.add_argument("--output", type=str, help="JSON output file")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("   LOG ERROR CLASSIFICATION & NOISE REDUCTION")
    print("=" * 60)
    
    print("\n📂 Loading log entries...")
    entries = LogGenerator.generate(args.count)
    print(f"   Loaded {len(entries)} entries")
    
    print("\n🔍 Classifying errors...")
    classifier = LogClassifier()
    for entry in entries:
        classifier.classify(entry)
    
    print_report(classifier)
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(classifier.get_summary(), f, indent=2)
        print(f"\n📄 Report saved to: {args.output}")
    
    return 0


if __name__ == "__main__":
    exit(main())
