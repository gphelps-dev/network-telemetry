#!/usr/bin/env python3
"""
Test script for TrackMap dashboard functionality
"""

import requests
import json
import os

def test_trackmap_dashboard():
    """Test if the TrackMap dashboard is accessible"""
    print("Testing TrackMap Dashboard...")
    
    # Grafana configuration
    grafana_url = "http://localhost:3000"
    username = "admin"
    password = "admin123!"
    
    try:
        # First, try to login and get session
        session = requests.Session()
        login_data = {
            "user": username,
            "password": password
        }
        
        login_response = session.post(f"{grafana_url}/login", data=login_data)
        
        if login_response.status_code == 200:
            print("  PASS: Successfully logged into Grafana")
            
            # Try to access the dashboard
            dashboard_url = f"{grafana_url}/d/network-path-map/network-path-map-dashboard"
            dashboard_response = session.get(dashboard_url)
            
            if dashboard_response.status_code == 200:
                print("  PASS: TrackMap dashboard is accessible")
                return True
            else:
                print(f"  FAIL: Dashboard returned status {dashboard_response.status_code}")
                return False
        else:
            print(f"  FAIL: Login failed with status {login_response.status_code}")
            return False
            
    except Exception as e:
        print(f"  FAIL: Error testing dashboard: {e}")
        return False

def test_plugin_availability():
    """Test if TrackMap plugin is available"""
    print("Testing TrackMap Plugin Availability...")
    
    try:
        # Check if plugin is installed by looking at Grafana API
        response = requests.get("http://localhost:3000/api/plugins")
        
        if response.status_code == 200:
            plugins = response.json()
            trackmap_plugin = None
            
            for plugin in plugins:
                if "trackmap" in plugin.get("id", "").lower():
                    trackmap_plugin = plugin
                    break
            
            if trackmap_plugin:
                print(f"  PASS: TrackMap plugin found: {trackmap_plugin['id']}")
                return True
            else:
                print("  WARNING: TrackMap plugin not found - may need manual installation")
                print("  INFO: You can install it via Grafana UI: Plugins > Browse > Search 'TrackMap'")
                return False
        else:
            print(f"  FAIL: Could not access plugins API: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  FAIL: Error checking plugin availability: {e}")
        return False

def main():
    """Run TrackMap tests"""
    print("TrackMap Dashboard Testing")
    print("=" * 40)
    
    # Test plugin availability
    plugin_ok = test_plugin_availability()
    
    # Test dashboard accessibility
    dashboard_ok = test_trackmap_dashboard()
    
    print("\n" + "=" * 40)
    print("SUMMARY:")
    
    if plugin_ok and dashboard_ok:
        print("PASS: TrackMap dashboard is ready for testing")
    elif dashboard_ok:
        print("PASS: Dashboard accessible (plugin may need manual installation)")
    else:
        print("FAIL: Dashboard testing failed")
    
    print("\nNext steps:")
    print("1. Login to Grafana at http://localhost:3000")
    print("2. Look for 'Network Path Map Dashboard' in the dashboard list")
    print("3. If TrackMap plugin is missing, install it via Plugins > Browse")
    print("4. The dashboard will show network paths on a map when data is available")

if __name__ == "__main__":
    main() 