# Netflix Network Telemetry Dashboard

A real-time network telemetry monitoring system that collects latency, packet loss, and hop count data from multiple destinations and displays it in a beautiful Grafana dashboard.

## Features

- **Real-time Network Monitoring**: Continuously monitors network performance to multiple destinations
- **Comprehensive Metrics**: Tracks latency, packet loss, hop count, and success rates
- **Beautiful Dashboard**: Grafana-based visualization with interactive charts and maps
- **Docker-based**: Easy deployment with Docker Compose
- **Time-series Database**: InfluxDB for efficient data storage and querying
- **Geographic Visualization**: Network path mapping with geographic coordinates

## Dashboard Features

- **Latency Monitoring**: Real-time latency measurements in milliseconds
- **Packet Loss Tracking**: Percentage of packet loss for each destination
- **Hop Count Analysis**: Number of network hops to reach destinations
- **Success Rate Monitoring**: Connection success/failure rates
- **Geographic Map**: Visual representation of network paths
- **Auto-refresh**: Dashboard updates every 30 seconds

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Telemetry     │    │   InfluxDB      │    │   Grafana       │
│   Container     │───▶│   Time-series   │───▶│   Dashboard     │
│   (Data         │    │   Database      │    │   Visualization │
│   Collection)   │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Prerequisites

- Docker and Docker Compose
- Internet connectivity for network testing
- At least 2GB of available RAM

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd netflix-network-telemetry
   ```

2. **Start the services**:
   ```bash
   docker compose up -d
   ```

3. **Access the dashboard**:
   - **Grafana Dashboard**: http://localhost:3000
   - **Username**: admin
   - **Password**: admin123!

## Configuration

### Environment Variables

The telemetry service can be configured using environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `DESTINATIONS` | `google.com,github.com,stackoverflow.com` | Comma-separated list of destinations to monitor |
| `COLLECT_INTERVAL` | `60` | Interval between measurements in seconds |
| `INFLUX_URL` | `http://influxdb2:8086` | InfluxDB connection URL |
| `INFLUX_TOKEN` | (auto-generated) | InfluxDB authentication token |
| `INFLUX_BUCKET` | `default` | InfluxDB bucket name |
| `INFLUX_ORG` | `nflx` | InfluxDB organization name |

### Customizing Destinations

To monitor different destinations, modify the `DESTINATIONS` environment variable in `docker-compose.yml`:

```yaml
environment:
  - DESTINATIONS=google.com,github.com,stackoverflow.com
```

## Testing

### Running Unit Tests

```bash
python test_telemetry.py
```

### Running Integration Tests

```bash
python test_telemetry.py TestIntegration
```

### Test Coverage

The test suite covers:
- Ping functionality and output parsing
- Traceroute functionality and hop counting
- InfluxDB data writing
- Error handling and edge cases
- Dependency checking
- Network connectivity (integration tests)

## Dashboard Metrics

### Latency Panel
- **Unit**: Milliseconds (ms)
- **Thresholds**: 
  - Green: < 50ms
  - Yellow: 50-100ms
  - Red: > 100ms

### Packet Loss Panel
- **Unit**: Percentage (%)
- **Thresholds**:
  - Green: < 1%
  - Yellow: 1-5%
  - Red: > 5%

### Hop Count Panel
- **Unit**: Number of hops
- **Description**: Network path complexity

### Success Rate Panel
- **Unit**: Percentage (%)
- **Description**: Connection success rate over time

### Network Path Map
- **Features**: Geographic visualization of network paths
- **Data**: Real-time location data for each destination

## Troubleshooting

### Dashboard is Blank

1. **Check if services are running**:
   ```bash
   docker compose ps
   ```

2. **Check telemetry logs**:
   ```bash
   docker compose logs telemetry
   ```

3. **Verify InfluxDB data**:
   ```bash
   curl -s -H "Authorization: Token YOUR_TOKEN" \
        "http://localhost:8086/api/v2/query?org=nflx" \
        -d "from(bucket: \"default\") |> range(start: -1h) |> limit(n: 5)"
   ```

### No Data Being Collected

1. **Check network connectivity**:
   ```bash
   docker exec telemetry ping -c 1 google.com
   ```

2. **Verify environment variables**:
   ```bash
   docker exec telemetry env | grep INFLUX
   ```

3. **Check InfluxDB connection**:
   ```bash
   curl -s "http://localhost:8086/health"
   ```

### High Latency or Packet Loss

- This is normal behavior and indicates actual network conditions
- The dashboard will show these metrics accurately
- Consider adding more destinations to compare performance

## Development

### Project Structure

```
netflix-network-telemetry/
├── docker-compose.yml          # Service orchestration
├── telemetry/                  # Telemetry service
│   ├── Dockerfile             # Container definition
│   ├── main.py               # Main telemetry script
│   ├── run_telemetry.sh      # Shell script wrapper
│   └── requirements.txt      # Python dependencies
├── grafana/                   # Grafana configuration
│   ├── dashboards/           # Dashboard definitions
│   └── provisioning/         # Auto-provisioning config
├── influxdb2_data/           # InfluxDB data persistence
├── test_telemetry.py         # Unit and integration tests
└── README.md                 # This file
```

### Adding New Metrics

1. **Modify the telemetry script** (`telemetry/main.py`)
2. **Update the dashboard** (`grafana/dashboards/network-telemetry.json`)
3. **Add tests** (`test_telemetry.py`)
4. **Rebuild and restart**:
   ```bash
   docker compose build telemetry
   docker compose up -d telemetry
   ```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Performance Considerations

- **Data Retention**: InfluxDB automatically manages data retention
- **Resource Usage**: 
  - Telemetry: ~50MB RAM
  - InfluxDB: ~200MB RAM
  - Grafana: ~100MB RAM
- **Network Impact**: Minimal - only ping and traceroute commands
- **Storage**: ~10MB/day for typical usage

## Security

- **Default Credentials**: Change default passwords in production
- **Network Access**: Services are bound to localhost by default
- **Token Management**: InfluxDB tokens are auto-generated
- **Container Security**: Running as non-root user

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs: `docker compose logs`
3. Run the test suite: `python test_telemetry.py`
4. Open an issue on GitHub 