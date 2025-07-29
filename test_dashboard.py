#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify dashboard queries are working
"""

import requests
import json

# InfluxDB configuration
INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "SlhPxmQPGdRbxnVO5onZOJwqiuf8_9pqdIJPuNpUFKRiPBRlDHyOdMqJEaKNuK1CEFSWH9It0FtYM619I8pIlA=="
INFLUX_ORG = "nflx"

def test_query(query_name, flux_query):
    """Test a Flux query and return results"""
    headers = {
        "Authorization": "Token " + INFLUX_TOKEN,
        "Content-Type": "application/vnd.flux"
    }
    
    url = INFLUX_URL + "/api/v2/query?org=" + INFLUX_ORG
    
    try:
        response = requests.post(url, headers=headers, data=flux_query, timeout=10)
        if response.status_code == 200:
            data = response.text
            lines = data.strip().split('\n')
            if len(lines) > 1:  # Has data (header + at least one data row)
                print("SUCCESS: " + query_name + " - " + str(len(lines)-1) + " data points")
                return True
            else:
                print("NO DATA: " + query_name)
                return False
        else:
            print("HTTP ERROR: " + query_name + " - " + str(response.status_code) + " - " + response.text)
            return False
    except Exception as e:
        print("ERROR: " + query_name + " - " + str(e))
        return False

def main():
    """Test all dashboard queries"""
    print("Testing Dashboard Queries...")
    print("=" * 50)
    
    # Test queries from the dashboard
    queries = {
        "Latency Panel": '''from(bucket: "default")
  |> range(start: -15m)
  |> filter(fn: (r) => r._measurement == "network_telemetry")
  |> filter(fn: (r) => r._field == "latency")
  |> filter(fn: (r) => r.destination != "test")''',
        
        "Packet Loss Panel": '''from(bucket: "default")
  |> range(start: -15m)
  |> filter(fn: (r) => r._measurement == "network_telemetry")
  |> filter(fn: (r) => r._field == "packet_loss")
  |> filter(fn: (r) => r.destination != "test")''',
        
        "Hop Count Panel": '''from(bucket: "default")
  |> range(start: -15m)
  |> filter(fn: (r) => r._measurement == "network_telemetry")
  |> filter(fn: (r) => r._field == "hop_count")
  |> filter(fn: (r) => r.destination != "test")''',
        
        "Success Rate Panel": '''from(bucket: "default")
  |> range(start: -15m)
  |> filter(fn: (r) => r._measurement == "network_telemetry")
  |> filter(fn: (r) => r._field == "success")
  |> filter(fn: (r) => r.destination != "test")
  |> aggregateWindow(every: 1m, fn: mean, createEmpty: false)
  |> map(fn: (r) => ({r with _value: r._value * 100.0}))''',
        
        "Network Map": '''from(bucket: "default")
  |> range(start: -15m)
  |> filter(fn: (r) => r._measurement == "network_telemetry")
  |> filter(fn: (r) => r._field == "latency")
  |> filter(fn: (r) => r.destination != "test")
  |> last()
  |> map(fn: (r) => ({
    _time: r._time,
    _value: r._value,
    destination: r.destination,
    lat: if r.destination == "google.com" then 37.4225 else if r.destination == "cloudflare.com" then 43.6532 else 40.7128,
    lon: if r.destination == "google.com" then -122.085 else if r.destination == "cloudflare.com" then -79.3832 else -74.0060,
    hop_label: r.destination
  }))'''
    }
    
    results = {}
    for name, query in queries.items():
        results[name] = test_query(name, query)
    
    print("\n" + "=" * 50)
    print("SUMMARY:")
    successful = sum(results.values())
    total = len(results)
    print("SUCCESS: " + str(successful) + "/" + str(total) + " queries successful")
    
    if successful == total:
        print("All dashboard queries are working!")
    else:
        print("Some queries are failing. Check the errors above.")
    
    return successful == total

if __name__ == "__main__":
    main()