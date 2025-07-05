import pytest
from unittest.mock import patch, MagicMock
from infrahealth.docker_health import get_docker_health


@patch("docker.from_env")
def test_get_docker_health_basic(mock_docker):
    """Test fetching basic Docker container health metrics."""
    mock_client = MagicMock()
    mock_container = MagicMock()
    mock_container.name = "test-container"
    mock_container.status = "running"
    mock_container.stats.return_value = {
        "cpu_stats": {
            "cpu_usage": {"total_usage": 2000},
            "system_cpu_usage": 10000,
            "online_cpus": 2
        },
        "precpu_stats": {
            "cpu_usage": {"total_usage": 1000},
            "system_cpu_usage": 5000
        },
        "memory_stats": {
            "usage": 1000000,
            "limit": 2000000,
            "stats": {"cache": 100000}
        }
    }
    mock_client.containers.list.return_value = [mock_container]
    mock_docker.return_value = mock_client

    health = get_docker_health(detailed=False)
    assert len(health) == 1
    assert health[0]["name"] == "test-container"
    assert health[0]["status"] == "running"
    assert health[0]["cpu_percent"] == 40.0  # (2000-1000)/(10000-5000)*2*100
    assert health[0]["memory_percent"] == 45.0  # (1000000-100000)/2000000*100


@patch("docker.from_env")
def test_get_docker_health_detailed(mock_docker):
    """Test fetching detailed Docker container health metrics."""
    mock_client = MagicMock()
    mock_container = MagicMock()
    mock_container.name = "test-container"
    mock_container.status = "running"
    mock_container.attrs = {"RestartCount": 2}
    mock_container.stats.return_value = {
        "cpu_stats": {
            "cpu_usage": {"total_usage": 2000},
            "system_cpu_usage": 10000,
            "online_cpus": 2
        },
        "precpu_stats": {
            "cpu_usage": {"total_usage": 1000},
            "system_cpu_usage": 5000
        },
        "memory_stats": {
            "usage": 1000000,
            "limit": 2000000,
            "stats": {"cache": 100000}
        },
        "networks": {"eth0": {"tx_bytes": 1000, "rx_bytes": 2000}}
    }
    mock_client.containers.list.return_value = [mock_container]
    mock_docker.return_value = mock_client

    health = get_docker_health(detailed=True)
    assert len(health) == 1
    assert health[0]["name"] == "test-container"
    assert health[0]["status"] == "running"
    assert health[0]["cpu_percent"] == 40.0
    assert health[0]["memory_percent"] == 45.0
    assert health[0]["network_bytes_sent"] == 1000
    assert health[0]["network_bytes_received"] == 2000
    assert health[0]["restart_count"] == 2


@patch("docker.from_env")
def test_get_docker_health_no_containers(mock_docker):
    """Test handling when no containers are running."""
    mock_client = MagicMock()
    mock_client.containers.list.return_value = []
    mock_docker.return_value = mock_client

    health = get_docker_health(detailed=True)
    assert health == []


@patch("docker.from_env")
def test_get_docker_health_error(mock_docker):
    """Test handling of Docker daemon errors."""
    mock_docker.side_effect = docker.errors.DockerException(
        "Docker not running")
    with pytest.raises(RuntimeError, match="Docker not running"):
        get_docker_health()
