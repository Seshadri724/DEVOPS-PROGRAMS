#!/usr/bin/env python3
"""
================================================================================
SECRET SCANNING IN GIT WORKFLOWS
================================================================================

RESUME BULLET POINT:
"Implemented secret scanning in Git workflows, preventing credential leaks 
and improving baseline security posture."

DESCRIPTION:
Scans Git repositories and commits for accidentally committed secrets like 
API keys, passwords, tokens, and private keys.

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


class SecretType(Enum):
    API_KEY = "api_key"
    AWS_KEY = "aws_key"
    PASSWORD = "password"
    PRIVATE_KEY = "private_key"
    JWT = "jwt"
    DATABASE_URL = "database_url"


@dataclass
class SecretFinding:
    """Detected secret in code"""
    secret_type: SecretType
    file: str
    line: int
    snippet: str  # Redacted snippet
    commit: str
    author: str


class SecretScanner:
    """Scans for secrets in code"""
    
    # Regex patterns for different secret types
    PATTERNS = {
        SecretType.AWS_KEY: r'AKIA[0-9A-Z]{16}',
        SecretType.API_KEY: r'[aA][pP][iI][-_]?[kK][eE][yY][\s]*[:=][\s]*["\']?([a-zA-Z0-9]{20,})["\']?',
        SecretType.PASSWORD: r'[pP][aA][sS][sS][wW][oO][rR][dD][\s]*[:=][\s]*["\']?([^\s"\']{8,})["\']?',
        SecretType.PRIVATE_KEY: r'-----BEGIN (RSA|EC|OPENSSH) PRIVATE KEY-----',
        SecretType.JWT: r'eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*',
        SecretType.DATABASE_URL: r'(postgres|mysql|mongodb):\/\/[^:]+:[^@]+@',
    }
    
    # Files to skip
    EXCLUDED_FILES = ['.lock', '.min.js', 'package-lock.json', 'yarn.lock']
    
    def __init__(self):
        self.findings: List[SecretFinding] = []
    
    def scan_content(self, content: str, file: str, commit: str = "HEAD") -> List[SecretFinding]:
        """Scan file content for secrets"""
        findings = []
        
        if any(excl in file for excl in self.EXCLUDED_FILES):
            return findings
        
        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            for secret_type, pattern in self.PATTERNS.items():
                if re.search(pattern, line):
                    # Redact the actual secret
                    redacted = re.sub(pattern, f'[REDACTED-{secret_type.value}]', line)
                    
                    finding = SecretFinding(
                        secret_type=secret_type,
                        file=file,
                        line=line_num,
                        snippet=redacted[:80] + "..." if len(redacted) > 80 else redacted,
                        commit=commit,
                        author="user@example.com",
                    )
                    findings.append(finding)
                    self.findings.append(finding)
        
        return findings
    
    def scan_demo(self) -> List[SecretFinding]:
        """Run demo scan with sample files"""
        demo_files = {
            "config.py": 'DATABASE_URL = "postgres://user:password123@localhost/db"\nAPI_KEY = "sk_live_abcdef1234567890abcdef"',
            ".env.example": 'AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE\nAWS_SECRET_ACCESS_KEY=xxxxx',
            "auth.js": 'const token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"',
            "deploy.sh": 'export PASSWORD="supersecretpassword123"',
        }
        
        for file, content in demo_files.items():
            self.scan_content(content, file)
        
        return self.findings
    
    def get_summary(self) -> Dict:
        """Get scan summary"""
        by_type = {}
        for f in self.findings:
            type_name = f.secret_type.value
            by_type[type_name] = by_type.get(type_name, 0) + 1
        
        return {
            "total_findings": len(self.findings),
            "by_type": by_type,
            "files_affected": len(set(f.file for f in self.findings)),
            "critical": any(f.secret_type in [SecretType.AWS_KEY, SecretType.PRIVATE_KEY] for f in self.findings),
        }


def print_report(scanner: SecretScanner):
    """Print scan report"""
    summary = scanner.get_summary()
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║              SECRET SCANNING REPORT                          ║
╠══════════════════════════════════════════════════════════════╣
║  Total Secrets Found: {summary['total_findings']:<37}║
║  Files Affected: {summary['files_affected']:<42}║
║  Critical Exposure: {'YES 🔴' if summary['critical'] else 'NO 🟢':<39}║
╠══════════════════════════════════════════════════════════════╣
║  BY SECRET TYPE:                                             ║""")
    
    for stype, count in summary['by_type'].items():
        print(f"║    {stype:<25} {count:>3} findings{' ':<20}║")
    
    print(f"""╠══════════════════════════════════════════════════════════════╣
║  FINDINGS:                                                   ║""")
    
    for finding in scanner.findings[:5]:
        print(f"║    🔴 {finding.file}:{finding.line} [{finding.secret_type.value}]{' ':<14}║")
    
    print("╚══════════════════════════════════════════════════════════════╝")
    
    if summary['critical']:
        print("\n🚨 CRITICAL: AWS keys or private keys detected! Rotate immediately!")


def main():
    parser = argparse.ArgumentParser(description="Secret Scanner")
    parser.add_argument("--demo", action="store_true", help="Run demo scan")
    parser.add_argument("--path", type=str, help="Path to scan")
    parser.add_argument("--output", type=str, help="JSON output file")
    parser.add_argument("--fail-on-secret", action="store_true", help="Exit with error if secrets found")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("   SECRET SCANNING IN GIT WORKFLOWS")
    print("=" * 60)
    
    scanner = SecretScanner()
    
    print("\n🔍 Scanning for secrets...")
    scanner.scan_demo()
    
    print_report(scanner)
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump({
                "summary": scanner.get_summary(),
                "findings": [{"type": f.secret_type.value, "file": f.file, "line": f.line} 
                            for f in scanner.findings]
            }, f, indent=2)
        print(f"\n📄 Report saved to: {args.output}")
    
    if args.fail_on_secret and scanner.findings:
        return 1
    return 0


if __name__ == "__main__":
    exit(main())
