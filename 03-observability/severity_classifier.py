#!/usr/bin/env python3
"""
================================================================================
INCIDENT SEVERITY CLASSIFIER
================================================================================

RESUME BULLET POINT:
"Built an incident severity classifier that auto-tags incidents based on 
blast radius and customer impact, enabling faster prioritization."

DESCRIPTION:
Automatically classifies incident severity based on affected services, 
customer impact, and business criticality metrics.

Author: DevOps Engineer | Version: 1.0.0
================================================================================
"""

import argparse
import json
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum


class Severity(Enum):
    SEV1 = "SEV1"  # Critical - Major outage
    SEV2 = "SEV2"  # High - Significant impact
    SEV3 = "SEV3"  # Medium - Limited impact
    SEV4 = "SEV4"  # Low - Minimal impact


@dataclass
class IncidentSignals:
    """Signals used for classification"""
    affected_services: List[str]
    error_rate: float
    affected_users_pct: float
    revenue_impacting: bool
    service_criticality: str  # critical, high, medium, low
    time_of_day: str  # business_hours, off_hours


@dataclass
class ClassificationResult:
    """Result of severity classification"""
    severity: Severity
    score: int
    factors: List[str]
    recommended_responders: List[str]


class SeverityClassifier:
    """Classifies incident severity"""
    
    CRITICALITY_WEIGHTS = {
        "critical": 30,
        "high": 20,
        "medium": 10,
        "low": 5,
    }
    
    RESPONDERS = {
        Severity.SEV1: ["on-call-primary", "on-call-secondary", "engineering-lead", "management"],
        Severity.SEV2: ["on-call-primary", "on-call-secondary"],
        Severity.SEV3: ["on-call-primary"],
        Severity.SEV4: ["service-owner"],
    }
    
    def classify(self, signals: IncidentSignals) -> ClassificationResult:
        """Classify incident severity based on signals"""
        score = 0
        factors = []
        
        # Factor 1: Service criticality
        criticality_score = self.CRITICALITY_WEIGHTS.get(signals.service_criticality, 5)
        score += criticality_score
        factors.append(f"Service criticality: {signals.service_criticality} (+{criticality_score})")
        
        # Factor 2: Error rate
        if signals.error_rate > 50:
            score += 30
            factors.append(f"Error rate {signals.error_rate:.1f}% (severe, +30)")
        elif signals.error_rate > 20:
            score += 20
            factors.append(f"Error rate {signals.error_rate:.1f}% (high, +20)")
        elif signals.error_rate > 5:
            score += 10
            factors.append(f"Error rate {signals.error_rate:.1f}% (elevated, +10)")
        
        # Factor 3: User impact
        if signals.affected_users_pct > 50:
            score += 25
            factors.append(f"Users affected: {signals.affected_users_pct:.1f}% (+25)")
        elif signals.affected_users_pct > 10:
            score += 15
            factors.append(f"Users affected: {signals.affected_users_pct:.1f}% (+15)")
        
        # Factor 4: Revenue impact
        if signals.revenue_impacting:
            score += 20
            factors.append("Revenue impacting (+20)")
        
        # Factor 5: Blast radius (number of affected services)
        if len(signals.affected_services) > 3:
            score += 15
            factors.append(f"Multiple services affected ({len(signals.affected_services)}, +15)")
        
        # Factor 6: Time of day
        if signals.time_of_day == "business_hours":
            score += 5
            factors.append("Business hours (+5)")
        
        # Determine severity from score
        if score >= 70:
            severity = Severity.SEV1
        elif score >= 45:
            severity = Severity.SEV2
        elif score >= 25:
            severity = Severity.SEV3
        else:
            severity = Severity.SEV4
        
        return ClassificationResult(
            severity=severity,
            score=score,
            factors=factors,
            recommended_responders=self.RESPONDERS[severity],
        )


def get_demo_incidents() -> List[IncidentSignals]:
    """Get demo incident signals"""
    return [
        IncidentSignals(
            affected_services=["payment", "orders", "api"],
            error_rate=75.0,
            affected_users_pct=60.0,
            revenue_impacting=True,
            service_criticality="critical",
            time_of_day="business_hours",
        ),
        IncidentSignals(
            affected_services=["search"],
            error_rate=15.0,
            affected_users_pct=5.0,
            revenue_impacting=False,
            service_criticality="medium",
            time_of_day="off_hours",
        ),
        IncidentSignals(
            affected_services=["notifications"],
            error_rate=5.0,
            affected_users_pct=2.0,
            revenue_impacting=False,
            service_criticality="low",
            time_of_day="off_hours",
        ),
    ]


def print_classification(signals: IncidentSignals, result: ClassificationResult):
    """Print classification result"""
    sev_icons = {"SEV1": "🔴", "SEV2": "🟠", "SEV3": "🟡", "SEV4": "🟢"}
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║           INCIDENT SEVERITY CLASSIFICATION                   ║
╠══════════════════════════════════════════════════════════════╣
║  Affected Services: {', '.join(signals.affected_services):<39}║
║  Error Rate: {signals.error_rate:.1f}%{' ':<47}║
║  Users Affected: {signals.affected_users_pct:.1f}%{' ':<44}║
╠══════════════════════════════════════════════════════════════╣
║  CLASSIFICATION: {sev_icons[result.severity.value]} {result.severity.value} (Score: {result.score}){' ':<27}║
╠══════════════════════════════════════════════════════════════╣
║  SCORING FACTORS:                                            ║""")
    
    for factor in result.factors:
        print(f"║    • {factor:<53}║")
    
    print(f"""╠══════════════════════════════════════════════════════════════╣
║  RECOMMENDED RESPONDERS:                                     ║
║    {', '.join(result.recommended_responders):<55}║
╚══════════════════════════════════════════════════════════════╝""")


def main():
    parser = argparse.ArgumentParser(description="Incident Severity Classifier")
    parser.add_argument("--demo", action="store_true", help="Run demo")
    parser.add_argument("--output", type=str, help="JSON output file")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("   INCIDENT SEVERITY CLASSIFIER")
    print("=" * 60)
    
    classifier = SeverityClassifier()
    incidents = get_demo_incidents()
    
    print(f"\n📋 Classifying {len(incidents)} incidents...")
    
    results = []
    for signals in incidents:
        result = classifier.classify(signals)
        results.append((signals, result))
        print_classification(signals, result)
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump([
                {"severity": r[1].severity.value, "score": r[1].score, "factors": r[1].factors}
                for r in results
            ], f, indent=2)
        print(f"\n📄 Results saved to: {args.output}")
    
    return 0


if __name__ == "__main__":
    exit(main())
