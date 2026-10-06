import os
import platform
import socket
import time
from typing import Any, Dict, List
import psutil


class SystemCollector:
    def __init__(self, process_checks: List[str] = None, port_checks: List[int] = None):
        self.process_checks = process_checks or []
        self.port_checks = port_checks or []
        self.last_net_io = psutil.net_io_counters()
        self.last_net_time = time.time()

    def get_system_info(self) -> Dict[str, str]:
        return {
            "hostname": socket.gethostname(),
            "ip_address": self._get_primary_ip(),
            "os_info": f"{platform.system()} {platform.release()} ({platform.machine()})"
        }

    def _get_primary_ip(self) -> str:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    def collect_metrics(self) -> List[Dict[str, Any]]:
        metrics = []

        # CPU %
        cpu_pct = psutil.cpu_percent(interval=1)
        metrics.append({"name": "cpu_usage_percent", "value": round(float(cpu_pct), 2)})

        # Memory
        mem = psutil.virtual_memory()
        metrics.append({"name": "memory_usage_percent", "value": round(float(mem.percent), 2)})
        metrics.append({"name": "memory_used_mb", "value": round(float(mem.used / (1024 * 1024)), 2)})
        metrics.append({"name": "memory_total_mb", "value": round(float(mem.total / (1024 * 1024)), 2)})

        # Disk
        try:
            root_path = "C:\\" if os.name == "nt" else "/"
            disk = psutil.disk_usage(root_path)
            metrics.append({"name": "disk_usage_percent", "value": round(float(disk.percent), 2)})
            metrics.append({"name": "disk_used_gb", "value": round(float(disk.used / (1024**3)), 2)})
            metrics.append({"name": "disk_total_gb", "value": round(float(disk.total / (1024**3)), 2)})
        except Exception:
            pass

        # Network Rates
        now = time.time()
        curr_net = psutil.net_io_counters()
        dt = max(now - self.last_net_time, 1.0)
        sent_rate = (curr_net.bytes_sent - self.last_net_io.bytes_sent) / dt
        recv_rate = (curr_net.bytes_recv - self.last_net_io.bytes_recv) / dt
        self.last_net_io = curr_net
        self.last_net_time = now

        metrics.append({"name": "net_bytes_sent", "value": round(float(sent_rate), 2)})
        metrics.append({"name": "net_bytes_recv", "value": round(float(recv_rate), 2)})

        return metrics

    def collect_checks(self) -> List[Dict[str, Any]]:
        checks = []

        # Process Checks
        if self.process_checks:
            running_processes = {p.name().lower() for p in psutil.process_iter(['name'])}
            for proc in self.process_checks:
                is_running = proc.lower() in running_processes
                checks.append({
                    "check_name": f"process_{proc}",
                    "check_type": "process_running",
                    "status": "pass" if is_running else "fail",
                    "message": f"Process '{proc}' is {'running' if is_running else 'NOT running'}"
                })

        # Port Checks
        if self.port_checks:
            for port in self.port_checks:
                is_open = self._check_port_open(port)
                checks.append({
                    "check_name": f"port_{port}",
                    "check_type": "port_open",
                    "status": "pass" if is_open else "fail",
                    "message": f"Port {port} is {'open' if is_open else 'closed/unreachable'}"
                })

        return checks

    def _check_port_open(self, port: int) -> bool:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.0)
        try:
            res = s.connect_ex(("127.0.0.1", port))
            return res == 0
        except Exception:
            return False
        finally:
            s.close()
