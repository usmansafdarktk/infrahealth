import pytest
import psutil
from unittest.mock import patch
from infrahealth.health import get_server_health


@patch("psutil.cpu_percent")
@patch("psutil.virtual_memory")
@patch("psutil.disk_usage")
def test_get_server_health_basic(mock_disk, mock_memory, mock_cpu):
    """Test fetching basic server health metrics."""
    mock_cpu.return_value = 10.0
    mock_memory.return_value.percent = 50.0
    mock_disk.return_value.percent = 75.0

    health = get_server_health(detailed=False)
    assert health == {"cpu_percent": 10.0,
                      "memory_percent": 50.0, "disk_percent": 75.0}


@patch("psutil.cpu_percent")
@patch("psutil.virtual_memory")
@patch("psutil.disk_usage")
@patch("psutil.net_io_counters")
@patch("psutil.boot_time")
@patch("psutil.pids")
@patch("psutil.getloadavg")
def test_get_server_health_detailed(mock_loadavg, mock_pids, mock_boot, mock_net, mock_disk, mock_memory, mock_cpu):
    """Test fetching detailed server health metrics."""
    mock_cpu.return_value = 10.0
    mock_memory.return_value.percent = 50.0
    mock_disk.return_value.percent = 75.0
    mock_net.return_value = type(
        "obj", (), {"bytes_sent": 1000, "bytes_recv": 2000})()
    mock_boot.return_value = 1000
    mock_pids.return_value = [1, 2, 3, 4]
    mock_loadavg.return_value = (0.5, 1.0, 1.5)

    with patch("platform.system", return_value="Linux"):
        with patch("time.time", return_value=4600):  # 3600s = 1 hour uptime
            health = get_server_health(detailed=True)
            assert health == {
                "cpu_percent": 10.0,
                "memory_percent": 50.0,
                "disk_percent": 75.0,
                "network_bytes_sent": 1000,
                "network_bytes_received": 2000,
                "uptime_seconds": 3600,
                "process_count": 4,
                "load_avg_1min": 0.5,
                "load_avg_5min": 1.0,
                "load_avg_15min": 1.5
            }


@patch("psutil.cpu_percent")
def test_get_server_health_permission_error(mock_cpu):
    """Test handling of permission errors."""
    mock_cpu.side_effect = PermissionError("Permission denied")
    with pytest.raises(RuntimeError, match="Permission denied. Try running with sudo."):
        get_server_health()
