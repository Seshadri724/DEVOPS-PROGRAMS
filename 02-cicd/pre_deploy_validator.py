#!/usr/bin/env python3
"""
================================================================================
PRE-DEPLOYMENT VALIDATION GATES
================================================================================

RESUME BULLET POINT:
"Developed pre-deployment validation gates in CI/CD pipelines to catch 
misconfigurations, missing secrets, and schema issues before production releases."

DESCRIPTION:
Runs comprehensive checks before deployment: config validation, secret verification,
schema compatibility, dependency checks, and security scans.

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


class CheckStatus(Enum):
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"


class CheckSeverity(Enum):
    BLOCKER = "blocker"   # Blocks deployment
    CRITICAL = "critical" # Should block, can override
    WARNING = "warning"   # Informational
    INFO = "info"


@dataclass
class ValidationCheck:
    """Result of a validation check"""
    name: str
    category: str
    status: CheckStatus
    severity: CheckSeverity
    message: str
    details: List[str] = None


class PreDeployValidator:
    """Runs all pre-deployment validation checks"""
    
    def __init__(self, environment: str):
        self.environment = environment
        self.checks: List[ValidationCheck] = []
    
    def run_all_checks(self) -> List[ValidationCheck]:
        """Run all validation checks"""
        print(f"\n🔍 Running pre-deployment validation for {self.environment}...")
        
        self.check_config_files()
        self.check_secrets()
        self.check_database_schema()
        self.check_dependencies()
        self.check_security()
        self.check_resource_limits()
        self.check_feature_flags()
        
        return self.checks
    
    def check_config_files(self):
        """Validate configuration files"""
        print("   📋 Checking configurations...")
        
        # Simulated config checks
        configs = [
            ("app.config.json", True, []),
            ("database.yml", True, []),
            ("secrets.encrypted", False, ["Missing encryption key reference"]),
        ]
        
        for config, valid, issues in configs:
            self.checks.append(ValidationCheck(
                name=f"Config: {config}",
                category="configuration",
                status=CheckStatus.PASSED if valid else CheckStatus.FAILED,
                severity=CheckSeverity.BLOCKER if not valid else CheckSeverity.INFO,
                message=f"{'Valid' if valid else 'Invalid'} configuration",
                details=issues,
            ))
    
    def check_secrets(self):
        """Verify all required secrets are present"""
        print("   🔐 Checking secrets...")
        
        required_secrets = ["DATABASE_URL", "API_KEY", "JWT_SECRET", "AWS_ACCESS_KEY"]
        present_secrets = ["DATABASE_URL", "API_KEY", "JWT_SECRET"]  # Simulated
        
        missing = [s for s in required_secrets if s not in present_secrets]
        
        self.checks.append(ValidationCheck(
            name="Required Secrets",
            category="secrets",
            status=CheckStatus.FAILED if missing else CheckStatus.PASSED,
            severity=CheckSeverity.BLOCKER,
            message=f"Missing secrets: {', '.join(missing)}" if missing else "All secrets present",
            details=missing,
        ))
    
    def check_database_schema(self):
        """Check for pending database migrations"""
        print("   🗄️  Checking database schema...")
        
        # Simulated: Check for pending migrations
        pending_migrations = ["20231215_add_user_preferences"]  # Simulated
        
        self.checks.append(ValidationCheck(
            name="Database Migrations",
            category="database",
            status=CheckStatus.WARNING if pending_migrations else CheckStatus.PASSED,
            severity=CheckSeverity.CRITICAL,
            message=f"{len(pending_migrations)} pending migrations" if pending_migrations else "Schema up to date",
            details=pending_migrations,
        ))
    
    def check_dependencies(self):
        """Check for vulnerable or outdated dependencies"""
        print("   📦 Checking dependencies...")
        
        vulnerabilities = [
            {"package": "lodash", "severity": "high", "version": "4.17.19"},
        ]
        
        self.checks.append(ValidationCheck(
            name="Dependency Vulnerabilities",
            category="security",
            status=CheckStatus.WARNING if vulnerabilities else CheckStatus.PASSED,
            severity=CheckSeverity.CRITICAL,
            message=f"{len(vulnerabilities)} vulnerable packages" if vulnerabilities else "No vulnerabilities",
            details=[f"{v['package']}@{v['version']} ({v['severity']})" for v in vulnerabilities],
        ))
    
    def check_security(self):
        """Run security scans"""
        print("   🛡️  Running security checks...")
        
        # Simulated security findings
        findings = []
        
        self.checks.append(ValidationCheck(
            name="Security Scan",
            category="security",
            status=CheckStatus.PASSED if not findings else CheckStatus.FAILED,
            severity=CheckSeverity.BLOCKER,
            message="No security issues" if not findings else f"{len(findings)} issues found",
            details=findings,
        ))
    
    def check_resource_limits(self):
        """Verify resource limits are set"""
        print("   📊 Checking resource limits...")
        
        # Check Kubernetes resource limits
        missing_limits = []  # Simulated: all limits set
        
        self.checks.append(ValidationCheck(
            name="Resource Limits",
            category="resources",
            status=CheckStatus.PASSED if not missing_limits else CheckStatus.WARNING,
            severity=CheckSeverity.WARNING,
            message="All resource limits configured" if not missing_limits else "Missing limits",
            details=missing_limits,
        ))
    
    def check_feature_flags(self):
        """Verify feature flag configuration"""
        print("   🚩 Checking feature flags...")
        
        self.checks.append(ValidationCheck(
            name="Feature Flags",
            category="configuration",
            status=CheckStatus.PASSED,
            severity=CheckSeverity.INFO,
            message="Feature flags configured correctly",
        ))
    
    def get_summary(self) -> Dict:
        """Get validation summary"""
        passed = sum(1 for c in self.checks if c.status == CheckStatus.PASSED)
        failed = sum(1 for c in self.checks if c.status == CheckStatus.FAILED)
        warnings = sum(1 for c in self.checks if c.status == CheckStatus.WARNING)
        blockers = sum(1 for c in self.checks if c.status == CheckStatus.FAILED 
                      and c.severity == CheckSeverity.BLOCKER)
        
        return {
            "total_checks": len(self.checks),
            "passed": passed,
            "failed": failed,
            "warnings": warnings,
            "blockers": blockers,
            "can_deploy": blockers == 0,
        }


def print_report(validator: PreDeployValidator):
    """Print validation report"""
    summary = validator.get_summary()
    
    status_icon = "✅" if summary["can_deploy"] else "❌"
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║           PRE-DEPLOYMENT VALIDATION REPORT                   ║
╠══════════════════════════════════════════════════════════════╣
║  Environment: {validator.environment:<45}║
║  Deployment Status: {status_icon} {'ALLOWED' if summary['can_deploy'] else 'BLOCKED':<40}║
╠══════════════════════════════════════════════════════════════╣
║  SUMMARY:                                                    ║
║    ✅ Passed:   {summary['passed']:<44}║
║    ❌ Failed:   {summary['failed']:<44}║
║    ⚠️  Warnings: {summary['warnings']:<44}║
║    🚫 Blockers: {summary['blockers']:<44}║
╠══════════════════════════════════════════════════════════════╣
║  CHECK DETAILS:                                              ║""")
    
    for check in validator.checks:
        icon = {"passed": "✅", "failed": "❌", "warning": "⚠️", "skipped": "⏭️"}[check.status.value]
        print(f"║    {icon} {check.name:<50}    ║")
        if check.details and check.status != CheckStatus.PASSED:
            for detail in check.details[:2]:
                print(f"║       └─ {detail:<48}║")
    
    print("╚══════════════════════════════════════════════════════════════╝")
    
    if not summary["can_deploy"]:
        print("\n🚨 DEPLOYMENT BLOCKED: Fix blocker issues before deploying!")


def main():
    parser = argparse.ArgumentParser(description="Pre-Deployment Validation Gates")
    parser.add_argument("--env", choices=["dev", "staging", "prod"], default="staging")
    parser.add_argument("--demo", action="store_true", help="Run with simulated data")
    parser.add_argument("--output", type=str, help="JSON output file")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("   PRE-DEPLOYMENT VALIDATION GATES")
    print("=" * 60)
    
    validator = PreDeployValidator(args.env)
    validator.run_all_checks()
    
    print_report(validator)
    
    if args.output:
        summary = validator.get_summary()
        with open(args.output, 'w') as f:
            json.dump({
                "summary": summary,
                "checks": [{"name": c.name, "status": c.status.value, "message": c.message} 
                          for c in validator.checks]
            }, f, indent=2)
        print(f"\n📄 Report saved to: {args.output}")
    
    summary = validator.get_summary()
    return 0 if summary["can_deploy"] else 1


if __name__ == "__main__":
    exit(main())
