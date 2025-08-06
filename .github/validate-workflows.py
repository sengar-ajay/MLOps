#!/usr/bin/env python3
"""
GitHub Actions Workflow Validator
Validates YAML syntax and basic structure of workflow files
"""

import os
import sys
import yaml
from pathlib import Path

def validate_workflow_file(filepath):
    """Validate a single workflow file"""
    print(f"INFO: Validating {filepath}...")
    
    try:
        with open(filepath, 'r') as f:
            workflow = yaml.safe_load(f)
        
        # Basic structure validation
        required_keys = ['name', 'jobs']
        for key in required_keys:
            if key not in workflow:
                print(f"  ERROR: Missing required key: {key}")
                return False
        
        # Check for 'on' key (which might be parsed as True due to YAML boolean interpretation)
        has_trigger = 'on' in workflow or True in workflow
        if not has_trigger:
            print(f"  ERROR: Missing workflow trigger ('on' key)")
            return False
        
        # Validate jobs structure
        jobs = workflow.get('jobs', {})
        if not isinstance(jobs, dict) or not jobs:
            print(f"  ERROR: No jobs defined")
            return False
        
        # Validate each job
        for job_name, job_config in jobs.items():
            if not isinstance(job_config, dict):
                print(f"  ERROR: Job '{job_name}' is not a dictionary")
                return False
            
            if 'runs-on' not in job_config:
                print(f"  ERROR: Job '{job_name}' missing 'runs-on'")
                return False
            
            if 'steps' not in job_config:
                print(f"  ERROR: Job '{job_name}' missing 'steps'")
                return False
        
        print(f"  SUCCESS: Valid workflow with {len(jobs)} jobs")
        return True
        
    except yaml.YAMLError as e:
        print(f"  ERROR: YAML syntax error: {e}")
        return False
    except Exception as e:
        print(f"  ERROR: Validation error: {e}")
        return False

def main():
    """Main validation function"""
    print("DEPLOY: GitHub Actions Workflow Validator")
    print("=" * 50)
    
    workflows_dir = Path(".github/workflows")
    
    if not workflows_dir.exists():
        print("ERROR: .github/workflows directory not found")
        sys.exit(1)
    
    workflow_files = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
    
    if not workflow_files:
        print("ERROR: No workflow files found")
        sys.exit(1)
    
    valid_count = 0
    total_count = len(workflow_files)
    
    for workflow_file in sorted(workflow_files):
        if validate_workflow_file(workflow_file):
            valid_count += 1
        print()
    
    print("STATS: Validation Summary")
    print("-" * 20)
    print(f"Total workflows: {total_count}")
    print(f"Valid workflows: {valid_count}")
    print(f"Invalid workflows: {total_count - valid_count}")
    
    if valid_count == total_count:
        print("\nSUCCESS: All workflows are valid!")
        sys.exit(0)
    else:
        print(f"\nERROR: {total_count - valid_count} workflow(s) have issues")
        sys.exit(1)

if __name__ == "__main__":
    main()