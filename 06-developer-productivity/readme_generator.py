#!/usr/bin/env python3
"""
================================================================================
README/SERVICE DOC GENERATOR
================================================================================

RESUME BULLET POINT:
"Built a README/service doc generator that auto-creates documentation stubs 
from code analysis, improving documentation coverage."

Author: DevOps Engineer | Version: 1.0.0
================================================================================
"""

import argparse
import json
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class CodeArtifact:
    """Discovered code artifact"""
    name: str
    artifact_type: str  # function, class, endpoint
    signature: str
    docstring: str = ""


class ReadmeGenerator:
    """Generates README documentation"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.artifacts: List[CodeArtifact] = []
    
    def analyze_code(self) -> List[CodeArtifact]:
        """Analyze code to find documentable artifacts (simulated)"""
        self.artifacts = [
            CodeArtifact("UserService", "class", "class UserService", "Manages user operations"),
            CodeArtifact("get_user", "function", "def get_user(id: int) -> User", "Get user by ID"),
            CodeArtifact("create_user", "function", "def create_user(data: dict) -> User", ""),
            CodeArtifact("GET /api/users", "endpoint", "GET /api/users", "List all users"),
            CodeArtifact("POST /api/users", "endpoint", "POST /api/users", ""),
        ]
        return self.artifacts
    
    def generate_readme(self) -> str:
        """Generate README markdown"""
        undocumented = [a for a in self.artifacts if not a.docstring]
        
        readme = f"""# {self.service_name}

## Overview

[TODO: Add service description]

## Getting Started

### Prerequisites

- Python 3.10+
- Docker

### Installation

```bash
pip install -r requirements.txt
```

### Running

```bash
python main.py
```

## API Reference

"""
        endpoints = [a for a in self.artifacts if a.artifact_type == "endpoint"]
        for ep in endpoints:
            readme += f"### `{ep.signature}`\n\n{ep.docstring or '[TODO: Add description]'}\n\n"
        
        readme += "## Classes\n\n"
        classes = [a for a in self.artifacts if a.artifact_type == "class"]
        for cls in classes:
            readme += f"### `{cls.name}`\n\n{cls.docstring or '[TODO: Add description]'}\n\n"
        
        readme += "## Functions\n\n"
        funcs = [a for a in self.artifacts if a.artifact_type == "function"]
        for func in funcs:
            readme += f"### `{func.signature}`\n\n{func.docstring or '[TODO: Add description]'}\n\n"
        
        return readme
    
    def get_coverage(self) -> Dict:
        """Get documentation coverage"""
        documented = sum(1 for a in self.artifacts if a.docstring)
        return {
            "total": len(self.artifacts),
            "documented": documented,
            "undocumented": len(self.artifacts) - documented,
            "coverage_pct": (documented / len(self.artifacts) * 100) if self.artifacts else 0,
        }


def print_report(generator: ReadmeGenerator):
    """Print generation report"""
    coverage = generator.get_coverage()
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║           README GENERATOR                                   ║
╠══════════════════════════════════════════════════════════════╣
║  Service: {generator.service_name:<49}║
║  Artifacts Found: {coverage['total']:<41}║
║  Documentation Coverage: {coverage['coverage_pct']:.0f}%{' ':<32}║
╠══════════════════════════════════════════════════════════════╣
║  UNDOCUMENTED:                                               ║""")
    
    for a in generator.artifacts:
        if not a.docstring:
            print(f"║    ⚠️ {a.artifact_type}: {a.name:<43}║")
    
    print("╚══════════════════════════════════════════════════════════════╝")


def main():
    parser = argparse.ArgumentParser(description="README Generator")
    parser.add_argument("--demo", action="store_true")
    parser.add_argument("--service", default="my-service")
    parser.add_argument("--output", type=str, help="Output README file")
    args = parser.parse_args()
    
    print("=" * 60)
    print("   README / SERVICE DOC GENERATOR")
    print("=" * 60)
    
    generator = ReadmeGenerator(args.service)
    generator.analyze_code()
    
    print_report(generator)
    
    readme = generator.generate_readme()
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(readme)
        print(f"\n📄 README saved to: {args.output}")
    
    return 0


if __name__ == "__main__":
    exit(main())
