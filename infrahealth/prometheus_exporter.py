from prometheus_client import start_http_server, Gauge
from .health import get_server_health
from .docker_health import get_docker_health
import time
import logging

logging.basicConfig(
    filename="infrahealth.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def export_metrics(port: int = 8000):
    """Export server and Docker metrics to Prometheus."""
    server_cpu = Gauge("infrahealth_server_cpu_percent",
                       "Server CPU usage percentage")
    server_memory = Gauge("infrahealth_server_memory_percent",
                          "Server memory usage percentage")
    server_disk = Gauge("infrahealth_server_disk_percent",
                        "Server disk usage percentage")
    container_cpu = Gauge("infrahealth_container_cpu_percent",
                          "Container CPU usage percentage", ["container_name"])
    container_memory = Gauge("infrahealth_container_memory_percent",
                             "Container memory usage percentage", ["container_name"])

    start_http_server(port)
    logging.info("Started Prometheus exporter on port %d", port)

    while True:
        try:
            # Server metrics
            server_health = get_server_health(detailed=False)
            server_cpu.set(server_health["cpu_percent"])
            server_memory.set(server_health["memory_percent"])
            server_disk.set(server_health["disk_percent"])

            # Docker metrics
            docker_health = get_docker_health(detailed=False)
            for container in docker_health:
                container_cpu.labels(container_name=container["name"]).set(
                    container["cpu_percent"])
                container_memory.labels(container_name=container["name"]).set(
                    container["memory_percent"])
        except Exception as e:
            logging.error("Failed to export metrics: %s", str(e))
        time.sleep(10)
