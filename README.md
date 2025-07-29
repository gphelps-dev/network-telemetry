# Network Telemetry Dashboard

A production-ready network monitoring solution that captures latency, packet loss, and hop count metrics to help diagnose network issues between your location and target FQDNs.

## Features

- **Network Diagnostics**: Monitor latency, packet loss, and hop count to any FQDN
- **Configurable Destinations**: Support teams can easily modify target destinations via environment variables
- **Production-Ready**: Clean, organized dashboard with essential metrics only
- **Docker-based**: Easy deployment with Docker Compose
- **Time-series Database**: InfluxDB for efficient data storage and querying
- **Secure Configuration**: Environment-based secrets management

## Quick Start

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd netflix-network-telemetry
   ```

2. **Set up environment variables**:
   ```bash
   # Copy the example environment file
   cp env.example .env
   
   # Edit .env with your secure values
   nano .env
   ```

3. **Start the services**:
   ```bash
   docker compose up -d
   ```

4. **Access the dashboard**:
   - **Grafana Dashboard**: http://localhost:3000
   - **Authentication**: Admin login (admin/admin123!) or GitHub OAuth
   - **Network Telemetry Dashboard**: http://localhost:3000/d/network-telemetry/network-telemetry-dashboard
   - **Network Telemetry Dashboard (Built-in Geomap)**: http://localhost:3000/d/network-telemetry-geomap/network-telemetry-dashboard-built-in-geomap
   - **Network Telemetry Dashboard with Routes**: http://localhost:3000/d/network-telemetry-routes/network-telemetry-dashboard-with-routes
   - **Network Telemetry Dashboard with Flow-Styled Routes**: http://localhost:3000/d/network-telemetry-flow-routes/network-telemetry-dashboard-with-flow-styled-routes

## Measurement Location

This system measures network performance **from your local machine** (where Docker is running) to the configured destinations. The telemetry container runs on your local system and performs:

- **Ping measurements** from your location to target FQDNs
- **Traceroute analysis** to determine network hops from your location
- **Real-time monitoring** of network conditions from your network

**Current measurement destinations:**
- google.com
- github.com
- stackoverflow.com
- cloudflare.com
- netflix.com

You can modify these destinations by editing the `NETWORK_DESTINATIONS` environment variable in your `.env` file.

## Network Diagnostics Configuration

### For Support Teams

This system is designed to help diagnose network issues between your location and any FQDN. Support teams can easily modify the target destinations:

#### 1. **Configure Destinations**

Edit the `.env` file and modify the `NETWORK_DESTINATIONS` variable:

```bash
# Example: Monitor specific services for troubleshooting
NETWORK_DESTINATIONS=api.company.com,cdn.company.com,database.company.com

# Example: Monitor external dependencies
NETWORK_DESTINATIONS=aws.amazon.com,cloudflare.com,github.com

# Example: Monitor single destination for focused debugging
NETWORK_DESTINATIONS=problematic-service.company.com
```

#### 2. **Deploy and Monitor**

```bash
# Restart services with new configuration
docker compose down
docker compose up -d

# Check telemetry logs
docker compose logs telemetry
```

#### 3. **Analyze Network Issues**

The dashboard will show:
- **Latency trends** - Identify performance degradation
- **Packet loss** - Detect network instability
- **Hop count changes** - Identify routing changes
- **Connection success rate** - Monitor reliability

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `NETWORK_DESTINATIONS` | Comma-separated FQDNs to monitor | `google.com,github.com,stackoverflow.com` | No |
| `TELEMETRY_COLLECT_INTERVAL` | Collection interval in seconds | `60` | No |
| `INFLUXDB_TOKEN` | InfluxDB authentication token | - | Yes |
| `GITHUB_CLIENT_ID` | GitHub OAuth client ID | - | Yes |
| `GITHUB_CLIENT_SECRET` | GitHub OAuth client secret | - | Yes |

## Environment Setup

### Security Configuration

This project uses environment variables for secure configuration. The `.env` file contains sensitive information and is excluded from version control.

**Required Environment Variables:**

| Variable | Description | Required |
|----------|-------------|----------|
| `INFLUXDB_TOKEN` | InfluxDB authentication token | Yes |
| `GITHUB_CLIENT_ID` | GitHub OAuth client ID | Yes |
| `GITHUB_CLIENT_SECRET` | GitHub OAuth client secret | Yes |

**Optional Environment Variables:**

| Variable | Default | Description |
|----------|---------|-------------|
| `NETWORK_DESTINATIONS` | google.com,github.com,stackoverflow.com | FQDNs to monitor for network diagnostics |
| `TELEMETRY_COLLECT_INTERVAL` | 60 | Collection interval in seconds |
| `INFLUXDB_ADMIN_USER` | admin | InfluxDB admin username |
| `INFLUXDB_ADMIN_PASSWORD` | admin123! | InfluxDB admin password |
| `GITHUB_OAUTH_ENABLED` | true | Enable GitHub OAuth |
| `GITHUB_SCOPES` | user | GitHub OAuth scopes |
| `GITHUB_ALLOW_SIGN_UP` | true | Allow new user sign-ups |
| `GITHUB_ALLOWED_ORGANIZATIONS` | | Restrict to specific GitHub organizations |
| `GITHUB_TEAM_IDS` | | Restrict to specific GitHub teams |

### Setting Up GitHub OAuth

1. Create a GitHub OAuth App (see `GITHUB_OAUTH_SETUP.md`)
2. Add your GitHub credentials to `.env`:
   ```bash
   GITHUB_CLIENT_ID=your_client_id
   GITHUB_CLIENT_SECRET=your_client_secret
   ```

### Generating InfluxDB Token

The InfluxDB token is automatically generated on first run. You can also generate one manually:

```bash
# Access the InfluxDB container
docker exec -it influxdb2 influx

# Generate a token
influx auth create --org nflx --token-description "telemetry-token"
```

### Authentication

This Grafana instance supports both **admin login** and **GitHub OAuth**:

- **Admin Login**: Username `admin`, Password `admin123!`
- **GitHub OAuth**: Configured for team authentication (if GitHub credentials are provided)

You can use either method to access the dashboard.

### Configuring Grafana Datasource

The InfluxDB datasource is automatically configured. If you need to manually configure it:

1. Go to Grafana → Configuration → Data Sources
2. Add InfluxDB datasource
3. Use the token from your `.env` file

## Dashboard Features

### Network Metrics

- **Latency Monitoring**: Real-time latency measurements to each destination
- **Packet Loss Tracking**: Monitor network stability and quality
- **Hop Count Analysis**: Track routing changes and network topology
- **Connection Success Rate**: Monitor reliability with gauge visualization

### Diagnostic Capabilities

- **Trend Analysis**: Identify performance degradation over time
- **Comparative Monitoring**: Compare performance across multiple destinations
- **Alerting**: Set up alerts for latency spikes or packet loss
- **Historical Data**: Access historical network performance data
- **Current Status Table**: Real-time overview of all destinations

### Network Map Visualization

The system includes modern network visualization dashboards using [Grafana's built-in Geomap visualization](https://grafana.com/docs/grafana/latest/panels-visualizations/visualizations/geomap/):

- **Geographic Network Map**: Visual representation of network destinations with real-time metrics
- **Interactive Markers**: Click on destinations to view detailed telemetry data
- **Dynamic Styling**: Color-coded markers based on latency and packet loss thresholds
- **Real-time Updates**: Live updates of network status and performance metrics every 5 seconds
- **Modern UI**: Clean, responsive interface using built-in Grafana geomap technology

#### Geomap Features Implemented:

- **Markers Layer**: Orange circle markers showing network destinations
- **Text Layer**: Hop count labels displayed above each destination
- **Tooltip Details**: Hover to see latency, packet loss, and hop count
- **Auto Location**: Automatically detects latitude/longitude from data fields
- **Map Controls**: Zoom, pan, and scale controls enabled
- **Dark Theme**: Optimized for dark dashboard theme

#### Supported Data Format:
The geomap uses latitude/longitude coordinates with the following fields:
- `lat`: Latitude coordinates (hardcoded for each destination)
- `lon`: Longitude coordinates (hardcoded for each destination)
- `destination`: Hostname being monitored
- `latency`: Ping latency in milliseconds
- `packet_loss`: Packet loss percentage
- `hop_count`: Number of network hops

The system provides map-based dashboards:
- **Network Telemetry Geomap Dashboard** (`network-telemetry-geomap.json`): Uses built-in geomap panel with hop information
- **Network Telemetry Dashboard with Routes** (`network-telemetry-with-routes.json`): Includes [route layers](https://grafana.com/docs/grafana/latest/panels-visualizations/visualizations/geomap/#route-layer-beta) showing network paths
- **Network Telemetry Dashboard with Flow-Styled Routes** (`network-telemetry-with-routes-enhanced.json`): Advanced route visualization with [flow-based styling](https://viglino.github.io/ol-ext/examples/style/map.style.flowline.html) - color varies by latency, width by packet loss

These dashboards provide improved visual experiences with better performance compared to external map plugins.

## Troubleshooting

### Common Issues

1. **No data appearing**: Check that `INFLUXDB_TOKEN` is set correctly
2. **Authentication issues**: Verify GitHub OAuth credentials
3. **Network connectivity**: Ensure containers can reach the internet
4. **Destination unreachable**: Verify FQDNs are accessible from your network

### Support Team Usage

For network diagnostics:

1. **Identify the problematic FQDN**
2. **Add it to `NETWORK_DESTINATIONS`** in `.env`
3. **Restart services**: `docker compose restart telemetry`
4. **Monitor the dashboard** for latency, packet loss, and hop count
5. **Analyze trends** to identify root cause

### Logs and Debugging

```bash
# View telemetry logs
docker compose logs telemetry

# Check InfluxDB data
docker exec influxdb2 influx query --org nflx --token YOUR_TOKEN 'from(bucket: "default") |> range(start: -1h)'

# Test individual destination
docker compose exec telemetry ping -c 4 your-destination.com
```

## Development

### Adding New Metrics

To add new network metrics:

1. Modify `telemetry/main.py` to collect additional data
2. Update the InfluxDB write function to store new fields
3. Add corresponding panels to the Grafana dashboard

### Custom Destinations

To monitor custom destinations:

1. Edit `NETWORK_DESTINATIONS` in `.env`
2. Restart the telemetry service
3. Verify data collection in Grafana

## Production Deployment

### Security Considerations

- **Change default passwords** in production environments
- **Use strong InfluxDB tokens** for authentication
- **Restrict network access** to necessary ports only
- **Monitor container logs** for security events

### Performance Optimization

- **Data retention**: Configure InfluxDB retention policies
- **Resource limits**: Set appropriate Docker resource limits
- **Monitoring**: Add container health checks
- **Backup**: Implement regular data backups

### Scaling

- **Multiple destinations**: Add more FQDNs to monitor
- **Collection frequency**: Adjust `TELEMETRY_COLLECT_INTERVAL`
- **Storage**: Increase InfluxDB storage capacity
- **High availability**: Deploy with multiple instances

## License

This project is licensed under the MIT License. 