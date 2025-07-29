#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import time
import datetime
import requests
import sys
import re

print("🚀 main.py is running")

# Config from environment variables
INFLUX_URL = os.getenv("INFLUX_URL", "http://influxdb2:8086")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN", "")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET", "default")
INFLUX_ORG = os.getenv("INFLUX_ORG", "nflx")
DESTINATIONS = os.getenv("DESTINATIONS", "google.com,netflix.com,cloudflare.com").split(",")
INTERVAL = int(os.getenv("COLLECT_INTERVAL", 60))

print("📡 Monitoring destinations: {}".format(', '.join(DESTINATIONS)))

def check_dependencies():
    """Check if required system tools are available"""
    try:
        subprocess.run(["ping", "-c", "1", "127.0.0.1"], capture_output=True, check=True)
        subprocess.run(["traceroute", "-n", "127.0.0.1"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print("❌ Missing required tools: {}".format(e))
        return False

def ping(destination):
    """Perform ping and return latency and packet loss"""
    try:
        output = subprocess.check_output(
            ["ping", "-c", "4", "-W", "5", destination], 
            stderr=subprocess.STDOUT
        ).decode('utf-8')
        
        # Parse ping output - handle both Linux and macOS formats
        if "round-trip min/avg/max" in output:
            # macOS format
            rtt_line = output.split("round-trip min/avg/max")[1].split("=")[1].strip()
            avg_latency = float(rtt_line.split("/")[1])
            
            # Parse packet loss from statistics line
            stats_line = [line for line in output.splitlines() if "packets transmitted" in line][0]
            packet_loss = float(stats_line.split(", ")[2].split("%")[0])
            return avg_latency, packet_loss
        elif "rtt min/avg/max/mdev = " in output:
            # Linux format
            rtt_line = output.split("rtt min/avg/max/mdev = ")[1].split("\n")[0]
            avg_latency = float(rtt_line.split("/")[1])
            
            # Parse packet loss
            if "packets transmitted" in output:
                stats_line = [line for line in output.splitlines() if "packets transmitted" in line][0]
                packet_loss = float(stats_line.split(", ")[2].split("%")[0])
                return avg_latency, packet_loss
        
        print("❌ Could not parse ping output for {}".format(destination))
        return None, None
        
    except Exception as e:
        print("❌ Ping failed for {}: {}".format(destination, e))
        return None, None

def traceroute(destination):
    """Perform traceroute and return hop count"""
    try:
        output = subprocess.check_output(
            ["traceroute", "-n", "-w", "3", destination], 
            stderr=subprocess.STDOUT
        ).decode('utf-8')
        
        # Parse traceroute output to count hops
        hop_count = 0
        for line in output.splitlines()[1:]:  # Skip first line (header)
            if line.strip() and "*" not in line and "ms" in line:
                # Extract IP address using regex
                ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                if ip_match:
                    hop_count += 1
        
        return hop_count if hop_count > 0 else None
        
    except Exception as e:
        print("❌ Traceroute failed for {}: {}".format(destination, e))
        return None

def write_to_influx(destination, latency, packet_loss, hops, success=True):
    """Write metrics to InfluxDB"""
    if not INFLUX_TOKEN:
        print("❌ No InfluxDB token provided")
        return False
    
    timestamp = int(time.time() * 1e9)
    
    # Write basic network telemetry
    payload = "network_telemetry,destination={} latency={},packet_loss={},hop_count={},success={} {}".format(
        destination, latency, packet_loss, hops, 1.0 if success else 0.0, timestamp
    )
    
    headers = {
        "Authorization": "Token {}".format(INFLUX_TOKEN),
        "Content-Type": "text/plain; charset=utf-8"
    }
    url = "{}/api/v2/write?org={}&bucket={}&precision=ns".format(INFLUX_URL, INFLUX_ORG, INFLUX_BUCKET)

    try:
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        if response.status_code == 204:
            status = "✅" if success else "⚠️"
            print("{} Wrote to InfluxDB at {} — {}: latency={}ms, packet_loss={}%, hops={}, success={}".format(
                status, datetime.datetime.now(), destination, latency, packet_loss, hops, success
            ))
            return True
        else:
            print("❌ Failed to write to InfluxDB: {} {}".format(response.status_code, response.text))
            return False
    except requests.exceptions.RequestException as e:
        print("❌ Network error writing to InfluxDB: {}".format(e))
        return False

def collect_telemetry_for_destination(destination):
    """Collect telemetry data for a single destination"""
    print("[{}] Running telemetry to {}".format(datetime.datetime.now(), destination))
    
    latency, packet_loss = ping(destination)
    hops = traceroute(destination)

    # Validate data before writing
    if latency is not None and packet_loss is not None and hops is not None:
        if 0 <= latency <= 10000 and 0 <= packet_loss <= 100 and 0 <= hops <= 50:
            write_to_influx(destination, latency, packet_loss, hops, success=True)
            return True
        else:
            print("⚠️ Invalid data for {}: latency={}, packet_loss={}, hops={}".format(destination, latency, packet_loss, hops))
            write_to_influx(destination, latency or 0, packet_loss or 0, hops or 0, success=False)
            return False
    else:
        print("⚠️ Skipping write for {} due to missing data".format(destination))
        write_to_influx(destination, 0, 0, 0, success=False)
        return False

if __name__ == "__main__":
    print("🚀 Telemetry script has started")
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Missing required system tools. Exiting.")
        sys.exit(1)
    
    consecutive_failures = 0
    max_failures = 5
    destination_index = 0
    
    while True:
        try:
            # Round-robin through destinations
            destination = DESTINATIONS[destination_index]
            
            success = collect_telemetry_for_destination(destination)
            
            if success:
                consecutive_failures = 0
            else:
                consecutive_failures += 1
            
            # Move to next destination
            destination_index = (destination_index + 1) % len(DESTINATIONS)
            
            # Exit if too many consecutive failures
            if consecutive_failures >= max_failures:
                print("❌ Too many consecutive failures ({}). Exiting.".format(consecutive_failures))
                sys.exit(1)
                
        except KeyboardInterrupt:
            print("\n🛑 Telemetry script stopped by user")
            sys.exit(0)
        except Exception as e:
            print("❌ Unexpected error: {}".format(e))
            consecutive_failures += 1
            
            if consecutive_failures >= max_failures:
                print("❌ Too many consecutive failures ({}). Exiting.".format(consecutive_failures))
                sys.exit(1)

        print("⏰ Waiting {} seconds before next measurement...".format(INTERVAL))
        time.sleep(INTERVAL)