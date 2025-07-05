## Infrahealth CLI

A command-line tool for monitoring server and Docker container health, including CPU, memory, disk, network, and application metrics, with support for Prometheus export and alerting.

## Features

- Monitor server health (`check server`): CPU, memory, disk, network, uptime, processes, and load averages.
- Monitor Docker containers (`check docker`): CPU, memory, network, and restart counts.
- Alerting: Send email notifications for high resource usage.
- Prometheus integration: Export metrics for visualization.
- Output formats: Text or JSON.

## Installation

```bash
pip install git+https://github.com/<your-username>/infrahealth.git
```
## Usage

```bash
# Check server health
infrahealth check server
infrahealth check server --detailed --format json

# Check Docker container health
infrahealth check docker
infrahealth check docker --detailed --alert

# Start Prometheus exporter
infrahealth start-prometheus --port 8000
```
## Requirements
```bash
Python 3.6+

Libraries: click, psutil, docker, requests, prometheus_client

Optional: Docker for container monitoring, Prometheus
```

## Setup

``` bash

# Clone the repository
git clone https://github.com/<your-username>/infrahealth.git
cd infrahealth

# Install dependencies
pip install -e .

# Run tests
pytest

```


## Development

Contributions are welcome! To contribute:
```bash
# Fork the repository

# Create a feature branch
git checkout -b feature/xyz

# Commit changes
git commit -m "Add xyz feature"

# Push to the branch
git push origin feature/xyz

# Open a pull request on GitHub
```

## License

MIT License
