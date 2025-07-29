#!/bin/bash

echo "🚀 Starting telemetry loop..."

while true; do
    echo "📡 Running telemetry cycle..."
    python main.py
    echo "⏰ Telemetry cycle completed, restarting..."
done