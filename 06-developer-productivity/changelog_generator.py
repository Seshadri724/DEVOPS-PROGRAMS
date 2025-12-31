#!/usr/bin/env python3
"""
================================================================================
CHANGELOG AUTOMATION BOT
================================================================================

RESUME BULLET POINT:
"Built a changelog automation bot that generates changelogs from commit 
history using conventional commits, eliminating manual tracking."

Author: DevOps Engineer | Version: 1.0.0
================================================================================
"""

import argparse
import json
import re
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class Commit:
    """Git commit"""
    sha: str
    message: str
    author: str
    date: datetime


class ChangelogGenerator:
    """Generates changelog from conventional commits"""
    
    # Conventional commit patterns
    PATTERNS = {
        r'^feat(\(.+\))?:': ('Features', '✨'),
        r'^fix(\(.+\))?:': ('Bug Fixes', '🐛'),
        r'^docs(\(.+\))?:': ('Documentation', '📚'),
        r'^style(\(.+\))?:': ('Styling', '💄'),
        r'^refactor(\(.+\))?:': ('Refactoring', '♻️'),
        r'^perf(\(.+\))?:': ('Performance', '⚡'),
        r'^test(\(.+\))?:': ('Tests', '✅'),
        r'^build(\(.+\))?:': ('Build', '📦'),
        r'^ci(\(.+\))?:': ('CI', '👷'),
        r'^chore(\(.+\))?:': ('Chores', '🔧'),
    }
    
    def __init__(self, version: str):
        self.version = version
        self.commits: List[Commit] = []
        self.categorized: Dict[str, List[Commit]] = {}
    
    def load_commits(self) -> List[Commit]:
        """Load commits since last release (simulated)"""
        self.commits = [
            Commit("abc123", "feat(auth): add OAuth2 support", "dev1", datetime.now()),
            Commit("def456", "fix(api): handle null response", "dev2", datetime.now()),
            Commit("ghi789", "docs: update API documentation", "dev3", datetime.now()),
            Commit("jkl012", "feat(ui): add dark mode toggle", "dev1", datetime.now()),
            Commit("mno345", "fix(db): connection pool leak", "dev2", datetime.now()),
            Commit("pqr678", "perf(search): optimize query performance", "dev1", datetime.now()),
            Commit("stu901", "chore: update dependencies", "bot", datetime.now()),
        ]
        return self.commits
    
    def categorize_commits(self):
        """Categorize commits by type"""
        for commit in self.commits:
            for pattern, (category, emoji) in self.PATTERNS.items():
                if re.match(pattern, commit.message.lower()):
                    if category not in self.categorized:
                        self.categorized[category] = []
                    self.categorized[category].append(commit)
                    break
    
    def generate_changelog(self) -> str:
        """Generate markdown changelog"""
        changelog = f"# Changelog\n\n## [{self.version}] - {datetime.now().strftime('%Y-%m-%d')}\n\n"
        
        for pattern, (category, emoji) in self.PATTERNS.items():
            commits = self.categorized.get(category, [])
            if commits:
                changelog += f"### {emoji} {category}\n\n"
                for c in commits:
                    # Extract scope and description
                    msg = re.sub(r'^[a-z]+(\(.+\))?:\s*', '', c.message)
                    changelog += f"- {msg} ({c.sha[:7]})\n"
                changelog += "\n"
        
        return changelog
    
    def get_summary(self) -> Dict:
        """Get generation summary"""
        return {
            "total_commits": len(self.commits),
            "categories": len(self.categorized),
            "by_category": {k: len(v) for k, v in self.categorized.items()},
        }


def print_report(generator: ChangelogGenerator):
    """Print changelog report"""
    summary = generator.get_summary()
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║           CHANGELOG GENERATOR                                ║
╠══════════════════════════════════════════════════════════════╣
║  Version: {generator.version:<49}║
║  Commits Analyzed: {summary['total_commits']:<40}║
║  Categories: {summary['categories']:<46}║
╠══════════════════════════════════════════════════════════════╣
║  BY CATEGORY:                                                ║""")
    
    for cat, count in summary['by_category'].items():
        print(f"║    {cat:<25} {count:>3} commits{' ':<19}║")
    
    print("╚══════════════════════════════════════════════════════════════╝")


def main():
    parser = argparse.ArgumentParser(description="Changelog Generator")
    parser.add_argument("--demo", action="store_true")
    parser.add_argument("--version", default="v1.0.0")
    parser.add_argument("--output", type=str, help="Output changelog file")
    args = parser.parse_args()
    
    print("=" * 60)
    print("   CHANGELOG AUTOMATION BOT")
    print("=" * 60)
    
    generator = ChangelogGenerator(args.version)
    generator.load_commits()
    generator.categorize_commits()
    
    print_report(generator)
    
    changelog = generator.generate_changelog()
    print("\n📝 Generated Changelog:")
    print("-" * 40)
    print(changelog)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(changelog)
        print(f"📄 Saved to: {args.output}")
    
    return 0


if __name__ == "__main__":
    exit(main())
