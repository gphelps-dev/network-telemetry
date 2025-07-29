#!/usr/bin/env python3

import subprocess
import sys
import os

def run_test(test_name, test_file):
    """Run a specific test and return success status"""
    print(f"\n🧪 Running {test_name}...")
    print("=" * 50)
    
    try:
        result = subprocess.run(['python3', test_file], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {test_name} passed")
            return True
        else:
            print(f"❌ {test_name} failed")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {test_name} failed with exception: {e}")
        return False

def main():
    """Run all tests before making changes"""
    print("🔍 Running comprehensive test suite...")
    
    tests = [
        ("Dashboard Validation", "test_dashboard.py"),
        ("Integration Tests", "test_integration.py")
    ]
    
    all_passed = True
    failed_tests = []
    
    for test_name, test_file in tests:
        if os.path.exists(test_file):
            if not run_test(test_name, test_file):
                all_passed = False
                failed_tests.append(test_name)
        else:
            print(f"⚠️  Test file not found: {test_file}")
    
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    if all_passed:
        print("✅ All tests passed! System is healthy.")
        print("\n🚀 Safe to proceed with changes.")
        return 0
    else:
        print("❌ Some tests failed:")
        for test in failed_tests:
            print(f"  • {test}")
        print("\n⚠️  Please fix the issues before making changes.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 