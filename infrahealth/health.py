import psutil
import time
import platform
from typing import Dict
import logging

logging.basicConfig(
    filename="infrahealth.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def get_server_health(detailed: bool = False) -> Dict[str, float]:
    """
    Fetch server health metrics for the local system.

    Args:
        detailed (bool): If True, include additional metrics (network, uptime, processes, load).

    Returns:
        Dict containing system metrics (percentages, counts, or times).

    Raises:
        RuntimeError: If fetching metrics fails (e.g., permission denied).
    """
    try:
        # Basic metrics
        health = {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage("/").percent
        }

        if detailed:
            # Network metrics
            net = psutil.net_io_counters()
            health["network_bytes_sent"] = net.bytes_sent
            health["network_bytes_received"] = net.bytes_recv

            # Uptime (seconds since boot)
            health["uptime_seconds"] = time.time() - psutil.boot_time()

            # Process count
            health["process_count"] = len(psutil.pids())

            # Load average (Linux only)
            if platform.system() == "Linux":
                load1, load5, load15 = psutil.getloadavg()
                health["load_avg_1min"] = load1
                health["load_avg_5min"] = load5
                health["load_avg_15min"] = load15

        logging.info("Fetched server health: %s", health)
        return health
    except PermissionError as e:
        logging.error(
            "Permission denied while fetching server health: %s", str(e))
        raise RuntimeError("Permission denied. Try running with sudo.")
    except Exception as e:
        logging.error("Failed to fetch server health: %s", str(e))
        raise RuntimeError(f"Failed to fetch server health: {str(e)}")
