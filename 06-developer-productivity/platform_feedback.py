#!/usr/bin/env python3
"""
================================================================================
PLATFORM FEEDBACK COLLECTOR
================================================================================

RESUME BULLET POINT:
"Built a platform feedback collector that surfaces developer experience pain 
points, enabling data-driven platform improvements."

Author: DevOps Engineer | Version: 1.0.0
================================================================================
"""

import argparse
import json
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum
from collections import Counter


class Category(Enum):
    CI_CD = "ci_cd"
    INFRASTRUCTURE = "infrastructure"
    TOOLING = "tooling"
    DOCUMENTATION = "documentation"
    SECURITY = "security"
    OTHER = "other"


@dataclass
class Feedback:
    """Developer feedback entry"""
    id: int
    category: Category
    rating: int  # 1-5
    comment: str
    submitted_at: datetime
    team: str


class FeedbackCollector:
    """Collects and analyzes platform feedback"""
    
    def __init__(self):
        self.feedback: List[Feedback] = []
    
    def load_feedback(self) -> List[Feedback]:
        """Load feedback (simulated)"""
        self.feedback = [
            Feedback(1, Category.CI_CD, 2, "Builds take too long", datetime.now(), "api-team"),
            Feedback(2, Category.CI_CD, 3, "Flaky tests blocking deploys", datetime.now(), "web-team"),
            Feedback(3, Category.TOOLING, 4, "K8s dashboard is helpful", datetime.now(), "api-team"),
            Feedback(4, Category.DOCUMENTATION, 2, "Runbooks outdated", datetime.now(), "platform"),
            Feedback(5, Category.INFRASTRUCTURE, 1, "Staging env always broken", datetime.now(), "mobile-team"),
            Feedback(6, Category.SECURITY, 4, "SSO setup was smooth", datetime.now(), "web-team"),
        ]
        return self.feedback
    
    def get_analysis(self) -> Dict:
        """Analyze feedback trends"""
        by_category = Counter(f.category.value for f in self.feedback)
        avg_by_category = {}
        for cat in Category:
            ratings = [f.rating for f in self.feedback if f.category == cat]
            avg_by_category[cat.value] = sum(ratings) / len(ratings) if ratings else 0
        
        pain_points = [f for f in self.feedback if f.rating <= 2]
        
        return {
            "total_feedback": len(self.feedback),
            "avg_rating": sum(f.rating for f in self.feedback) / len(self.feedback),
            "by_category": dict(by_category),
            "avg_by_category": avg_by_category,
            "pain_points": len(pain_points),
            "top_pain_points": [f.comment for f in pain_points],
        }


def print_report(collector: FeedbackCollector):
    """Print feedback report"""
    analysis = collector.get_analysis()
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║           PLATFORM FEEDBACK REPORT                           ║
╠══════════════════════════════════════════════════════════════╣
║  Total Submissions: {analysis['total_feedback']:<39}║
║  Avg Rating: {analysis['avg_rating']:.1f}/5{' ':<44}║
║  Pain Points: {analysis['pain_points']:<45}║
╠══════════════════════════════════════════════════════════════╣
║  BY CATEGORY (Avg Rating):                                   ║""")
    
    for cat, avg in analysis['avg_by_category'].items():
        if avg > 0:
            bar = "★" * int(avg) + "☆" * (5 - int(avg))
            print(f"║    {cat:<20} {bar} ({avg:.1f}){' ':<18}║")
    
    print(f"""╠══════════════════════════════════════════════════════════════╣
║  TOP PAIN POINTS:                                            ║""")
    
    for pp in analysis['top_pain_points'][:3]:
        print(f"║    ❌ {pp:<52}║")
    
    print("╚══════════════════════════════════════════════════════════════╝")


def main():
    parser = argparse.ArgumentParser(description="Feedback Collector")
    parser.add_argument("--demo", action="store_true")
    parser.add_argument("--output", type=str)
    args = parser.parse_args()
    
    print("=" * 60)
    print("   PLATFORM FEEDBACK COLLECTOR")
    print("=" * 60)
    
    collector = FeedbackCollector()
    collector.load_feedback()
    
    print_report(collector)
    
    return 0


if __name__ == "__main__":
    exit(main())
