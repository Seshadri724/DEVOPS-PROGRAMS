#!/usr/bin/env python3
"""
================================================================================
GRACEFUL DEGRADATION IMPLEMENTATION
================================================================================

RESUME BULLET POINT:
"Built graceful degradation implementations that shed non-critical features 
under load, maintaining core service availability."

Author: DevOps Engineer | Version: 1.0.0
================================================================================
"""

import argparse
import json
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum


class FeaturePriority(Enum):
    CRITICAL = 1    # Never disable
    HIGH = 2        # Disable last
    MEDIUM = 3      # Disable under moderate load
    LOW = 4         # Disable first


class DegradationLevel(Enum):
    NORMAL = 0
    LEVEL_1 = 1     # Disable low priority
    LEVEL_2 = 2     # Disable medium priority
    LEVEL_3 = 3     # Emergency - only critical


@dataclass
class Feature:
    """Service feature that can be degraded"""
    name: str
    priority: FeaturePriority
    cpu_impact: float
    enabled: bool = True


class GracefulDegradation:
    """Manages graceful degradation"""
    
    THRESHOLDS = {
        DegradationLevel.LEVEL_1: 70,   # CPU > 70%
        DegradationLevel.LEVEL_2: 85,   # CPU > 85%
        DegradationLevel.LEVEL_3: 95,   # CPU > 95%
    }
    
    def __init__(self):
        self.features: List[Feature] = []
        self.current_level = DegradationLevel.NORMAL
    
    def load_features(self) -> List[Feature]:
        """Load feature definitions"""
        self.features = [
            Feature("core_api", FeaturePriority.CRITICAL, 10),
            Feature("authentication", FeaturePriority.CRITICAL, 5),
            Feature("payment_processing", FeaturePriority.HIGH, 15),
            Feature("search", FeaturePriority.MEDIUM, 20),
            Feature("recommendations", FeaturePriority.LOW, 25),
            Feature("analytics_tracking", FeaturePriority.LOW, 15),
            Feature("social_features", FeaturePriority.LOW, 10),
        ]
        return self.features
    
    def evaluate_degradation(self, cpu_usage: float) -> DegradationLevel:
        """Determine degradation level based on load"""
        if cpu_usage >= self.THRESHOLDS[DegradationLevel.LEVEL_3]:
            return DegradationLevel.LEVEL_3
        elif cpu_usage >= self.THRESHOLDS[DegradationLevel.LEVEL_2]:
            return DegradationLevel.LEVEL_2
        elif cpu_usage >= self.THRESHOLDS[DegradationLevel.LEVEL_1]:
            return DegradationLevel.LEVEL_1
        return DegradationLevel.NORMAL
    
    def apply_degradation(self, level: DegradationLevel) -> List[str]:
        """Apply degradation level, returns disabled features"""
        disabled = []
        
        for feature in self.features:
            if level == DegradationLevel.NORMAL:
                feature.enabled = True
            elif level == DegradationLevel.LEVEL_1:
                feature.enabled = feature.priority.value <= FeaturePriority.MEDIUM.value
            elif level == DegradationLevel.LEVEL_2:
                feature.enabled = feature.priority.value <= FeaturePriority.HIGH.value
            elif level == DegradationLevel.LEVEL_3:
                feature.enabled = feature.priority == FeaturePriority.CRITICAL
            
            if not feature.enabled:
                disabled.append(feature.name)
        
        self.current_level = level
        return disabled
    
    def calculate_load_reduction(self) -> float:
        """Calculate CPU reduction from disabled features"""
        return sum(f.cpu_impact for f in self.features if not f.enabled)
    
    def get_status(self) -> Dict:
        """Get degradation status"""
        return {
            "level": self.current_level.name,
            "enabled_features": sum(1 for f in self.features if f.enabled),
            "disabled_features": sum(1 for f in self.features if not f.enabled),
            "load_reduction": self.calculate_load_reduction(),
        }


def print_report(degradation: GracefulDegradation, cpu: float):
    """Print degradation report"""
    status = degradation.get_status()
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║           GRACEFUL DEGRADATION STATUS                        ║
╠══════════════════════════════════════════════════════════════╣
║  Current CPU: {cpu:.1f}%{' ':<44}║
║  Degradation Level: {status['level']:<39}║
║  Load Reduction: {status['load_reduction']:.0f}%{' ':<41}║
╠══════════════════════════════════════════════════════════════╣
║  FEATURE STATUS:                                             ║""")
    
    for f in degradation.features:
        icon = "🟢" if f.enabled else "🔴"
        priority = f.priority.name
        print(f"║    {icon} {f.name:<25} [{priority:<8}] {f.cpu_impact:>2.0f}% CPU ║")
    
    print("╚══════════════════════════════════════════════════════════════╝")


def main():
    parser = argparse.ArgumentParser(description="Graceful Degradation")
    parser.add_argument("--demo", action="store_true")
    parser.add_argument("--cpu", type=float, default=75, help="Current CPU usage")
    args = parser.parse_args()
    
    print("=" * 60)
    print("   GRACEFUL DEGRADATION IMPLEMENTATION")
    print("=" * 60)
    
    degradation = GracefulDegradation()
    degradation.load_features()
    
    print(f"\n📊 Evaluating degradation for CPU: {args.cpu}%")
    level = degradation.evaluate_degradation(args.cpu)
    disabled = degradation.apply_degradation(level)
    
    if disabled:
        print(f"   ⚠️ Disabling {len(disabled)} features: {', '.join(disabled)}")
    
    print_report(degradation, args.cpu)
    
    return 0


if __name__ == "__main__":
    exit(main())
