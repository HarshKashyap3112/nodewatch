from enum import Enum


class MetricName(str, Enum):
    CPU_USAGE_PERCENT = "cpu_usage_percent"
    MEMORY_USAGE_PERCENT = "memory_usage_percent"
    MEMORY_USED_MB = "memory_used_mb"
    MEMORY_TOTAL_MB = "memory_total_mb"
    DISK_USAGE_PERCENT = "disk_usage_percent"
    DISK_USED_GB = "disk_used_gb"
    DISK_TOTAL_GB = "disk_total_gb"
    NET_BYTES_SENT = "net_bytes_sent"
    NET_BYTES_RECV = "net_bytes_recv"
