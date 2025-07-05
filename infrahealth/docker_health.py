import docker
from typing import List, Dict
import logging

logging.basicConfig(
    filename="infrahealth.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def get_docker_health(detailed: bool = False, app_check: bool = False) -> List[Dict]:
    try:
        client = docker.from_env()
        containers = client.containers.list()
        health_data = []
        for container in containers:
            stats = container.stats(stream=False)
            data = {
                "name": container.name,
                "status": container.status,
                "cpu_percent": calculate_cpu_percent(stats),
                "memory_percent": calculate_memory_percent(stats)
            }
            if detailed:
                data.update({
                    "network_bytes_sent": stats["networks"].get("eth0", {}).get("tx_bytes", 0),
                    "network_bytes_received": stats["networks"].get("eth0", {}).get("rx_bytes", 0),
                    "restart_count": container.attrs["RestartCount"]
                })
            if app_check:
                data.update(check_app_health(container))
            health_data.append(data)
        logging.info("Fetched Docker health: %s", health_data)
        return health_data
    except docker.errors.DockerException as e:
        logging.error("Failed to fetch Docker health: %s", str(e))
        raise RuntimeError(
            f"Failed to fetch Docker health: {str(e)}. Ensure Docker is running and you have permissions.")
    finally:
        if 'client' in locals():
            client.close()


def check_app_health(container: docker.models.containers.Container) -> Dict:
    """Check application health via HTTP endpoint."""
    try:
        # Example: Check if container exposes a health endpoint
        exec_result = container.exec_run(
            "curl --fail http://localhost/health || exit 1")
        return {"app_health": "healthy" if exec_result.exit_code == 0 else "unhealthy"}
    except docker.errors.APIError as e:
        logging.error("Failed to check app health for %s: %s",
                      container.name, str(e))
        return {"app_health": "unhealthy"}


def calculate_cpu_percent(stats: Dict) -> float:
    """Calculate CPU usage percentage from container stats."""
    cpu_stats = stats["cpu_stats"]
    precpu_stats = stats["precpu_stats"]
    cpu_delta = cpu_stats["cpu_usage"]["total_usage"] - \
        precpu_stats["cpu_usage"]["total_usage"]
    system_delta = cpu_stats["system_cpu_usage"] - \
        precpu_stats["system_cpu_usage"]
    num_cpus = cpu_stats["online_cpus"]
    return (cpu_delta / system_delta * num_cpus * 100.0) if system_delta > 0 else 0.0


def calculate_memory_percent(stats: Dict) -> float:
    """Calculate memory usage percentage from container stats."""
    memory_stats = stats["memory_stats"]
    used = memory_stats["usage"] - \
        memory_stats.get("stats", {}).get("cache", 0)
    limit = memory_stats["limit"]
    return (used / limit * 100.0) if limit > 0 else 0.0
