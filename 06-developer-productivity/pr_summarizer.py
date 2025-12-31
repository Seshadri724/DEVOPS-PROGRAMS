#!/usr/bin/env python3
"""
================================================================================
AUTO PR SUMMARIZER / RELEASE NOTES DRAFTER
================================================================================

RESUME BULLET POINT:
"Built an auto PR summarizer that drafts release notes from merged PRs, 
saving hours of manual changelog writing."

Author: DevOps Engineer | Version: 1.0.0
================================================================================
"""

import argparse
import json
import re
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum


class ChangeType(Enum):
    FEATURE = "feature"
    BUGFIX = "bugfix"
    BREAKING = "breaking"
    DOCS = "docs"
    CHORE = "chore"
    SECURITY = "security"


@dataclass
class PullRequest:
    """Pull request data"""
    number: int
    title: str
    author: str
    labels: List[str]
    merged_at: datetime
    body: str


class PRSummarizer:
    """Summarizes PRs into release notes"""
    
    LABEL_MAPPING = {
        "feature": ChangeType.FEATURE,
        "enhancement": ChangeType.FEATURE,
        "bug": ChangeType.BUGFIX,
        "fix": ChangeType.BUGFIX,
        "breaking": ChangeType.BREAKING,
        "breaking-change": ChangeType.BREAKING,
        "docs": ChangeType.DOCS,
        "documentation": ChangeType.DOCS,
        "security": ChangeType.SECURITY,
        "chore": ChangeType.CHORE,
        "maintenance": ChangeType.CHORE,
    }
    
    EMOJI_MAP = {
        ChangeType.FEATURE: "✨",
        ChangeType.BUGFIX: "🐛",
        ChangeType.BREAKING: "💥",
        ChangeType.DOCS: "📚",
        ChangeType.SECURITY: "🔒",
        ChangeType.CHORE: "🔧",
    }
    
    def __init__(self):
        self.prs: List[PullRequest] = []
        self.categorized: Dict[ChangeType, List[PullRequest]] = {}
    
    def load_prs(self) -> List[PullRequest]:
        """Load merged PRs (simulated)"""
        self.prs = [
            PullRequest(123, "Add user profile page", "dev1", ["feature"], datetime.now(), "Implements user profiles"),
            PullRequest(124, "Fix login timeout bug", "dev2", ["bug"], datetime.now(), "Fixes #100"),
            PullRequest(125, "Update API authentication", "dev3", ["breaking"], datetime.now(), "BREAKING: New auth flow"),
            PullRequest(126, "Add caching layer for search", "dev1", ["feature", "performance"], datetime.now(), "Improves search"),
            PullRequest(127, "Fix null pointer in orders", "dev2", ["bug"], datetime.now(), "Handles edge case"),
            PullRequest(128, "Security patch for CVE-2024-001", "security-team", ["security"], datetime.now(), "Patches vulnerability"),
            PullRequest(129, "Update README", "dev3", ["docs"], datetime.now(), "Updated docs"),
        ]
        return self.prs
    
    def categorize_prs(self) -> Dict[ChangeType, List[PullRequest]]:
        """Categorize PRs by type"""
        self.categorized = {ct: [] for ct in ChangeType}
        
        for pr in self.prs:
            change_type = ChangeType.CHORE
            for label in pr.labels:
                if label.lower() in self.LABEL_MAPPING:
                    change_type = self.LABEL_MAPPING[label.lower()]
                    break
            self.categorized[change_type].append(pr)
        
        return self.categorized
    
    def generate_release_notes(self, version: str) -> str:
        """Generate markdown release notes"""
        notes = f"# Release {version}\n\n"
        notes += f"_Released: {datetime.now().strftime('%Y-%m-%d')}_\n\n"
        
        order = [ChangeType.BREAKING, ChangeType.SECURITY, ChangeType.FEATURE, 
                 ChangeType.BUGFIX, ChangeType.DOCS, ChangeType.CHORE]
        
        for change_type in order:
            prs = self.categorized.get(change_type, [])
            if prs:
                emoji = self.EMOJI_MAP[change_type]
                notes += f"## {emoji} {change_type.value.title()}\n\n"
                for pr in prs:
                    notes += f"- {pr.title} (#{pr.number}) @{pr.author}\n"
                notes += "\n"
        
        return notes
    
    def get_summary(self) -> Dict:
        """Get summary of changes"""
        return {
            "total_prs": len(self.prs),
            "by_type": {ct.value: len(prs) for ct, prs in self.categorized.items() if prs},
            "breaking_changes": len(self.categorized.get(ChangeType.BREAKING, [])),
        }


def print_report(summarizer: PRSummarizer):
    """Print PR summary report"""
    summary = summarizer.get_summary()
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║           PR SUMMARIZER / RELEASE NOTES                      ║
╠══════════════════════════════════════════════════════════════╣
║  Total PRs: {summary['total_prs']:<47}║
║  Breaking Changes: {summary['breaking_changes']:<40}║
╠══════════════════════════════════════════════════════════════╣
║  BY TYPE:                                                    ║""")
    
    for ct, count in summary['by_type'].items():
        print(f"║    {ct:<20} {count:>3} PRs{' ':<30}║")
    
    print("╚══════════════════════════════════════════════════════════════╝")


def main():
    parser = argparse.ArgumentParser(description="PR Summarizer")
    parser.add_argument("--demo", action="store_true")
    parser.add_argument("--version", default="v1.2.0")
    parser.add_argument("--output", type=str, help="Output release notes file")
    args = parser.parse_args()
    
    print("=" * 60)
    print("   AUTO PR SUMMARIZER / RELEASE NOTES")
    print("=" * 60)
    
    summarizer = PRSummarizer()
    summarizer.load_prs()
    summarizer.categorize_prs()
    
    print_report(summarizer)
    
    notes = summarizer.generate_release_notes(args.version)
    print("\n📝 Generated Release Notes:")
    print("-" * 40)
    print(notes)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(notes)
        print(f"📄 Saved to: {args.output}")
    
    return 0


if __name__ == "__main__":
    exit(main())
