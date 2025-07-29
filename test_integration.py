#!/usr/bin/env python3

import json
import os
import sys
import subprocess
import time

class IntegrationTester:
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def test_docker_services(self):
        """Test that all Docker services are running"""
        print("🐳 Testing Docker services...")
        
        try:
            result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
            if result.returncode == 0:
                services = ['grafana', 'influxdb2', 'telemetry']
                running_services = []
                
                for line in result.stdout.split('\n'):
                    for service in services:
                        if service in line:
                            running_services.append(service)
                
                if len(running_services) == len(services):
                    print("  ✅ All services are running")
                    return True
                else:
                    missing = [s for s in services if s not in running_services]
                    self.errors.append(f"Missing services: {missing}")
                    return False
            else:
                self.errors.append("Docker command failed")
                return False
        except Exception as e:
            self.errors.append(f"Docker test failed: {e}")
            return False
    
    def test_dashboard_file(self):
        """Test that dashboard file exists and is valid JSON"""
        print("📊 Testing dashboard file...")
        
        dashboard_path = "grafana/dashboards/network-telemetry.json"
        
        if not os.path.exists(dashboard_path):
            self.errors.append(f"Dashboard file not found: {dashboard_path}")
            return False
        
        try:
            with open(dashboard_path, 'r') as f:
                dashboard = json.load(f)
            
            # Check required fields
            required_fields = ['title', 'panels', 'schemaVersion']
            for field in required_fields:
                if field not in dashboard:
                    self.errors.append(f"Dashboard missing required field: {field}")
                    return False
            
            print("  ✅ Dashboard file is valid")
            return True
        except json.JSONDecodeError as e:
            self.errors.append(f"Dashboard JSON is invalid: {e}")
            return False
        except Exception as e:
            self.errors.append(f"Dashboard test failed: {e}")
            return False
    
    def test_telemetry_file(self):
        """Test that telemetry main file exists and has required functions"""
        print("📡 Testing telemetry file...")
        
        telemetry_path = "telemetry/main.py"
        
        if not os.path.exists(telemetry_path):
            self.errors.append(f"Telemetry file not found: {telemetry_path}")
            return False
        
        try:
            with open(telemetry_path, 'r') as f:
                content = f.read()
            
            # Check for required functions
            required_functions = ['write_to_influx', 'get_geolocation']
            for func in required_functions:
                if func not in content:
                    self.errors.append(f"Telemetry missing function: {func}")
                    return False
            
            # Check for network_flow generation
            if 'network_flow' not in content:
                self.warnings.append("Network flow generation may not be implemented")
            
            print("  ✅ Telemetry file has required functions")
            return True
        except Exception as e:
            self.errors.append(f"Telemetry test failed: {e}")
            return False
    
    def test_influxdb_connection(self):
        """Test InfluxDB connection and basic queries"""
        print("💾 Testing InfluxDB connection...")
        
        try:
            # Test basic query
            cmd = [
                'docker', 'exec', 'influxdb2', 'influx', 'query',
                '--org', 'nflx',
                '--token', 'SlhPxmQPGdRbxnVO5onZOJwqiuf8_9pqdIJPuNpUFKRiPBRlDHyOdMqJEaKNuK1CEFSWH9It0FtYM619I8pIlA==',
                'from(bucket: "default") |> range(start: -1h) |> count()'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print("  ✅ InfluxDB is accessible")
                return True
            else:
                self.errors.append(f"InfluxDB query failed: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            self.errors.append("InfluxDB query timed out")
            return False
        except Exception as e:
            self.errors.append(f"InfluxDB test failed: {e}")
            return False
    
    def test_grafana_connection(self):
        """Test Grafana connection"""
        print("📈 Testing Grafana connection...")
        
        try:
            import urllib.request
            import urllib.error
            
            # Test Grafana health endpoint
            url = "http://localhost:3000/api/health"
            req = urllib.request.Request(url)
            
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    print("  ✅ Grafana is accessible")
                    return True
                else:
                    self.errors.append(f"Grafana returned status: {response.status}")
                    return False
        except urllib.error.URLError as e:
            self.errors.append(f"Grafana connection failed: {e}")
            return False
        except Exception as e:
            self.errors.append(f"Grafana test failed: {e}")
            return False
    
    def test_data_availability(self):
        """Test that we have some data in InfluxDB"""
        print("📊 Testing data availability...")
        
        try:
            # Check for network_telemetry data
            cmd = [
                'docker', 'exec', 'influxdb2', 'influx', 'query',
                '--org', 'nflx',
                '--token', 'SlhPxmQPGdRbxnVO5onZOJwqiuf8_9pqdIJPuNpUFKRiPBRlDHyOdMqJEaKNuK1CEFSWH9It0FtYM619I8pIlA==',
                'from(bucket: "default") |> range(start: -1h) |> filter(fn: (r) => r._measurement == "network_telemetry") |> count()'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and 'network_telemetry' in result.stdout:
                print("  ✅ Network telemetry data is available")
                return True
            else:
                self.warnings.append("No network telemetry data found")
                return True  # Not a critical error
        except Exception as e:
            self.warnings.append(f"Data availability test failed: {e}")
            return True  # Not a critical error
    
    def run_all_tests(self) -> bool:
        """Run all integration tests"""
        print("🔍 Running integration tests...")
        
        tests = [
            self.test_docker_services,
            self.test_dashboard_file,
            self.test_telemetry_file,
            self.test_influxdb_connection,
            self.test_grafana_connection,
            self.test_data_availability
        ]
        
        all_passed = True
        for test in tests:
            try:
                if not test():
                    all_passed = False
            except Exception as e:
                self.errors.append(f"Test {test.__name__} failed with exception: {e}")
                all_passed = False
        
        return all_passed
    
    def print_results(self):
        """Print test results"""
        if self.errors:
            print("\n❌ ERRORS:")
            for error in self.errors:
                print(f"  • {error}")
        
        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"  • {warning}")
        
        if not self.errors and not self.warnings:
            print("\n✅ All integration tests passed!")
        elif not self.errors:
            print("\n✅ System is healthy (with warnings).")
        else:
            print("\n❌ System has issues that need to be fixed.")

def main():
    tester = IntegrationTester()
    success = tester.run_all_tests()
    tester.print_results()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main() 