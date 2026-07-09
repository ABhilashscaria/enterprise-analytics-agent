#!/bin/bash

# Exit on any error
set -e

echo "=== Setting up local monitoring environment (No Docker) ==="

# Create a directory to hold the binaries so we don't clutter the project root
mkdir -p monitoring_local
cd monitoring_local

# 1. Download and Extract Prometheus (v2.53.0)
echo "Downloading Prometheus..."
wget -q -nc https://github.com/prometheus/prometheus/releases/download/v2.53.0/prometheus-2.53.0.linux-amd64.tar.gz
tar -xzf prometheus-2.53.0.linux-amd64.tar.gz
ln -sf prometheus-2.53.0.linux-amd64/prometheus prometheus-bin

# Create a prometheus configuration file that points to your FastAPI app
cat << 'EOF' > prometheus.yml
global:
  scrape_interval: 5s

scrape_configs:
  - job_name: "enterprise-analytics-agent"
    static_configs:
      - targets: ["localhost:8000"]
EOF

echo "Prometheus setup complete."

# 2. Download and Extract Grafana (v11.1.0)
echo "Downloading Grafana..."
wget -q -nc https://dl.grafana.com/oss/release/grafana-11.1.0.linux-amd64.tar.gz
tar -xzf grafana-11.1.0.linux-amd64.tar.gz
ln -sf grafana-11.1.0/bin/grafana grafana-bin

echo "Grafana setup complete."

echo ""
echo "=== Setup Complete ==="
echo ""
echo "To start Prometheus, run:"
echo "  cd monitoring_local && ./prometheus-bin --config.file=prometheus.yml"
echo ""
echo "To start Grafana, open a new terminal tab and run:"
echo "  cd monitoring_local/grafana-11.1.0 && ./bin/grafana server"
echo ""
echo "Grafana will be available at http://localhost:3000 (default login: admin / admin)"
echo "Prometheus will be available at http://localhost:9090"
