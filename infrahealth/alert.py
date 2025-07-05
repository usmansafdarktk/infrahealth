import logging
import smtplib
from email.message import EmailMessage
from typing import List, Dict

logging.basicConfig(
    filename="infrahealth.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def send_alert(health_data: Dict, alert_config: Dict) -> None:
    """
    Send email alert if metrics exceed thresholds.

    Args:
        health_data: Server or Docker health metrics.
        alert_config: Thresholds and email settings.
    """
    try:
        issues = []
        if isinstance(health_data, list):  # Docker metrics
            for container in health_data:
                if container["cpu_percent"] > alert_config.get("cpu_threshold", 80):
                    issues.append(
                        f"Container {container['name']}: CPU {container['cpu_percent']}%")
                if container["memory_percent"] > alert_config.get("memory_threshold", 80):
                    issues.append(
                        f"Container {container['name']}: Memory {container['memory_percent']}%")
                if container.get("restart_count", 0) > alert_config.get("restart_threshold", 5):
                    issues.append(
                        f"Container {container['name']}: Restarts {container['restart_count']}")
        else:  # Server metrics
            if health_data["cpu_percent"] > alert_config.get("cpu_threshold", 80):
                issues.append(f"Server: CPU {health_data['cpu_percent']}%")
            if health_data["memory_percent"] > alert_config.get("memory_threshold", 80):
                issues.append(
                    f"Server: Memory {health_data['memory_percent']}%")

        if issues:
            msg = EmailMessage()
            msg.set_content("\n".join(issues))
            msg["Subject"] = "Infrahealth Alert"
            msg["From"] = alert_config["email_from"]
            msg["To"] = alert_config["email_to"]
            with smtplib.SMTP(alert_config["smtp_host"], alert_config["smtp_port"]) as server:
                server.login(alert_config["email_user"],
                             alert_config["email_password"])
                server.send_message(msg)
            logging.info("Sent alert: %s", issues)
    except Exception as e:
        logging.error("Failed to send alert: %s", str(e))
