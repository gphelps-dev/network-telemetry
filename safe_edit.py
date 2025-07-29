#!/usr/bin/env python3

import subprocess
import sys
import os
import json
import shutil
from datetime import datetime

def run_tests():
    """Run all tests and return success status"""
    print("🔍 Running pre-change tests...")
    result = subprocess.run(['python3', 'run_tests.py'], capture_output=True, text=True)
    return result.returncode == 0

def backup_dashboard():
    """Create a backup of the dashboard file"""
    dashboard_path = "grafana/dashboards/network-telemetry.json"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"grafana/dashboards/network-telemetry.json.backup_{timestamp}"
    
    if os.path.exists(dashboard_path):
        shutil.copy2(dashboard_path, backup_path)
        print(f"📦 Created backup: {backup_path}")
        return backup_path
    return None

def validate_json(file_path):
    """Validate JSON syntax"""
    try:
        with open(file_path, 'r') as f:
            json.load(f)
        return True
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in {file_path}: {e}")
        return False

def restart_grafana():
    """Restart Grafana to pick up changes"""
    print("🔄 Restarting Grafana...")
    result = subprocess.run(['docker', 'restart', 'grafana'], capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ Grafana restarted successfully")
        return True
    else:
        print(f"❌ Failed to restart Grafana: {result.stderr}")
        return False

def main():
    """Safe edit workflow"""
    print("🛡️  Safe Edit Workflow")
    print("=" * 50)
    
    # Step 1: Run pre-change tests
    if not run_tests():
        print("❌ Pre-change tests failed. Aborting changes.")
        return 1
    
    # Step 2: Create backup
    backup_path = backup_dashboard()
    if not backup_path:
        print("❌ Failed to create backup. Aborting changes.")
        return 1
    
    # Step 3: Validate current JSON
    dashboard_path = "grafana/dashboards/network-telemetry.json"
    if not validate_json(dashboard_path):
        print("❌ Current dashboard JSON is invalid. Aborting changes.")
        return 1
    
    print("\n✅ Pre-change validation passed!")
    print("📝 You can now safely edit the dashboard file.")
    print(f"📦 Backup available at: {backup_path}")
    print("\nAfter making changes:")
    print("1. Run: python3 safe_edit.py --validate")
    print("2. Run: python3 safe_edit.py --restart")
    
    return 0

def validate_changes():
    """Validate changes after editing"""
    print("🔍 Validating changes...")
    
    dashboard_path = "grafana/dashboards/network-telemetry.json"
    
    # Validate JSON syntax
    if not validate_json(dashboard_path):
        return False
    
    # Run tests
    if not run_tests():
        return False
    
    print("✅ Changes are valid!")
    return True

def apply_changes():
    """Apply changes by restarting Grafana"""
    print("🚀 Applying changes...")
    
    # Validate first
    if not validate_changes():
        print("❌ Changes failed validation. Please fix issues.")
        return False
    
    # Restart Grafana
    if not restart_grafana():
        return False
    
    print("✅ Changes applied successfully!")
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--validate":
            sys.exit(0 if validate_changes() else 1)
        elif sys.argv[1] == "--restart":
            sys.exit(0 if apply_changes() else 1)
        else:
            print("Usage: python3 safe_edit.py [--validate|--restart]")
            sys.exit(1)
    else:
        sys.exit(main()) 