#!/usr/bin/env python3
"""
================================================================================
RUNBOOK BUILDER / PLAYBOOK GENERATOR
================================================================================

RESUME BULLET POINT:
"Built a runbook builder that generates incident response playbooks from 
templates, ensuring consistent and effective incident handling."

Author: DevOps Engineer | Version: 1.0.0
================================================================================
"""

import argparse
import json
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum


class IncidentType(Enum):
    OUTAGE = "outage"
    SECURITY = "security"
    PERFORMANCE = "performance"
    DATA_ISSUE = "data_issue"


@dataclass
class RunbookStep:
    """Single step in a runbook"""
    order: int
    title: str
    command: str = ""
    expected_output: str = ""
    escalation_criteria: str = ""


@dataclass
class Runbook:
    """Complete incident runbook"""
    name: str
    incident_type: IncidentType
    description: str
    steps: List[RunbookStep]


class RunbookBuilder:
    """Builds incident runbooks from templates"""
    
    TEMPLATES = {
        IncidentType.OUTAGE: [
            RunbookStep(1, "Acknowledge Incident", "pagerduty ack", "Incident acknowledged"),
            RunbookStep(2, "Check Service Status", "kubectl get pods -n production", "All pods running"),
            RunbookStep(3, "Check Recent Deployments", "kubectl rollout history deployment/api", "List of deployments"),
            RunbookStep(4, "Check Logs", "kubectl logs -l app=api --tail=100", "Error patterns"),
            RunbookStep(5, "Rollback if Needed", "kubectl rollout undo deployment/api", "Rollback complete", "If recent deploy caused issue"),
            RunbookStep(6, "Verify Recovery", "curl -s https://api/health", "200 OK"),
            RunbookStep(7, "Update Status Page", "statuspage update --status operational", "Status updated"),
        ],
        IncidentType.SECURITY: [
            RunbookStep(1, "Isolate Affected Systems", "kubectl cordon <node>", "Node cordoned"),
            RunbookStep(2, "Rotate Credentials", "vault rotate-secrets", "Secrets rotated"),
            RunbookStep(3, "Analyze Logs", "grep -r 'suspicious_pattern' /var/log/", "Attack patterns"),
            RunbookStep(4, "Document Findings", "", "Incident report created"),
        ],
        IncidentType.PERFORMANCE: [
            RunbookStep(1, "Check Resource Usage", "kubectl top pods", "CPU/Memory metrics"),
            RunbookStep(2, "Scale if Needed", "kubectl scale deployment/api --replicas=5", "Scaled"),
            RunbookStep(3, "Check Database Connections", "pg_stat_activity", "Connection count"),
            RunbookStep(4, "Enable Rate Limiting", "kubectl apply -f rate-limit.yaml", "Rate limiting applied"),
        ],
    }
    
    def __init__(self):
        self.runbooks: List[Runbook] = []
    
    def generate_runbook(self, incident_type: IncidentType, service: str) -> Runbook:
        """Generate a runbook from template"""
        steps = self.TEMPLATES.get(incident_type, [])
        
        runbook = Runbook(
            name=f"{service}-{incident_type.value}-runbook",
            incident_type=incident_type,
            description=f"Incident response runbook for {incident_type.value} in {service}",
            steps=steps,
        )
        
        self.runbooks.append(runbook)
        return runbook
    
    def export_markdown(self, runbook: Runbook) -> str:
        """Export runbook as markdown"""
        md = f"# {runbook.name}\n\n"
        md += f"**Type:** {runbook.incident_type.value}  \n"
        md += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  \n\n"
        md += f"## Description\n\n{runbook.description}\n\n"
        md += "## Steps\n\n"
        
        for step in runbook.steps:
            md += f"### Step {step.order}: {step.title}\n\n"
            if step.command:
                md += f"```bash\n{step.command}\n```\n\n"
            if step.expected_output:
                md += f"**Expected:** {step.expected_output}\n\n"
            if step.escalation_criteria:
                md += f"> ⚠️ Escalate if: {step.escalation_criteria}\n\n"
        
        return md


def print_report(builder: RunbookBuilder, runbook: Runbook):
    """Print runbook summary"""
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║           RUNBOOK BUILDER                                    ║
╠══════════════════════════════════════════════════════════════╣
║  Runbook: {runbook.name:<49}║
║  Type: {runbook.incident_type.value:<52}║
║  Steps: {len(runbook.steps):<51}║
╠══════════════════════════════════════════════════════════════╣
║  STEPS:                                                      ║""")
    
    for step in runbook.steps:
        print(f"║    {step.order}. {step.title:<51}║")
    
    print("╚══════════════════════════════════════════════════════════════╝")


def main():
    parser = argparse.ArgumentParser(description="Runbook Builder")
    parser.add_argument("--demo", action="store_true")
    parser.add_argument("--type", choices=["outage", "security", "performance"], default="outage")
    parser.add_argument("--service", default="api-service")
    parser.add_argument("--output", type=str, help="Output runbook file")
    args = parser.parse_args()
    
    print("=" * 60)
    print("   RUNBOOK BUILDER / PLAYBOOK GENERATOR")
    print("=" * 60)
    
    builder = RunbookBuilder()
    incident_type = IncidentType(args.type)
    
    print(f"\n📋 Generating {args.type} runbook for {args.service}...")
    runbook = builder.generate_runbook(incident_type, args.service)
    
    print_report(builder, runbook)
    
    if args.output:
        md = builder.export_markdown(runbook)
        with open(args.output, 'w') as f:
            f.write(md)
        print(f"\n📄 Runbook saved to: {args.output}")
    
    return 0


if __name__ == "__main__":
    exit(main())
