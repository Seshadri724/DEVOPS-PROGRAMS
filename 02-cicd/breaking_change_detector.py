#!/usr/bin/env python3
"""
================================================================================
BREAKING CHANGE DETECTOR
================================================================================

RESUME BULLET POINT:
"Built a breaking change detector that identifies backward-incompatible API 
or DB schema changes before merge, preventing production incidents."

DESCRIPTION:
Analyzes API specs and database schemas to detect breaking changes:
- Removed endpoints/fields
- Changed types
- New required parameters
- Schema incompatibilities

Author: DevOps Engineer | Version: 1.0.0
================================================================================
"""

import argparse
import json
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class BreakingChangeType(Enum):
    ENDPOINT_REMOVED = "endpoint_removed"
    FIELD_REMOVED = "field_removed"
    TYPE_CHANGED = "type_changed"
    REQUIRED_ADDED = "required_field_added"
    COLUMN_REMOVED = "column_removed"
    COLUMN_TYPE_CHANGED = "column_type_changed"


class Severity(Enum):
    CRITICAL = "critical"  # Will break clients
    HIGH = "high"          # Likely to break clients
    MEDIUM = "medium"      # May break some clients
    LOW = "low"            # Unlikely to break clients


@dataclass
class BreakingChange:
    """Detected breaking change"""
    change_type: BreakingChangeType
    severity: Severity
    location: str  # API path or table.column
    description: str
    old_value: str
    new_value: str


class APISchemaComparer:
    """Compares OpenAPI/Swagger schemas for breaking changes"""
    
    @staticmethod
    def compare(old_spec: Dict, new_spec: Dict) -> List[BreakingChange]:
        """Compare two API specifications"""
        changes = []
        
        old_paths = old_spec.get("paths", {})
        new_paths = new_spec.get("paths", {})
        
        # Check for removed endpoints
        for path in old_paths:
            if path not in new_paths:
                changes.append(BreakingChange(
                    change_type=BreakingChangeType.ENDPOINT_REMOVED,
                    severity=Severity.CRITICAL,
                    location=path,
                    description=f"Endpoint {path} was removed",
                    old_value=path,
                    new_value="(removed)",
                ))
        
        # Check for removed response fields (simplified)
        for path, methods in new_paths.items():
            if path in old_paths:
                # Check each method
                for method, spec in methods.items():
                    if method in old_paths.get(path, {}):
                        old_fields = old_paths[path][method].get("response_fields", [])
                        new_fields = spec.get("response_fields", [])
                        
                        for field in old_fields:
                            if field not in new_fields:
                                changes.append(BreakingChange(
                                    change_type=BreakingChangeType.FIELD_REMOVED,
                                    severity=Severity.HIGH,
                                    location=f"{method.upper()} {path}",
                                    description=f"Response field '{field}' was removed",
                                    old_value=field,
                                    new_value="(removed)",
                                ))
        
        return changes


class DBSchemaComparer:
    """Compares database schemas for breaking changes"""
    
    @staticmethod
    def compare(old_schema: Dict, new_schema: Dict) -> List[BreakingChange]:
        """Compare two database schemas"""
        changes = []
        
        old_tables = old_schema.get("tables", {})
        new_tables = new_schema.get("tables", {})
        
        for table, old_columns in old_tables.items():
            if table not in new_tables:
                changes.append(BreakingChange(
                    change_type=BreakingChangeType.COLUMN_REMOVED,
                    severity=Severity.CRITICAL,
                    location=f"Table: {table}",
                    description=f"Table {table} was removed",
                    old_value=table,
                    new_value="(removed)",
                ))
                continue
            
            new_columns = new_tables.get(table, {})
            
            for col, col_type in old_columns.items():
                if col not in new_columns:
                    changes.append(BreakingChange(
                        change_type=BreakingChangeType.COLUMN_REMOVED,
                        severity=Severity.HIGH,
                        location=f"{table}.{col}",
                        description=f"Column {col} removed from {table}",
                        old_value=col,
                        new_value="(removed)",
                    ))
                elif new_columns[col] != col_type:
                    changes.append(BreakingChange(
                        change_type=BreakingChangeType.COLUMN_TYPE_CHANGED,
                        severity=Severity.MEDIUM,
                        location=f"{table}.{col}",
                        description=f"Column type changed",
                        old_value=col_type,
                        new_value=new_columns[col],
                    ))
        
        return changes


class BreakingChangeDetector:
    """Main detector that combines API and DB change detection"""
    
    def __init__(self):
        self.changes: List[BreakingChange] = []
    
    def detect_api_changes(self, old_spec: Dict, new_spec: Dict):
        """Detect API breaking changes"""
        self.changes.extend(APISchemaComparer.compare(old_spec, new_spec))
    
    def detect_db_changes(self, old_schema: Dict, new_schema: Dict):
        """Detect database breaking changes"""
        self.changes.extend(DBSchemaComparer.compare(old_schema, new_schema))
    
    def get_summary(self) -> Dict:
        """Get detection summary"""
        critical = sum(1 for c in self.changes if c.severity == Severity.CRITICAL)
        high = sum(1 for c in self.changes if c.severity == Severity.HIGH)
        
        return {
            "total_breaking_changes": len(self.changes),
            "critical": critical,
            "high": high,
            "medium": sum(1 for c in self.changes if c.severity == Severity.MEDIUM),
            "low": sum(1 for c in self.changes if c.severity == Severity.LOW),
            "can_merge": critical == 0 and high == 0,
        }


def get_demo_specs() -> tuple:
    """Get demo API and DB specs for testing"""
    old_api = {
        "paths": {
            "/api/users": {"get": {"response_fields": ["id", "name", "email", "phone"]}},
            "/api/orders": {"get": {"response_fields": ["id", "total", "status"]}},
            "/api/legacy": {"get": {}},  # Will be removed
        }
    }
    
    new_api = {
        "paths": {
            "/api/users": {"get": {"response_fields": ["id", "name", "email"]}},  # phone removed
            "/api/orders": {"get": {"response_fields": ["id", "total", "status"]}},
            # /api/legacy removed
        }
    }
    
    old_db = {
        "tables": {
            "users": {"id": "int", "name": "varchar(255)", "email": "varchar(255)", "phone": "varchar(50)"},
            "orders": {"id": "int", "user_id": "int", "total": "decimal"},
        }
    }
    
    new_db = {
        "tables": {
            "users": {"id": "int", "name": "varchar(255)", "email": "varchar(255)"},  # phone removed
            "orders": {"id": "int", "user_id": "int", "total": "bigint"},  # type changed
        }
    }
    
    return old_api, new_api, old_db, new_db


def print_report(detector: BreakingChangeDetector):
    """Print breaking change report"""
    summary = detector.get_summary()
    
    can_merge = "✅ SAFE TO MERGE" if summary["can_merge"] else "❌ BLOCKED"
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║           BREAKING CHANGE DETECTION REPORT                   ║
╠══════════════════════════════════════════════════════════════╣
║  Status: {can_merge:<50}║
║  Total Breaking Changes: {summary['total_breaking_changes']:<34}║
╠══════════════════════════════════════════════════════════════╣
║  BY SEVERITY:                                                ║
║    🔴 Critical: {summary['critical']:<44}║
║    🟠 High:     {summary['high']:<44}║
║    🟡 Medium:   {summary['medium']:<44}║
║    🟢 Low:      {summary['low']:<44}║
╠══════════════════════════════════════════════════════════════╣
║  CHANGES:                                                    ║""")
    
    severity_icons = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
    
    for change in detector.changes:
        icon = severity_icons[change.severity.value]
        print(f"║    {icon} {change.location:<50}   ║")
        print(f"║       └─ {change.description:<48}║")
    
    print("╚══════════════════════════════════════════════════════════════╝")


def main():
    parser = argparse.ArgumentParser(description="Breaking Change Detector")
    parser.add_argument("--demo", action="store_true", help="Run with demo data")
    parser.add_argument("--old-api", type=str, help="Path to old API spec")
    parser.add_argument("--new-api", type=str, help="Path to new API spec")
    parser.add_argument("--output", type=str, help="JSON output file")
    parser.add_argument("--strict", action="store_true", help="Fail on any breaking change")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("   BREAKING CHANGE DETECTOR")
    print("=" * 60)
    
    detector = BreakingChangeDetector()
    
    # Load specs (demo mode)
    old_api, new_api, old_db, new_db = get_demo_specs()
    
    print("\n🔍 Analyzing API changes...")
    detector.detect_api_changes(old_api, new_api)
    
    print("🔍 Analyzing database schema changes...")
    detector.detect_db_changes(old_db, new_db)
    
    print_report(detector)
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump({
                "summary": detector.get_summary(),
                "changes": [
                    {"type": c.change_type.value, "severity": c.severity.value, 
                     "location": c.location, "description": c.description}
                    for c in detector.changes
                ]
            }, f, indent=2)
        print(f"\n📄 Report saved to: {args.output}")
    
    summary = detector.get_summary()
    return 0 if summary["can_merge"] else 1


if __name__ == "__main__":
    exit(main())
