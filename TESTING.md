# Testing

This project includes tests to ensure the dashboard and telemetry system work correctly.

## Test Files

### test_dashboard.py
Validates the Grafana dashboard configuration:
- JSON syntax validation
- Required dashboard fields
- Panel configurations
- Geomap panel validation
- Timeseries panel validation
- Query target validation

### test_integration.py
Tests the overall system health:
- Docker services running
- Dashboard file exists and valid
- Telemetry functions present
- InfluxDB connection
- Grafana connection
- Data availability

### run_tests.py
Master test runner that executes all tests:
- Runs dashboard validation
- Runs integration tests
- Provides comprehensive test summary

### safe_edit.py
Safe editing workflow:
- Pre-change validation
- Automatic backups
- Post-change validation
- Safe Grafana restarts

## Usage

### Run All Tests
```bash
python3 run_tests.py
```

### Safe Dashboard Editing
```bash
# 1. Prepare for editing (runs tests + creates backup)
python3 safe_edit.py

# 2. Edit the dashboard file
# ... make your changes ...

# 3. Validate changes
python3 safe_edit.py --validate

# 4. Apply changes (restarts Grafana)
python3 safe_edit.py --restart
```

### Individual Tests
```bash
# Dashboard validation only
python3 test_dashboard.py

# Integration tests only
python3 test_integration.py
```

## Safety Features

### Automatic Backups
- Creates timestamped backups before changes
- Backup location: `grafana/dashboards/network-telemetry.json.backup_YYYYMMDD_HHMMSS`

### Validation Checks
- JSON syntax validation
- Required field validation
- Panel configuration validation
- Query syntax validation

### Pre/Post Change Testing
- Runs comprehensive tests before changes
- Validates changes after editing
- Prevents broken configurations from being applied

## Test Coverage

### Dashboard Validation
- JSON syntax
- Required fields (title, panels, schemaVersion)
- Panel configurations
- Geomap panel validation
- Timeseries panel validation
- Query target validation
- Layer configuration validation

### Integration Testing
- Docker services health
- File existence and validity
- Database connectivity
- Grafana accessibility
- Data availability

### Safety Features
- Automatic backups
- Pre-change validation
- Post-change validation
- Safe service restarts

## Adding New Tests

To add new tests:

1. **Dashboard Tests**: Add validation logic to `test_dashboard.py`
2. **Integration Tests**: Add system checks to `test_integration.py`
3. **Custom Tests**: Create new test files and add to `run_tests.py`

### Example: Adding a New Dashboard Test
```python
def test_new_feature(self):
    """Test new dashboard feature"""
    # Your test logic here
    pass
```

## Best Practices

1. Always run tests before making changes
2. Use the safe edit workflow for dashboard changes
3. Check test results before applying changes
4. Keep backups of working configurations
5. Add tests for new features

## Troubleshooting

### Tests Failing
1. Check Docker services are running
2. Verify dashboard JSON is valid
3. Ensure all required files exist
4. Check network connectivity

### Dashboard Not Loading
1. Run `python3 test_dashboard.py` to check configuration
2. Check Grafana logs: `docker logs grafana`
3. Validate JSON syntax manually
4. Restore from backup if needed

### Integration Issues
1. Run `python3 test_integration.py` to identify issues
2. Check service status: `docker ps`
3. Verify database connectivity
4. Check Grafana accessibility 