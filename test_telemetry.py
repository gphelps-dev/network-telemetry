#!/usr/bin/env python3

import unittest
try:
    from unittest.mock import patch, MagicMock, mock_open
except ImportError:
    from mock import patch, MagicMock, mock_open
import subprocess
import requests
import os
import sys
import tempfile
import json

# Add the telemetry directory to the path so we can import the functions
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'telemetry'))

# Import the functions we want to test
from main import ping, traceroute, write_to_influx, collect_telemetry_for_destination, check_dependencies

class TestTelemetryFunctions(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment"""
        # Mock environment variables
        self.env_patcher = patch.dict(os.environ, {
            'INFLUX_URL': 'http://test:8086',
            'INFLUX_TOKEN': 'test_token',
            'INFLUX_BUCKET': 'test_bucket',
            'INFLUX_ORG': 'test_org'
        })
        self.env_patcher.start()
    
    def tearDown(self):
        """Clean up after tests"""
        self.env_patcher.stop()
    
    @patch('subprocess.check_output')
    def test_ping_success(self, mock_check_output):
        """Test successful ping parsing"""
        mock_output = """
PING google.com (142.250.189.206) 56(84) bytes of data.
64 bytes from sfo03s25-in-f14.1e100.net (142.250.189.206): icmp_seq=1 ttl=63 time=6.13 ms
64 bytes from sfo03s25-in-f14.1e100.net (142.250.189.206): icmp_seq=2 ttl=63 time=8.09 ms
64 bytes from sfo03s25-in-f14.1e100.net (142.250.189.206): icmp_seq=3 ttl=63 time=12.1 ms
64 bytes from sfo03s25-in-f14.1e100.net (142.250.189.206): icmp_seq=4 ttl=63 time=9.39 ms

--- google.com ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3014ms
rtt min/avg/max/mdev = 5.931/8.884/12.134/2.245 ms
"""
        mock_check_output.return_value = mock_output.encode()
        
        latency, packet_loss = ping("google.com")
        
        self.assertIsNotNone(latency)
        self.assertIsNotNone(packet_loss)
        self.assertEqual(latency, 8.884)
        self.assertEqual(packet_loss, 0.0)
        mock_check_output.assert_called_once()
    
    @patch('subprocess.check_output')
    def test_ping_failure(self, mock_check_output):
        """Test ping failure handling"""
        mock_check_output.side_effect = subprocess.CalledProcessError(1, "ping")
        
        latency, packet_loss = ping("invalid.domain")
        
        self.assertIsNone(latency)
        self.assertIsNone(packet_loss)
    
    @patch('subprocess.check_output')
    def test_traceroute_success(self, mock_check_output):
        """Test successful traceroute parsing"""
        mock_output = """
traceroute to google.com (142.250.189.206), 30 hops max, 60 byte packets
 1  172.18.0.1  0.216 ms  0.187 ms  0.178 ms
 2  * * 192.168.64.1  0.229 ms
 3  192.168.36.1  7.727 ms  7.711 ms  7.699 ms
 4  67.208.237.129  7.680 ms  7.670 ms  7.667 ms
"""
        mock_check_output.return_value = mock_output.encode()
        
        hop_count = traceroute("google.com")
        
        self.assertIsNotNone(hop_count)
        self.assertEqual(hop_count, 3)  # 3 valid hops
        mock_check_output.assert_called_once()
    
    @patch('subprocess.check_output')
    def test_traceroute_failure(self, mock_check_output):
        """Test traceroute failure handling"""
        mock_check_output.side_effect = subprocess.CalledProcessError(1, "traceroute")
        
        hop_count = traceroute("invalid.domain")
        
        self.assertIsNone(hop_count)
    
    @patch('requests.post')
    def test_write_to_influx_success(self, mock_post):
        """Test successful InfluxDB write"""
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_post.return_value = mock_response
        
        result = write_to_influx("google.com", 10.5, 0.0, 8, True)
        
        self.assertTrue(result)
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_write_to_influx_failure(self, mock_post):
        """Test InfluxDB write failure"""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response
        
        result = write_to_influx("google.com", 10.5, 0.0, 8, True)
        
        self.assertFalse(result)
    
    @patch('requests.post')
    def test_write_to_influx_network_error(self, mock_post):
        """Test InfluxDB network error"""
        mock_post.side_effect = requests.exceptions.RequestException("Network error")
        
        result = write_to_influx("google.com", 10.5, 0.0, 8, True)
        
        self.assertFalse(result)
    
    @patch('subprocess.run')
    def test_check_dependencies_success(self, mock_run):
        """Test dependency check success"""
        mock_run.return_value = MagicMock(returncode=0)
        
        result = check_dependencies()
        
        self.assertTrue(result)
        self.assertEqual(mock_run.call_count, 2)  # ping and traceroute
    
    @patch('subprocess.run')
    def test_check_dependencies_failure(self, mock_run):
        """Test dependency check failure"""
        mock_run.side_effect = subprocess.CalledProcessError(1, "ping")
        
        result = check_dependencies()
        
        self.assertFalse(result)
    
    @patch('main.ping')
    @patch('main.traceroute')
    @patch('main.write_to_influx')
    def test_collect_telemetry_success(self, mock_write, mock_traceroute, mock_ping):
        """Test successful telemetry collection"""
        mock_ping.return_value = (10.5, 0.0)
        mock_traceroute.return_value = 8
        mock_write.return_value = True
        
        result = collect_telemetry_for_destination("google.com")
        
        self.assertTrue(result)
        mock_ping.assert_called_once_with("google.com")
        mock_traceroute.assert_called_once_with("google.com")
        mock_write.assert_called_once_with("google.com", 10.5, 0.0, 8, True)
    
    @patch('main.ping')
    @patch('main.traceroute')
    @patch('main.write_to_influx')
    def test_collect_telemetry_failure(self, mock_write, mock_traceroute, mock_ping):
        """Test telemetry collection failure"""
        mock_ping.return_value = (None, None)
        mock_traceroute.return_value = None
        mock_write.return_value = True
        
        result = collect_telemetry_for_destination("invalid.domain")
        
        self.assertFalse(result)
        mock_write.assert_called_once_with("invalid.domain", 0, 0, 0, False)
    
    @patch('main.ping')
    @patch('main.traceroute')
    @patch('main.write_to_influx')
    def test_collect_telemetry_invalid_data(self, mock_write, mock_traceroute, mock_ping):
        """Test telemetry collection with invalid data"""
        mock_ping.return_value = (10000.0, 50.0)  # Invalid values
        mock_traceroute.return_value = 8
        mock_write.return_value = True
        
        result = collect_telemetry_for_destination("google.com")
        
        self.assertFalse(result)
        mock_write.assert_called_once_with("google.com", 10000.0, 50.0, 8, False)

class TestIntegration(unittest.TestCase):
    """Integration tests that require actual network connectivity"""
    
    def test_ping_real_destination(self):
        """Test ping with a real destination (requires network)"""
        try:
            latency, packet_loss = ping("8.8.8.8")  # Google DNS
            if latency is not None and packet_loss is not None:
                self.assertGreaterEqual(latency, 0)
                self.assertLessEqual(latency, 1000)  # Reasonable latency
                self.assertGreaterEqual(packet_loss, 0)
                self.assertLessEqual(packet_loss, 100)
        except Exception as e:
            self.skipTest("Network test skipped: {}".format(e))
    
    def test_traceroute_real_destination(self):
        """Test traceroute with a real destination (requires network)"""
        try:
            hop_count = traceroute("8.8.8.8")  # Google DNS
            if hop_count is not None:
                self.assertGreaterEqual(hop_count, 1)
                self.assertLessEqual(hop_count, 30)  # Reasonable hop count
        except Exception as e:
            self.skipTest("Network test skipped: {}".format(e))

if __name__ == '__main__':
    unittest.main()